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
'InputException', 'BaseInputWdg', 'TextWdg', 'FilterTextWdg', 'TextAreaWdg',
#'TextAreaWithSelectWdg',
'RadioWdg', 'CheckboxWdg', 'FilterCheckboxWdg', 'SelectWdg', 'FilterSelectWdg', 
'MultiSelectWdg', 'ItemsNavigatorWdg', 'ButtonWdg',
'SubmitWdg', 'ActionSelectWdg', 'DownloadWdg',
'ResetWdg', 'PasswordWdg', 'HiddenWdg', 'NoneWdg', 'ThumbInputWdg',
'SimpleUploadWdg', 'UploadWdg', 'MultiUploadWdg', 
'CalendarWdg', 'CalendarInputWdg',
"PopupWdg", "PopupMenuWdg", "ColorWdg"
]


import os, shutil, string, types, random

from pyasm.common import Common, Marshaller, Date, SPTDate, TacticException
from pyasm.biz import File, Snapshot, Pipeline, NamingUtil, ExpressionParser, PrefSetting
from pyasm.web import *
from pyasm.search import Search, SearchKey, SearchException

from .icon_wdg import IconButtonWdg, IconWdg

from operator import itemgetter

import six
basestring = six.string_types


class InputException(Exception):
    pass


 
class BaseInputWdg(HtmlElement):

    ARGS_KEYS = {}
    def get_args_keys(cls):
        '''external settings which populate the widget'''
        return cls.ARGS_KEYS
    get_args_keys = classmethod(get_args_keys)


    #def __init__(self, name=None, type=None, label=None):
    def __init__(self, name=None, type=None, label=None, **kwargs):
        #assert(type)
        super(BaseInputWdg,self).__init__(type)

        # the name of the input element
        self.name = name
        self.input_prefix = None
        self.value = ""
        self.options = {}
        self.options['default'] = ""
        self.options['persist'] = "false"
        if kwargs:
            self.options = kwargs
            self.kwargs = kwargs

        self.persistence = False
        self.persistence_obj = None
        self.cached_values = None
        self.label = label
        self.disabled_look = True
        self.prefix = ''
        self.change_cbjs_action = ''
        # deprecated
        self.element = None

        self.parent_wdg = None
        self.state = {}

        self.title = ''

        self.related_type = None


    # FIXME: need to make this more elegant: these are only put here
    # to conform to the interface of BaseTableElementWdg so that these
    # elements can be put into a TableWdg.  This should be more formal
    # because the relationship here is quite tenuous
    def get_style(self):
        return ""
    def get_bottom(self):
        return ""




    def copy(self, input):
        '''copies the parameters of one widget to the other. This is useful
        for transfering the parameters specified in a config file to a contained
        widget.'''
        self.name = input.name
        self.input_prefix = input.input_prefix
        self.options = input.options
        self.sobjects = input.sobjects
        self.current_index = input.current_index

        self.set_sobject = input.get_current_sobject()


    def set_state(self, state):
        '''Set the state for this table element'''
        self.state = state

    def get_state(self):
        '''get the state for this table element'''
        return self.state



    def get_related_type(self):
        '''Some input widgets will be related to a search type to define
        a list or range of parameters.  This will allow an external
        widget to discover this relationship and provide a means to add
        to this list'''
        return self.related_type




    def set_title(self, title):
        self.title = title
        
    def get_display_title(self):
        '''Function that that gives a title represenation of this widget'''
        if self.title:
            return self.title

        name = self.get_name()
        name = name.replace("_", " ")
        return name.title()
 


    def get_title(self):
        '''Function that that gives a title represenation of this widget'''
        if self.title:
            return self.title

        name = self.get_name()
        if not name:
            return ""

        title = Common.get_display_title(name)
        span = SpanWdg(title)
        return span


    def _add_required(self, span, offset_x=10):
        required_span = DivWdg("*")
        required_span.add_style("position: absolute")
        required_span.add_style("margin-left: -%dpx"% offset_x)

        required_span.add_color("color", "color", [50, 0, 0])
        required_span.add_style("font-size: 1.0em")
        
        span.add(required_span)
        span.add_class("spt_required")

    def set_parent_wdg(self, parent_wdg):
        '''method to set the parent widget.  This is typicaly the EditWdg'''
        self.parent_wdg = parent_wdg

    def get_parent_wdg(self):
        return self.parent_wdg


    def set_layout_wdg(self, layout_wdg):
        self.parent_wdg = layout_wdg

        
    def get_prefs(self):
        '''Function that that gives a preference widget for this input'''
        return ""


    def set_input_prefix(self, input_prefix):
        self.input_prefix = input_prefix

    def get_input_name(self, name=''):
        input_name = self.name
        if name:
            input_name = name
        if self.input_prefix:
            return "%s|%s" % (self.input_prefix, input_name)
        else:
            return input_name


    def set_name(self, name):
        '''set the name externally'''
        self.name = name

    
    def get_name(self):
        return self.name

    def get_label(self):
        if self.label:
            return self.label
        else:
            return self.name

    def set_options(self, options):
        self.options = options
		
        if self.has_option('search_key'):
            search_key = options.get('search_key')
            if search_key:
                sobj = SearchKey.get_by_search_key(search_key)
                self.set_sobjects([sobj])

    

    def has_option(self, key):
        return key in self.options
 
    def set_option(self, key, value):
        if isinstance(value, type( {}.keys() )):
            value = list(value)
        self.options[key] = value
        
    def get_option(self, key):
        '''gets the value of the specified option'''
        if key in self.options:
            return self.options[key]
        else:
            return ""

    def set_disabled_look(self, disable):
        self.disabled_look = disable

    def is_read_only(self):
        ''' if the read_only option is true, either set disabled or readonly'''
        if self.get_option('read_only') in ['true', True]:
            return True
        return False

    def is_edit_only(self):
        return self.get_option('edit_only') == 'true'

    def is_simple_viewable(self):
        return True

    def is_editable(self):
        return True

    def get_timezone_value(self, value):
        '''given a datetime value, try to convert to timezone specified in the widget.
           If not specified, use the My Preferences time zone'''
        timezone = self.get_option('timezone')
        if not timezone:
            timezone = PrefSetting.get_value_by_key('timezone')
        
        if timezone in ["local", '']:
            value = SPTDate.convert_to_local(value)
        else:
            value = SPTDate.convert_to_timezone(value, timezone)
        
        return value

    def check_persistent_values(self, cgi_values):
        web = WebContainer.get_web()
        if self.is_form_submitted() and web.has_form_key(self.get_input_name()):
            # if the form is submitted, then always use the submitted value
            self._set_persistent_values(cgi_values)
            self.cached_values = cgi_values
            return cgi_values
        else:
            return False

    def check_persistent_display(self, cgi_values):
        # no longer checking for web.get_form_keys()
        web = WebContainer.get_web()
        if self.get_option("persist") == "true":
            # old web implementation
            if web.has_form_key(self.get_input_name()):
                values = cgi_values
                #self._set_persistent_values(values)
                return values
            else:
                # try the json implementation if it has been set
                from tactic.ui.filter import FilterData 
                filter_data = FilterData.get()
                values = filter_data.get_values_by_prefix(self.prefix)
                if values:
                    values = values[0]
                    value = values.get(self.get_input_name())
                    if value:
                        cgi_values = [value]
                        #self._set_persistent_values(cgi_values)
                        return cgi_values
                return False
        else:
            return False

    def get_values(self, for_display=False):
        '''gets the current value of this input element.  The order of
        importance is as follows.  If the form was submitted, this value
        will always take precedence.  Then externally set values through
        code.'''
        values = []
       
        if self.get_option("value"):
            values = [self.get_option("value")]
            return values



        web = WebContainer.get_web()
        if self.has_option('search_key') and not self.get_current_sobject():
            sobject = SearchKey.get_by_search_key(self.options.get('search_key'))
            if sobject:
                self.set_sobjects([sobject])
        
        # getting the value from CGI depends on whether this is for display
        # of the widget or for getting the current value of this widget.
        cgi_values = web.get_form_values( self.get_input_name() )

        if for_display:

            # get it from the sobject: this grabs the values from the
            # sobject in the db for editing
            column = self.get_option('column')
            if not column:
                column = self.name

            current_sobject = self.get_current_sobject()
            if current_sobject and current_sobject.has_value(column):
                sobject = self.get_current_sobject()
                values = [sobject.get_value(column)]
                if not values:
                    values = []
                return values



            # if set explicitly, then this is the value
            if self.value != '':
                
                values = [self.value]
                self._set_persistent_values(values)
                return values


            # the value is taken from CGI only if the input is persistent
            values = self.check_persistent_display(cgi_values)
            if values != False:
                return values
            else:
                values = []
            
            # This option will read the webstate if no explicit value is
            # present
            if self.get_option("web_state") == "true":
                # this will eventually use the WebState: for now, use cgi
                values = cgi_values
                if values and values[0] != "":
                    self._set_persistent_values(values)
                    return values

        # if this has been called before, get the previous value
        elif self.cached_values != None:
            return self.cached_values
        
       
        # check for key existence only in for_display=False
        #elif self.is_form_submitted() and web.has_form_key(self.get_input_name()):
        #    # if the form is submitted, then always use the submitted value
        #    self._set_persistent_values(cgi_values)
        #    self.cached_values = cgi_values
        #    return cgi_values
        else: 
            temp_values = self.check_persistent_values(cgi_values)
            if temp_values != False:
                return temp_values  
        # if there are values in CGI, use these
        if not for_display and cgi_values:
            values = cgi_values
           
        
        # if the value has been explicitly set, then use that one
        elif self.value != '':
            values = [self.value]
          

        
        # otherwise, get it from the sobject: this grabs the values from the
        # sobject in the db for editing
        elif self.get_current_sobject() and \
                self.get_current_sobject().has_value(self.name):
            sobject = self.get_current_sobject()
            values = [sobject.get_value(self.name)]
            if not values:
                values = []


        # This option will read the webstate if no explicit value is
        # present
        elif self.get_option("web_state") == "true":
            # this will eventually use the WebState: for now, use cgi
            values = cgi_values
            self._set_persistent_values(values)
            self.cached_values = values
            return values




        # otherwise, get it from the persistence (database)
        elif self.persistence:
            class_path = Common.get_full_class_name(self.persistence_obj)
            key = "%s|%s" % (class_path, self.name)
            #values = WidgetSettings.get_key_values(key, auto_create=False)
            values = WidgetSettings.get_key_values(key)
        
        # if all of the above overrides fail, then set to the default
        # the rules for persistent input is slightly different
        if (values == None and self.persistence) or (values == [] and not self.persistence):
            default = self.get_option("default")
            if default != "":
                # default can be a list
                if isinstance(default, list):
                    values = default
                else:
                    values = [default]

                # evaluate an sobject expression
                new_values = []
                for value in values:
                    new_value = NamingUtil.eval_template(value)
                    new_values.append(new_value)
                values = new_values


            else:
                values = []
        
        if values:
            #web.set_form_value(self.name, values[0])
            web.set_form_value(self.get_input_name(), values)
            self._set_persistent_values(values)
      
        # only cache if it is not for display: otherwise we have to separate
        # the for display cache and the non for display cache
        if not for_display:
            self.cached_values = values

        return values


    def _set_persistent_values(self, values):

        if self.persistence:

            class_path = Common.get_full_class_name(self.persistence_obj)
            key = "%s|%s" % (class_path, self.name)

            # make sure the value is not empty
            if not values:
                values = []

            # if the current value is different from stored value, then update
            # this check is done in set_key_values()
            WidgetSettings.set_key_values(key, values)


    

    def get_value(self, for_display=False):
        values = self.get_values(for_display)
        if not values:
            return ""
        else:
            return values[0]



    def set_value(self, value, set_form_value=True):
        self.value = value

        # some widgets do not have names (occasionally)
        name = self.get_input_name()
        if not name:
            return


        # when the value is explicitly set, the set then form value as such
        if set_form_value:
            web = WebContainer.get_web()
            web.set_form_value(name, value)



    def set_persistence(self, object=None):
        self.persistence = True
        if object == None:
            object = self
        self.persistence_obj = object

        # this implies persist on submit (it is also faster)
        self.set_persist_on_submit()


    def set_persist_on_submit(self, prefix=''):
        self.set_option("persist", "true")
        self.prefix = prefix

    def set_submit_onchange(self, set=True):
        if set:
            self.change_cbjs_action = 'spt.panel.refresh( bvr.src_el.getParent(".spt_panel") );'
            #self.add_behavior(behavior)

        else:
            print("DEPRECATED: set_submit_onchange, arg set=False")
            self.remove_event('onchange')

    def is_form_submitted(self):
        web = WebContainer.get_web()
        if web.get_form_value("is_from_login") == "yes":
            return False

        # all ajax interactions are considered submitted as well
        if web.get_form_value("ajax"):
            return True

        return web.get_form_value("is_form_submitted") == "yes"

    def set_form_submitted(self, event='onchange'):
        '''TODO: deprecated this: to declare if a form is submitted, used primarily for FilterCheckboxWdg'''
        self.add_event(event, "document.form.elements['is_form_submitted'].value='yes'", idx=0)

    def set_style(self, style):
        '''Sets the style of the top widget contained in the input widget'''
        self.element.set_style(style)

    def get_key(self):
        if not self.persistence_obj:
            self.persistence_obj = self
        key = "%s|%s"%(Common.get_full_class_name(self.persistence_obj), self.name)
        return key

    def get_save_script(self):
        '''get the js script to save the value to widget settings for persistence'''
        key = self.get_key()
        return "spt.api.Utility.save_widget_setting('%s', bvr.src_el.value)" %key

    def get_refresh_script(self):
        '''get a general refresh script. use this as a template if you need to pass in 
           bvr.src_el.value to values'''
        return "var top=spt.get_parent_panel(bvr.src_el); spt.panel.refresh(top, {}, true)"


class BaseTextWdg(BaseInputWdg):
    def handle_mode(self):
        return



class TextWdg(BaseTextWdg):

    ARGS_KEYS = {
    'size': {
        'description': 'width of the text field in pixels',
        'type': 'TextWdg',
        'order': 0,
        'category': 'Options'

    },
    'read_only': {
        'description': 'whether to set this text field to read-only',
        'type': 'SelectWdg',
        'values' : 'true|false',
        'order': 1,
        'category': 'Options'
    },
    'required': {
            'description': 'designate this field to be filled in',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': 2,
            'category': 'Options'
    }


    
    }
 

    def __init__(self,name=None, label=None, **kwargs):
        super(TextWdg,self).__init__(name, "input", label=label, **kwargs)
        self.css = "inputfield"
        self.add_class("spt_input")
    
   

    def get_display(self):
        input_type = self.get_option("type")
        if not input_type:
            input_type = "text"

        self.set_attr("type", input_type)
        self.set_attr("name", self.get_input_name())


        if self.is_read_only():
            # do not set disabled attr to disabled cuz usually we want the data to
            # get read and passed to callbacks
            self.set_attr('readonly', 'readonly')
            if self.disabled_look == True:
                #self.add_class('disabled')
                self.add_color("background", "background", -10)
        value = self.get_value(for_display=True)
        # this make sure that the display
        if isinstance(value, basestring):
            value = value.replace('"', '&quot;')
        self.set_attr("value", value)

        size = self.get_option("size")
        if size:
            self.set_attr("size", size)

        self.handle_mode()
        required = self.get_option("required")
        if required == "true":
            text = BaseInputWdg.get_class_display(self)
            wdg = SpanWdg()

            self._add_required(wdg)
            wdg.add(text)
            return wdg

        else:    
            return super(TextWdg,self).get_display()



class FilterTextWdg(TextWdg):
    '''This composite text acts as a filter and can be, for instance, 
        used in prefs area in TableWdg'''
    def __init__(self,name=None, label=None, css=None , is_number=False, has_persistence=True):
        super(FilterTextWdg,self).__init__(name, label=label)
        if is_number:
            self.add_event('onchange',\
                "val=document.form.elements['%s'].value; if (Common.validate_int(val))\
                    document.form.submit(); else \
                    {alert('[' + val + '] is not a valid integer.')}" %name)  
                
        else:
            self.set_submit_onchange()

        if has_persistence:
            self.set_persistence()
        else:
            self.set_persist_on_submit()
        self.css = css
        self.unit = ''

    def set_unit(self, unit):
        self.unit = unit
        
    
    def get_display(self):
        self.handle_behavior()
        if not self.label:
            return super(FilterTextWdg, self).get_display()
        else:
            text = TextWdg.get_class_display(self)
            span = SpanWdg(self.label, css=self.css)
            span.add(text)
            span.add(self.unit)
            return span

    def handle_behavior(self):
        if self.persistence:
            key = self.get_key()
            value = WidgetSettings.get_value_by_key(key)
            if value:
                self.set_value(value)

            behavior = {"type" : "change",
                    "cbjs_preaction":\
                    "spt.api.Utility.save_widget_setting('%s',bvr.src_el.value)"%key}
            if self.change_cbjs_action:
                behavior['cbjs_action'] = self.change_cbjs_action
            self.add_behavior(behavior)

    

class TextAreaWdg(BaseTextWdg):

    ARGS_KEYS = {
        'rows': {
            'description': 'The number of rows to show',
            'type': 'TextWdg',
            'order': 1,
            'category': 'Options'
        },
        'cols':  {
            'description': 'The number of columns to show',
            'type': 'TextWdg',
            'order': 2,
            'category': 'Options'
        },
        'required': {
            'description': 'designate this field to be filled in',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': 3,
            'category': 'Options'
        }

    }

    def __init__(self,name=None, **kwargs):
        super(TextAreaWdg,self).__init__(name,"textarea", **kwargs)
        
        self.kwargs = kwargs
        # on OSX rows and cols flag are not respected
        width = kwargs.get("width")
        if width:
            self.add_style("width", width)
            try:
                width = int(width)
                width = str(width) + "px"
            except ValueError:
                pass
        height = kwargs.get("height")
        if height:
            try:
                height = int(height)
                height = str(height) + "px"
            except ValueError:
                pass
            self.add_style("height", height)
            

    
        web = WebContainer.get_web()
        browser = web.get_browser()
        if browser == "Qt":
            rows = None
            cols = None
        else:
            rows = kwargs.get("rows")
            cols = kwargs.get("cols")
            if rows:
                self.set_attr("rows", rows)
            if cols:
                self.set_attr("cols", cols)


        self.add_class("spt_input")


    def handle_styles(self):
        
        if False:
        #if not self._use_bootstrap():
            self.add_color("background", "background", 10)
            self.add_color("color", "color")
            web = WebContainer.get_web()
            
            browser = web.get_browser()
            if not width and not cols:
                width = "300px"
                self.add_style("width", width)
            
            self.add_border()


    def get_display(self):
        
        self.handle_styles()

        self.set_attr("name", self.get_input_name())

        
        rows = self.get_option("rows")
        cols = self.get_option("cols")
        if not rows:
            rows = 3
        self.set_attr("rows", rows)

        if not cols:
            cols = 50

        self.set_attr("cols", cols)

        if self.is_read_only():
            self.set_attr('readonly', 'readonly')
            if self.disabled_look == True:
                #self.add_class('disabled')
                self.add_color("background", "background", -10)
        
        # value always overrides
        value = self.kwargs.get("value")
        if not value:
            value = self.get_value(for_display=True)

        self.add(value)

        #self.handle_mode()
        if self.get_option("required") in [True, 'true']:
            text_area = BaseInputWdg.get_class_display(self)
            wdg = SpanWdg()
            self._add_required(wdg)
            wdg.add(text_area)
            return wdg

        self.add_class("form-control")

        return super(TextAreaWdg,self).get_display()



class RadioWdg(BaseInputWdg):
    def __init__(self,name=None, label=None):
        super(RadioWdg,self).__init__(name,"input")
        self.set_attr("type", "radio")
        self.label = label

    def set_checked(self):
        self.set_attr("checked", "1")


    def get_display(self):

        self.set_attr("name", self.get_input_name())
        self.add_class("spt_input")

        # This is a little confusing.  the option value is mapped to the
        # html attribute value, however, the value from get_value() is the
        # state of the element (on or off)
        values = self.get_values(for_display=True)

        # determine if this is checked
        if self.name != None and len(values) != 0 \
                and self.get_option("value") in values:
            self.set_checked()

        # convert all of the options to attributes
        for name, option in self.options.items():
            self.set_attr(name,option)

        if self.label:
            self.add_style("display: inline-flex")
            self.add_style("margin-right: 5px")

            span = DivWdg()
            span.add(" %s" % self.label)
            self.add(span)

        return super(RadioWdg,self).get_display()




class CheckboxWdg(BaseInputWdg):
    def __init__(self,name=None, label=None, css=None):
        super(CheckboxWdg,self).__init__(name,"input", label)
        self.set_attr("type", "checkbox")
        self.label = label
        self.css = css

        self.add_class("spt_input")

        self.add_style("display: inline-block")
        self.add_style("vertical-align: middle")
        self.add_style("margin: 0px")



    def set_default_checked(self):
        ''' this is used for checkbox that has no value set'''
        self.set_option("default", "on")

    def set_checked(self):
        self.set_option("checked", "1")

    def set_unchecked(self):
        self.set_option("checked", None)


    def is_checked(self, for_display=False):

        return self.get_option("checked") in ['1','on','true']

        # Checkbox needs special treatment when comes to getting values
        values = self.get_values(for_display=for_display)
        value_option = self._get_value_option()

        # FIXME if values is boolean, it will raise exception
        if value_option in values:
            return True
        else:
            return False
        #return self.get_value() == self._get_value_option()

    def _get_value_option(self):
        value_option = self.get_option("value")
        if value_option == "":
            value_option = 'on'
        return value_option

    def get_key(self):
        class_path = Common.get_full_class_name(self)
        key = "%s|%s" % (class_path, self.name)
        return key
   
    def check_persistent_values(self, cgi_values):
        web = WebContainer.get_web()
        if self.is_form_submitted():# and web.has_form_key(self.get_input_name):
            # if the form is submitted, then always use the submitted value
            if not self.persistence_obj:
                return False
            class_path = Common.get_full_class_name(self.persistence_obj)
            key = "%s|%s" % (class_path, self.name)
            setting = WidgetSettings.get_by_key(key, auto_create=False)
            if setting == None:
                return False
            if not self.is_ajax(check_name=False):
                self._set_persistent_values(cgi_values)
            self.cached_values = cgi_values
                
            return cgi_values
        else:
            return False

   

    def get_display(self):
        self.set_attr("name", self.get_input_name())

        # This is a little confusing.  the option value is mapped to the
        # html attribute value, however, the value from get_value() is the
        # state of the element (on or off) or the "value" option
        values = self.get_values(for_display=True)
        # for multiple checkboxes using the same name

        self.add_style("width", "16px", override=False)
        self.add_style("height", "16px", override=False)

        if self.is_read_only():
            self.set_attr('disabled', 'disabled')

        if self.value in ['1','on','true']:
            self.set_checked()

        """
        if len(values) == 1:
            # skip boolean
            value = values[0]
            if value and not isinstance(value, bool) and '||' in value:
                values = value.split('||')
        # determine if this is checked
        value_option = self._get_value_option()
        if values and len(values) != 0:
            if value_option in values:
                self.set_checked()
            elif True in values: # for boolean columns
                self.set_checked()
        """

        # convert all of the options to attributes
        for name, option in self.options.items():
            if option is None:
                continue
            self.set_attr(name,option)

        self.handle_behavior()

        if not self.label:
            return super(CheckboxWdg, self).get_display()
        else:
            cb = BaseInputWdg.get_class_display(self)
            span = DivWdg(cb, css=self.css)
            span.add_style("display: inline-block")

            label_div = DivWdg()
            span.add(label_div)
            label_div.add_style("display: inline-block")
            label_div.add_style("margin-left: 5px")
            label_div.add(self.label)
            return span

        return super(CheckboxWdg,self).get_display()

    def handle_behavior(self):
        if self.persistence:
            key = "%s|%s"%(Common.get_full_class_name(self.persistence_obj), self.name)
            value = WidgetSettings.get_value_by_key(key)
     
            if value:
                self.set_value(value)

            behavior = {"type" : "click_up",
                    'propagate_evt': True,
                    "cbjs_preaction":
                    "spt.input.save_selected(bvr, '%s','%s')"%(self.name, key)}
            self.add_behavior(behavior)

class FilterCheckboxWdg(CheckboxWdg):
    '''This composite checkbox acts as a filter and can be, for instance, 
        used in prefs area in TableWdg'''
    def __init__(self,name=None, label=None, css=None ):
        super(FilterCheckboxWdg,self).__init__(name, label=label, css=css)
        #self.set_submit_onchange()
        
        self.set_persistence()
       
    

    def get_display(self):
        # order matters here
        return super(FilterCheckboxWdg, self).get_display()
        

       
        

class SelectWdg(BaseInputWdg):
    SELECT_LABEL = "- Select -"
    ALL_MODE = "all"
    NONE_MODE = "NONE"
    MAX_DEFAULT_SIZE = 20

    # FIXME: this should not be here!!!
    # dict for default project settings that will be auto-created if encountered.
    # If not listed here, user will be prompted to add it himself
    DEFAULT_SETTING = {'bin_type': 'client|dailies', 'bin_label': 'anim|tech', \
            'shot_status': 'online|offline', 'note_dailies_context': 'dailies|review',\
            'timecard_item': 'meeting|training|research'}



    ARGS_KEYS = {
    'values': {
        'description': 'A list of values separated by | that determine the actual values of the selection',
        'order': 1,
        'category': 'Options'

    },
    'labels': {
        'description': 'A list of values separated by | that determine the label of the selection',

        'order': 2,
        'category': 'Options'
    },


    'values_expr': {
        'description': 'A list of values retrieved through an expression. e.g. @GET(prod/shot.code)',
        'type': 'TextAreaWdg',
        'order': 3,
        'category': 'Misc',
    },
    'labels_expr': {
        'description': 'A list of labels retrieved through an expression. e.g. @GET(prod/shot.name)',
        'type': 'TextAreaWdg',
        'order': 2,
        'category': 'Misc',
    },
    'mode_expr': {
        'description': 'Specify if it uses the current sObject as a starting point',
        'type': 'SelectWdg',
        'values': 'relative',
        'empty': 'true',
        'order': 3,
        'category': 'Misc',
    },
    'empty': {
        'description': 'The label for an empty selection',
        #'default': '-- Select --',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 4,
        'category': 'Options'
    },
    'default': {
        'description': 'The default selection value in an edit form. Can be a TEL variable.',
        'type': 'TextWdg',
        'category': 'Options',
        'order': 5,
    },
    'query': {
        'description': 'Query shorthand in the form of <search_type>|<value_column>|<label_column>"'
    },
    'required': {
        'description': 'designate this field to have some value',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 5,
        'category': 'Options'
    }

 
    }


    def __init__(self, name=None, **kwargs):
        self.kwargs = kwargs
        css = kwargs.get('css')
        label = kwargs.get('label')
        bs = kwargs.get('bs')

        if not name:
            name = "select%s" % Common.randint(0, 1000000)

        self.sobjects_for_options = None
        self.empty_option_flag = False
        self.empty_option_label, self.empty_option_value = (self.SELECT_LABEL, "")
        self.append_list = []
        self.values = []
        self.labels = []
        self.has_set_options = False
        self.css = css
        self.append_widget = None
        super(SelectWdg,self).__init__(name, type="select", **kwargs)
        
        # add the standard style class
        self.add_class("inputfield")
        self.add_class("spt_input")

        # BOOTSTRAP
        if bs != False:
            self.add_class("form-control")



    def get_related_type(self):
        # In order to get the related type, the dom options need to have
        # been processed
        if not self.has_set_options:
            self.set_dom_options(is_run=False)

        return self.related_type


    def add_empty_option(self, label='---', value= ''):
        '''convenience function to an option with no value'''
        self.empty_option_flag = True
        self.empty_option_label, self.empty_option_value = label, value

    def add_none_option(self):
        self.append_option("-- %s --" %SelectWdg.NONE_MODE,\
                SelectWdg.NONE_MODE)

    def remove_empty_option(self):
        self.empty_option_flag = False

    def append_option(self, label, value):
        self.append_list.append((label, value))

    def set_search_for_options(self, search, value_column=None, label_column=None):
        assert value_column != ""
        assert label_column != ""
        sobjects = search.do_search()
        self.set_sobjects_for_options(sobjects,value_column,label_column)


    def set_sobjects_for_options(self,sobjects,value_column=None,label_column=None):
        if value_column == None:
            self.value_column = self.name
        else:
            self.value_column = value_column

        if label_column == None:
            self.label_column = self.value_column
        else:
            self.label_column = label_column

        assert self.value_column
        assert self.label_column

        self.sobjects_for_options = sobjects


    def _get_setting(self):
        ''' this check setting and add warnings if it's empty'''
        values_option = [] 
        labels_option = []
        setting = self.get_option("setting")
        if setting:
            from pyasm.prod.biz import ProdSetting

            values_option = ProdSetting.get_seq_by_key(setting)
            
            if not values_option:
                data_dict = {'key': setting}
                prod_setting = ProdSetting.get_by_key(setting)
                search_id = -1
                setting_value = self.DEFAULT_SETTING.get(setting)
                if prod_setting:
                    if setting_value:
                        # use the default if available
                        prod_setting.set_value('value', setting_value)
                        prod_setting.commit()
                        values_option = ProdSetting.get_seq_by_key(setting)
                        labels_option = values_option
                    else:
                        # prompt the user to do it instead
                        self._set_append_widget(prod_setting.get_id(), data_dict)
                     
                
                # if it is a new insert
                else:
                    if setting_value:
                        data_dict['value'] = setting_value
                        type = 'sequence'
                        ProdSetting.create(setting, setting_value, type)
                        values_option = ProdSetting.get_seq_by_key(setting)
                        labels_option = values_option
                    else:
                       self._set_append_widget(search_id, data_dict)
                
            else:
                # check if it is map
                prod_setting = ProdSetting.get_by_key(setting)
                if prod_setting.get_value('type') =='map':
                    map_option = ProdSetting.get_map_by_key(setting)

                    labels_option = [ x[1] for x in map_option ]
                    values_option = [ x[0] for x in map_option ]
                else:
                    labels_option = values_option

        return values_option, labels_option
  

    def _set_append_widget(self, search_id, data_dict):
        from .web_wdg import ProdSettingLinkWdg
        prod_setting_link = ProdSettingLinkWdg(search_id)
        prod_setting_link.set_value_dict(data_dict) 

        # HACK: usually when there is an iframe, there is a widget value
        #if WebContainer.get_web().get_form_value('widget'):
        #    prod_setting_link.set_layout('plain')
        self.append_widget = prod_setting_link

    def set_dom_options(self, is_run=True):
        ''' set the dom options for the Select. It should only be called once
        or there will be some unexpected behaviour'''
        # get the values
        self.values = []
        labels_option = self.get_option("labels")
        values_option = self.get_option("values")
        
        # if there are no values, check if there is a project setting
        # which will provide both values_option and labels_option
        if not values_option:
            values_option, labels_option = self._get_setting()
        
        if isinstance(values_option, list):
            self.values.extend(values_option)
            
            
        elif self.values != "":
            self.values = self.get_option("values").split("|")
        else:
            self.values = ["None"]

        # get the labels for the select options
        
        self.labels = []
        if isinstance(labels_option, list):
            self.labels = labels_option[:]
        elif labels_option != "":
            #self.labels = string.split( labels_option, "|" )
            self.labels = labels_option.split("|")
            if len(self.values) != len(self.labels):
                raise InputException("values [%s] does not have the same number of elements as [%s]" % (str(self.values), str(self.labels)))

        else:
            self.labels = self.values[:]

        query = self.get_option("query")
        if query and query != "" and query.find("|") != -1:
            search_type, value, label = query.split("|")
            project_code = None
            search = None

            current_sobj = self.get_current_sobject()
            if current_sobj:
                project_code = current_sobj.get_project_code()
            try:
                search = Search(search_type, project_code=project_code)
            except SearchException as e:
                # skip if there is an unregistered sType or the table does not exist in the db
                if e.__str__().find('does not exist for database') != -1 or 'not registered' != -1:
                    self.values = ['ERROR in query option. Remove it in Edit Mode > Other Options']
                    self.labels =  self.values[:]
                    return
        

            query_filter = self.get_option("query_filter")
            if query_filter:
                search.add_where(query_filter)
            query_limit = self.get_option("query_limit")
            if query_limit:
                search.add_limit(int(query_limit))

            if '()' not in label:
                search.add_order_by(label)
            elif '()' not in value:
                search.add_order_by(value)

            if not value or not label:
                raise InputException("Query string for SelectWdg is malformed [%s]" % query)

            # store the related type
            self.related_type = search_type

            self.set_search_for_options(search,value,label)



        values_expr = self.get_option("values_expr")
        if not values_expr:
            values_expr = self.kwargs.get("values_expr")

        labels_expr = self.get_option("labels_expr")
        if not labels_expr:
            labels_expr = self.kwargs.get("labels_expr")

        mode_expr = self.get_option("mode_expr")
        if not mode_expr:
            mode_expr = self.kwargs.get("mode_expr")
        if values_expr:
            if mode_expr == 'relative':
                sobjects = self.sobjects
                if not sobjects:
                    parent_wdg = self.get_parent_wdg()
                    if parent_wdg:
                        # use the search_key as a starting point if applicable
                        sk = parent_wdg.kwargs.get('search_key')
                        if sk:
                            sobjects = [Search.get_by_search_key(sk)]
                    else:
                        sk = self.kwargs.get('search_key')
                        if sk:
                            sobjects = [Search.get_by_search_key(sk)]

            else:
                sobjects = []
            from pyasm.security import Sudo
            try:
                sudo = Sudo()
                parser = ExpressionParser()
                self.values = parser.eval(values_expr, sobjects=sobjects)
            except Exception as e:
                print("Expression error: ", str(e))
                self.values = ['Error in values expression']
                self.labels = self.values[:]
                # don't raise anything yet until things are properly drawn
				#raise InputException(e) 
            finally:
                sudo.exit()

            
            if labels_expr:
                try:
                    sudo = Sudo()
                    self.labels = parser.eval(labels_expr, sobjects=sobjects)
                    # expression may return it as a string when doing concatenation is done on a 1-item list
                    if isinstance(self.labels, basestring):
                        self.labels = [self.labels]
                except Exception as e:
                    print("Expression error: ", str(e))
                    self.labels = ['Error in labels expression']
                finally:
                    sudo.exit()
            else:
                self.labels = self.values[:]

            # create a tuple for sorting by label if it's a list
            if self.values:
                zipped = zip(self.values, self.labels)
                zipped = sorted(zipped, key=itemgetter(1))
                unzipped = list(zip(*zipped))
                self.values = list(unzipped[0])
                self.labels = list(unzipped[1])
           
        # if there is a search for options stored, then use these
        if self.sobjects_for_options != None:
            self.values = []
            self.labels = [] 
            for sobject in self.sobjects_for_options:
                # if there was a function call, use it
                if self.value_column.find("()") != -1:
                    self.values.append( eval("sobject.%s" % self.value_column ) )
                else:
                    self.values.append(sobject.get_value(self.value_column, no_exception=True))


                if self.label_column.find("()") != -1:
                    self.labels.append( eval("sobject.%s" % self.label_column ) )
                else:
                    self.labels.append(sobject.get_value(self.label_column, no_exception=True))

        # manually add extra values and labes
        extra_values = self.get_option("extra_values") 
        if extra_values:
            extra_values = extra_values.split("|")
            self.values.extend(extra_values)

            extra_labels = self.get_option("extra_labels") 
            if extra_labels:
                extra_labels = "|".split(extra_labels)
                self.labels.extend(extra_labels)
            else:
                self.labels.extend(extra_values)

        
        # add empty option
        is_empty = self.get_option("empty") not in ['','false'] or self.get_option("empty_label")
        if self.empty_option_flag or is_empty:
            self.values.insert(0, self.empty_option_value)
            # empty_label takes prescedence over empty (boolean)
            
            if self.get_option("empty_label"):
                self.labels.insert(0, self.get_option("empty_label"))
            else:
                self.labels.insert(0, self.empty_option_label)

        # append any custom ones
        if self.append_list:
            for label, value in self.append_list:
                self.values.append(value)
                self.labels.append(label)
                
        if is_run:
            self.has_set_options = True
                
    def get_select_values(self):
        if not self.has_set_options:
            self.set_dom_options()
        return self.labels, self.values


    def init(self):
        #self.add_color("background", "background", 10)
        #self.add_color("color", "color")
        pass



    def get_styles(self):

        bgcolor = self.get_color("background", 10)
        fgcolor = self.get_color("foreground")
        styles = HtmlElement.style('''
            select {
                background: %s;
                color: %s;
            }

        ''' % (bgcolor, fgcolor)
        )
        return styles



    def get_display(self):
        class_name = self.kwargs.get('class')
        if class_name:
            self.add_class(class_name)

        if self.is_read_only():
            # don't disable it, just have to look disabled
            self.set_attr('disabled', 'disabled')
            self.add_class('disabled')
        assert self.get_input_name() != None

        self.set_attr("name", self.get_input_name())

        width = self.get_option("width")
        if width:
            try:
                width = int(width)
                width = str(width) + "px"
            except ValueError:
                pass
            self.add_style("width: %s" % width)

        if not self._use_bootstrap():
            border_mode = self.get_option("border_mode") or "box"
            if border_mode == "box":
                self.add_border()
            elif border_mode == "custom":
                pass
            else:
                self.add_style("border", "none")


        #self.add_style("margin: 0px 5px")

        # default select element size to max of 20 ...
        sz = '20'

        # look for a site-wide configuration for SELECT element size ...
        from pyasm.common import Config
        select_element_size = Config.get_value('web_ui','select_element_size')
        if select_element_size:
            sz = select_element_size

        # see if the configuration of this widget specified a SELECT size (local config overrides site-wide) ...
        wdg_config_select_size = self.get_option("select_size")
        if wdg_config_select_size:
            sz = wdg_config_select_size

        # store configured size of SELECT to be used later on the client side to set the
        # SELECT drop down size ...
        self.set_attr('spt_select_size',sz)


        # assign all the labels and values
        if not self.has_set_options:
            self.set_dom_options()

        # get the current value for this element
        current_values = self.get_values(for_display=True)
        #if not current_value and self.has_option("default"):
            #current_value = self.get_option("default")
        # go through each value and set the select options
        selection_found = False
        for i in range(0, len(self.values)):
            if i >= len(self.labels): break
            value = self.values[i]
            label = self.labels[i]
            option = HtmlElement("option")

            # always compare string values.  Not sure if this is a good
            # idea, but it should work for most cases
            if self._is_selected(value, current_values):
                option.set_attr("selected", "selected")
                selection_found = True

            option.set_attr("value", value)
            option.add(label)

            self.add(option)

        # if no valid values are found, then show the current value in red
        show_missing = self.get_option("show_missing")
        if show_missing in ['false', False]:
            show_missing = False
        else:
            show_missing = True

        if show_missing and not selection_found: #and (self.empty_option_flag or self.get_option("empty") != ""):
            option = HtmlElement("option")
            value = self.get_value()
            # this converts potential int to string
            self.values = [Common.process_unicode_string(x) for x in self.values]
            if value and value not in self.values:
                option.add("%s" % value)
                option.set_attr("value", value)
                option.add_style("color", "red")
                option.set_attr("selected", "selected")
                self.add_style("color", "#f44")
                self.add(option)
            

        self.handle_behavior()
        

       
        if not self.label and not self.append_widget:
            if self.kwargs.get("required") in [True, 'true']:
                sel = BaseInputWdg.get_class_display(self)
                wdg = SpanWdg()
                self._add_required(wdg, offset_x=6)
                wdg.add(sel)
                return wdg
            else:
                return super(SelectWdg, self).get_display()
        else:
            sel = BaseInputWdg.get_class_display(self)
            span = SpanWdg(self.label, css=self.css)
            span.add(sel)
            span.add(self.append_widget)
            return span
            


    def _is_selected(self, value, current_values):
        if current_values:

            if not isinstance(value, basestring):
                value = str(value)

            cur_value = current_values[0]
            if not isinstance(cur_value, basestring):
                cur_value = str(cur_value)
            return value == cur_value
        else:
            return False


    def handle_behavior(self):
        # if this interferes with something else, please leave a comment so it can be fixed.. Similar logic is found in FilterCheckboxWdg and FilterTextWdg

        if self.persistence:
            key = self.get_key()
            value = WidgetSettings.get_value_by_key(key)
            if value:
                self.set_value(value)

            behavior = {"type" : "change",
                    "cbjs_preaction":\
                    "spt.api.Utility.save_widget_setting('%s',bvr.src_el.value)"%key}
            if self.change_cbjs_action:
                behavior['cbjs_action'] = self.change_cbjs_action
            self.add_behavior(behavior)


        sobjects = self.sobjects
        if sobjects:
            sobject = sobjects[0]
            search_key = sobject.get_search_key()
        else:
            search_key = None

        onchange = self.get_option("onchange")
        if onchange:
            self.add_behavior( {
                'type': 'change',
                'search_key': search_key,
                'cbjs_action': onchange
            } )
 



class FilterSelectWdg(SelectWdg):
    def __init__(self, name=None, label='', css=None):
        super(FilterSelectWdg,self).__init__(name, label=label, css=css)
        
        self.set_submit_onchange()
        self.set_persistence()
       
    def get_display(self):
        return super(FilterSelectWdg, self).get_display()
      
class ActionSelectWdg(SelectWdg):
    def __init__(self,name=None):
        super(ActionSelectWdg,self).__init__(name)
        self.add_class("action")
       


class MultiSelectWdg(SelectWdg):
    def __init__(self,name=None, label='', css=None):
        super(MultiSelectWdg,self).__init__(name, label=label, css=css)
        self.set_attr("multiple", "1")
        self.set_attr("size", "6")

    def _is_selected(self, value, current_values):
        if not current_values:
            return False
        # if there is only one value, then try and make the assumption that
        # this may be a single string array
        if len(current_values) == 1:
            current_value = current_values[0]
            if current_value and current_value.startswith("||") and current_value.endswith("||"):
                current_value = current_value.strip("||")
                current_values = current_value.split("||")


        return value in current_values




class ItemsNavigatorWdg(HtmlElement):
    ''' a navigator that breaks down a long list of items into chunks 
        selected by a drop-down menu '''
    DETAIL = "detail_style"
    LESS_DETAIL = "less_detail_style"

    def __init__(self, label, max_length, step, refresh=True, max_items=100):
        assert isinstance(max_length, int) and step > 0
        if max_length < 0:
            max_length = 0
        self.max_length = max_length
        self.step = step
        self.label = label
        self.show_label = True
        self.style = self.DETAIL
        self.refresh = refresh
        self.refresh_script = ''
        self.select = SelectWdg(self.label)
        self.select.add_color("background-color", "background", -8)
        self.select.add_style("font-size: 0.9em")
        self.select.add_style("margin-top: 3px")
        self.select.set_persist_on_submit()
        self.max_items = max_items
        super(ItemsNavigatorWdg, self).__init__('span')

    def set_style(self, style):
        self.style = style
    
    def set_refresh_script(self, script):
        self.refresh_script = script

    def get_display(self):
        if not self.refresh:
            self.select.add_event('onchange', self.refresh_script)

        list_num = int(self.max_length / self.step)
        value_list = []
        label_list = []

        # set limit
        if list_num > self.max_items:
            past_max = list_num - self.max_items
            list_num = self.max_items 
        else:
            past_max = 0
       
        for x in range(list_num):
            value_list.append("%s - %s" %(x* self.step + 1, (x+1) * self.step))

        # handle the last item
        if not past_max:
            if list_num  * self.step + 1 <= self.max_length:
                value_list.append("%s - %s" %(list_num * self.step + 1,\
                    self.max_length ))
        else:
            value_list.append( "+ %s more" % past_max)


        if self.style == self.DETAIL:
            label_list = value_list
        else:
            for x in xrange(list_num):
                label_list.append("Page %s" %(x+1) )
            if list_num  * self.step + 1 <= self.max_length:
                label_list.append("Page %s" % (list_num+1))
           
        self.select.add_empty_option(self.select.SELECT_LABEL, '')
        self.select.set_option("values", value_list)
        self.select.set_option("labels", label_list)
        if self.max_length < self.step:
            self.step = self.max_length
        self.select.set_option("default", "%s - %s" %(1, self.step))

        if self.show_label:
            self.add("%s:" %self.label)

        self.add(self.select)
        return super(ItemsNavigatorWdg, self).get_display() 
   
    def set_display_label(self, visible=True):
        self.show_label = visible
        
    def set_value(self, value):
        self.select.set_value(value)

    def get_value(self):
        return self.select.get_value()



class ButtonWdg(BaseInputWdg):
    def __init__(self,name=None):
        super(ButtonWdg,self).__init__(name,"input")
        #self.add_style("background-color: #f0f0f0")

    def get_display(self):
        self.set_attr("type", "button")
        self.set_attr("name", self.get_input_name())

        value = self.name
        self.set_attr("value",value)
        return super(ButtonWdg,self).get_display()


class SubmitWdg(BaseInputWdg):
    def __init__(self,name=None,value=None):
        super(SubmitWdg,self).__init__(name, "input")
        self.add_style("background-color: #f0f0f0")
        self.value = value

    def get_display(self):
        self.set_attr("type", "submit")
        self.set_attr("name", self.get_input_name())

        if self.value == None:
            self.value = self.name

        self.set_attr("value",self.value)
        return super(SubmitWdg,self).get_display()


class ResetWdg(BaseInputWdg):
    def __init__(self,name=None):
        super(ResetWdg,self).__init__(name, "input")

    def get_display(self):
        self.set_attr("type", "reset")
        self.set_attr("name", self.get_input_name())

        return super(ResetWdg,self).get_display()



class PasswordWdg(BaseInputWdg):
    def __init__(self,name=None):
        super(PasswordWdg,self).__init__(name,"input")
        self.css = "inputfield"
        self.add_class(self.css)
        self.add_class("spt_input")
        self.add_color("background", "background", 10)
        self.add_color("color", "color")
        self.add_style("border: solid 1px %s" % self.get_color("border_color") )
        #self.add_style("width: 200px") 

    def get_display(self):
        self.set_attr("type", "password")
        self.set_attr("name", self.get_input_name())

        self.add_class(self.css)
        return super(PasswordWdg,self).get_display()





class HiddenWdg(BaseInputWdg):
    def __init__(self,name=None, value=''):
        super(HiddenWdg,self).__init__(name,"input")
        self.value = value

    def get_title(self):
        return None

    def get_display(self):
        if self.options.get("value"):
            self.value = self.options.get("value")

        self.set_attr("type", "hidden")
        self.set_attr("name", self.get_input_name())

        value = self.get_value(for_display=True)
        if isinstance(value, basestring):
            value = value.replace('"', '&quot;')
        self.set_attr("value", value)

        self.add_class("spt_input")

        return super(HiddenWdg,self).get_display()


class NoneWdg(BaseInputWdg):
    '''An empty widget'''
    def __init__(self,name=None):
        super(NoneWdg,self).__init__(name)

    def get_title(self):
        if self.is_read_only():
            
            return super(NoneWdg, self).get_title()
        else:
            return ''

    def get_display(self):
        if self.is_read_only():
            self.set_attr('readonly', 'readonly')
            self.add(self.get_value())
            return super(NoneWdg, self).get_display() 
        else:
            return ''


class ThumbInputWdg(BaseInputWdg):
    '''Wrapper around the thumb widget, so that it can be display in the
    input form'''
    def __init__(self,name=None):
        super(ThumbInputWdg,self).__init__(name, "preview")

    def get_title(self):
        return '&nbsp;'

    def get_display(self):

        sobject = self.get_current_sobject()
        if sobject.is_insert():
            icon_path = IconWdg.get_icon_path("NO_IMAGE")
            img= "<img src="+icon_path+"></img>"
           
            return img

        if sobject.has_value("files"):
            column = "files"
        elif sobject.has_value("images"):
            column = "images"
        elif sobject.has_value("snapshot"):
            column = "snapshot"
        else:
            column = "snapshot"
            #return 'No icon'

        from .file_wdg import ThumbWdg
        icon = ThumbWdg()
        icon.set_name(column)
        icon.set_show_orig_icon(True)
        icon.set_show_filename(True)
        if self.get_option('latest_icon') == 'true':
            icon.set_show_latest_icon(True)
        icon.set_sobject( self.get_current_sobject() )
        return icon.get_display()



    


class SimpleUploadWdg(BaseInputWdg):
    def __init__(self,name=None):
        super(SimpleUploadWdg,self).__init__(name)

    def get_display(self):
       
        input = HtmlElement.input()
        input.set_attr("type","file")
        input.set_attr("name",self.get_input_name())
        input.add_class("inputfield")
        self.add(input)


        context = self.get_option("context")
        if context == "":
            context = Snapshot.get_default_context()
        context_input = HiddenWdg("%s|context" % self.get_input_name(), context)
        self.add(context_input)


        # override the column
        column = self.get_option("column")
        if column != "":
            column_input = HiddenWdg("%s|column" % self.get_input_name(), column)
            self.add(column_input)

        # create an event that will trigger a copy to handoff
        """
        web = WebContainer.get_web()
        handoff_dir = web.get_client_handoff_dir()
        path_hidden = HiddenWdg("%s|path" % self.get_input_name(), "")
        self.add(path_hidden)
        script = HtmlElement.script('''
        function foo() {
            var handoff_dir = '%s'
            var el = document.form.elements['%s']
            var path = el.value
            if (path == "") {
                return false
            }

            var parts = path.split(/\\\\|\//)
            var filename = parts[parts.length-1]
            var to_path = handoff_dir + "/" + filename
            alert(to_path)

            var hidden = document.form.elements['%s|path']
            hidden.value = path
            el.value = null
            // copy the file
            Applet.copy_file(path, to_path)
            //alert('move: ' + to_path)
            //Applet.move_file(path, to_path)
        }
        ''' % (handoff_dir, self.get_input_name(), self.get_input_name() ) )
        self.add(script)
        from pyasm.widget import GeneralAppletWdg
        self.add(GeneralAppletWdg())

        event_container = WebContainer.get_event_container()
        event_container.add_listener('sthpw:submit', 'foo()')
        """


        return super(SimpleUploadWdg,self).get_display()





class UploadWdg(BaseInputWdg):
    def __init__(self,name=None):
        super(UploadWdg,self).__init__(name)

    def add_upload(self, table, name, is_required=False):
        span = SpanWdg()
        if is_required:
            self._add_required(span)
        
        table.add_row()
        span.add("File (%s)" %name)
        table.add_cell(span)
        input = HtmlElement.input()
        input.set_attr("type","file")
        input.set_attr("name", self.get_input_name(name))
        input.set_attr("size", "40")
        
        table.add_cell(input)
    

    def get_display(self):

        icon_id = 'upload_div'
        div = DivWdg()

        if self.get_option('upload_type') == 'arbitrary':
            counter = HiddenWdg('upload_counter','0')
            div.add(counter)
            icon = IconButtonWdg('add upload', icon=IconWdg.ADD)
            icon.set_id(icon_id)
            icon.add_event('onclick', "Common.add_upload_input('%s','%s','upload_counter')" \
                %(icon_id, self.get_input_name()))
            div.add(icon)
        
        table = Table()
        table.set_class("minimal")
        table.add_style("font-size: 0.8em")

        names = self.get_option('names')
        required = self.get_option('required')
        if not names:
            self.add_upload(table, self.name)
        else:
            names = names.split('|')
            if required:
                required = required.split('|')
                if len(required) != len(names):
                    raise TacticException('required needs to match the number of names if defined in the config file.')
            # check for uniqueness in upload_names
            if len(set(names)) != len(names):
                raise TacticException('[names] in the config file must be unique')
            

            for idx, name in enumerate(names):
                 if required:
                     is_required = required[idx] == 'true'
                 else:
                     is_required = False
                 self.add_upload(table, name, is_required)

        table.add_row()
        

        context_option = self.get_option('context')
        pipeline_option = self.get_option('pipeline')
        setting_option = self.get_option('setting')
        context_name = "%s|context" % self.get_input_name()
        text = None 
        span1 = SpanWdg("Context", id='context_mode')
        span2 = SpanWdg("Context<br/>/Subcontext", id='subcontext_mode')
        span2.add_style('display','none')
        table.add_cell(span1)
        table.add_data(span2)
        if context_option or setting_option:
            # add swap display for subcontext only if there is setting or context option
            from web_wdg import SwapDisplayWdg
            swap = SwapDisplayWdg()
            table.add_data(SpanWdg(swap, css='small'))
            swap.set_display_widgets(StringWdg('[+]'), StringWdg('[-]'))
            subcontext_name = "%s|subcontext" % self.get_input_name()
            subcontext = SpanWdg('/ ', css='small')
            subcontext.add(TextWdg(subcontext_name))
            subcontext.add_style('display','none')
            subcontext.set_id(subcontext_name)
            on_script = "set_display_on('%s');swap_display('subcontext_mode','context_mode')"%subcontext_name
            off_script = "set_display_off('%s');get_elements('%s').set_value(''); "\
                "swap_display('context_mode','subcontext_mode')"%(subcontext_name, subcontext_name)
            swap.add_action_script(on_script, off_script)
            text = SelectWdg(context_name)
            if context_option:
                text.set_option('values', context_option)
            elif setting_option:
                text.set_option('setting', setting_option)
                    
            td = table.add_cell(text)
            
            table.add_data(subcontext)
            
        elif pipeline_option:
            sobject = self.sobjects[0]
            pipeline = Pipeline.get_by_sobject(sobject)
            context_names = []
            process_names = pipeline.get_process_names(recurse=True)
            for process in process_names:
                context_names.append(pipeline.get_output_contexts(process))
            text = SelectWdg(context_name)
            text.set_option('values', process_names)
            table.add_cell(text)
            
        else:
            text = TextWdg(context_name)
            table.add_cell(text)
            from web_wdg import HintWdg
            hint = HintWdg('If not specified, the default is [publish]')
            table.add_data(hint)
      
        revision_cb = CheckboxWdg('%s|is_revision' %self.get_input_name(),\
            label='is revision', css='med')
        table.add_data(revision_cb)
        table.add_row()
        table.add_cell("Comment")
        textarea = TextAreaWdg("%s|description"% self.get_input_name())
        table.add_cell(textarea)
        div.add(table)

        return div



class MultiUploadWdg(BaseInputWdg):
    UPLOAD_ID = "upload"
    
    def __init__(self,name=None):
        super(MultiUploadWdg,self).__init__(name)


    def get_display(self):

        # put in a default name
        if self.name == None:
            self.name = "upload_files"
       
        widget = Widget()

        # javascript function that polls the java applet for the files
        # that were uploaded
       
        widget.add(HtmlElement.script('''
            function do_upload()
            {
                upload = document.getElementById("%s")
                upload.do_upload()
                files = upload.get_uploaded_files()
                input = document.getElementById("%s")
                input.value = files
                return true
            }
            
            ''' % (self.UPLOAD_ID,self.name) ))
       
        # bind this to the edit button
        event = WebContainer.get_event("sthpw:submit")
        event.add_listener("do_upload()")

        context_url = WebContainer.get_web().get_context_url()
        
        # add the applet
        
        applet = HtmlElement("applet")
        applet.set_attr("code", "upload.UploadApplet")
        applet.set_attr("codebase", "%s/java" % context_url.get_url() )
        applet.set_attr("archive", "Upload-latest.jar")
        applet.set_attr("width", "450px")
        applet.set_attr("height", "120px")
        applet.set_attr("id", self.UPLOAD_ID)
        
        # create param for applet
        param = HtmlElement("param")
        param.set_attr("name","scriptable")
        param.set_attr("value","true")

        applet.add(param)
        widget.add(applet)
       

        # hidden element which fills in the file names that were
        # uploaded
        hidden = HiddenWdg(self.name)
        hidden.set_attr('id', self.name)
        widget.add(hidden)

        return widget




class DownloadWdg(BaseInputWdg):

    def __init__(self,name=None):
        super(DownloadWdg,self).__init__(name)

    def get_display(self):

        context_url = WebContainer.get_web().get_context_url()

        download_id = "download"

        # create applet
        applet = HtmlElement("applet")
        applet.set_attr("code", "upload.DownloadApplet")
        applet.set_attr("codebase", "%s/java" % context_url.get_url() )
        applet.set_attr("archive", "Upload-latest.jar")
        applet.set_attr("width", "1px")
        applet.set_attr("height", "1px")
        applet.set_attr("id", download_id)
    
        # create param for applet
        param = HtmlElement("param")
        param.set_attr("name","scriptable")
        param.set_attr("value","true")

        applet.add(param)
        self.add(applet)

        self.do_download()

        return super(DownloadWdg,self).get_display()


    def do_download(self):

        # get all of the files to download
        web = WebContainer.get_web()
        download_files = web.get_form_values("download_files")

        for download_file in download_files:

            search_type, search_id = download_file.split("|")

            search = Search(search_type)
            search.add_id_filter(search_id)
            sobject = search.get_sobject()


            # TODO: this code is highly flash dependent
            if sobject.has_value("episode_code"):
                sub_dir = sobject.get_value("episode_code")
            else:
                sub_dir = ""


            self._download_sobject(sobject,sub_dir)

            # for each shot download all of the dependent files
            if search_type.startswith("flash/shot"):
                instances = sobject.get_all_instances()
                for instance in instances:
                    from pyasm.flash import FlashAsset
                    asset = FlashAsset.get_by_code(instance.get_value("asset_code"))

                    asset_sub_dir = "%s/design" % sub_dir

                    self._download_sobject(asset, asset_sub_dir)


    def _download_sobject(self, sobject, sub_dir):

        web = WebContainer.get_web()
        to_dir = web.get_local_dir()

        snapshot = Snapshot.get_latest_by_sobject(sobject)
        if not snapshot:
            return

        web_paths = snapshot.get_all_web_paths()
        for web_path in web_paths:
            basename = os.path.basename(web_path)

            to_path = "%s/download/%s/%s" \
                % (to_dir, sub_dir, File.remove_file_code(basename))

            script = HtmlElement.script("download.do_download('%s','%s')"%\
                (web_path,to_path))

            self.add(script)


# DEPRECATED
class CalendarWdg(BaseInputWdg):
    ''' this can be instantiated multiple times in a page'''
    def __init__(self,name=None,id=None):

        self.id = id
        self.cal_options = {}
        self.on_wdg = None
        self.trigger = self.generate_unique_id("f_trigger_c")

        super(CalendarWdg,self).__init__(name,"div")

    def set_cal_option(self, name, value):
        self.cal_options[name] = value

    def set_on_wdg(self, widget):
        self.on_wdg = widget
        self.on_wdg.set_id(self.trigger)
        self.on_wdg.add_class("hand")
        
        

    def class_init(self):
        
        if WebContainer.get_web().is_IE():
            self.add( '''
            <!-- main calendar program -->
            <script src="/context/javascript/jscalendar/calendar.js"></script>

            <!-- language for the calendar -->
            <script src="/context/javascript/jscalendar/lang/calendar-en.js"></script>

            <!-- the following script defines the Calendar.setup helper
function, which makes adding a calendar a matter of 1 or 2
lines of code. -->
            <script src="/context/javascript/jscalendar/calendar-setup.js"></script>
            ''' )
            return

        self.add("<!-- main script for calendar -->")
        self.add("<!-- language for the calendar -->")
        self.add("<!-- the following script defines the Calendar.setup helper function -->")
        script = []
        script.append("var js=new Script()")
        script.append("js.include_once('/context/javascript/jscalendar/calendar.js')")
        script.append("js.include_once('/context/javascript/jscalendar/lang/calendar-en.js')")
        script.append("js.include_once('/context/javascript/jscalendar/calendar-setup.js')")
        init_script = HtmlElement.script(";".join(script))
        init_script.set_attr('mode','dynamic')
        self.add(init_script)


    def get_id(self):
        return self.id

    def get_display(self):
        value = self.get_value(for_display=True)

        if value == "":
            display_date = ""
            #hidden_value = "__NONE__"
            hidden_value = ""
        else:
            date = Date( value )
            display_date = date.get_display_date()
            hidden_value = value

        input_field = None
        if self.id:
            input_field = self.id
        else:
            input_field = self.get_input_name()
        hidden = HiddenWdg(input_field, hidden_value)
        hidden.set_id(input_field)
        self.add(hidden)


        display_area = "%s|display_area" % input_field
        text = SpanWdg()

        text.add( display_date )
        text.add_style("padding: 3px")
        text.set_id(display_area)
        self.add(text)


        #shows_time = "true"
        shows_time = "false"
        da_format = "%b %e, %Y"
        if_format = "%Y-%m-%e %H:%M"

        cal_options_str = ", ".join( [ "%s\t: %s" % (x,self.cal_options[x]) for x in self.cal_options.keys() ] )
        if cal_options_str != "":
            comma = ","
        else:
            comma = ""

        # set a default widget if it hasn't been defined
        if not self.on_wdg:
            img = HtmlElement.img("/context/javascript/jscalendar/img.gif")
            self.set_on_wdg(img)
            self.add(self.on_wdg)



        script = HtmlElement.script('''Calendar.setup({
        %s%s
        inputField      : '%s', /* id of the input field */
        displayArea     : '%s',
        ifFormat        : '%s', /* format of the input field */
        daFormat        : '%s', /* format of the display field */
        button          : '%s', /* trigger for the calendar (button ID) */
        align           : 'Br', /* alignment (defaults to 'Bl') */
        singleClick     : true,
        showsTime       : %s
        })'''% (cal_options_str, comma, input_field, display_area, if_format, da_format, self.trigger, shows_time))
        script.set_attr('mode', 'dynamic')
        self.add(script)

        return super(CalendarWdg,self).get_display()

  
class CalendarInputWdg(BaseInputWdg):
    ''' this one is the newer version with or without a TextWdg''' 
    def __init__(self, name=None, label=None, css=None, show_week=False):
        self.show_on_wdg = True
        self.show_value = True
        #self.cal_name = self.generate_unique_id()
        self.show_warning = True
        self.onchange_script = ''
        self.hidden = HiddenWdg(name)
        self.show_week = show_week
        self.css = css 
        super(CalendarInputWdg,self).__init__(name, "span", label=label)

    def class_init(self):
        if WebContainer.get_web().is_IE():
            self.add('''
<!-- main calendar program -->
<script type="text/javascript" src="/context/javascript/jscalendar/calendar.js"></script>

<!-- language for the calendar -->
<script type="text/javascript" src="/context/javascript/jscalendar/lang/calendar-en.js"></script>

<script type="text/javascript" src="/context/javascript/TacticCalendar.js"></script>

            ''')
            show_week = "false"
            if self.show_week :#or self.get_option('show_week') == 'true':
                show_week = "true"
            script = HtmlElement.script('''
                var calendar_tactic = new TacticCalendar(%s)
                ''' % (show_week) )
            self.add(script)
            return

        self.add('''
<!-- main calendar program -->
<script type="text/javascript" src="/context/javascript/jscalendar/calendar.js"></script>

<!-- language for the calendar -->
<script type="text/javascript" src="/context/javascript/jscalendar/lang/calendar-en.js"></script>

<!-- the following script defines the Calendar.setup helper
function, which makes adding a calendar a matter of 1 or 2
lines of code. -->
<script type="text/javascript" src="/context/javascript/jscalendar/calendar-setup.js"></script>

<script type="text/javascript" src="/context/javascript/TacticCalendar.js"></script>
            ''')
        show_week = "false"
        if self.show_week :#or self.get_option('show_week') == 'true':
            show_week = "true"
        script = HtmlElement.script('''
            var calendar_tactic = new TacticCalendar(%s)
            ''' % (show_week) )
        self.add(script)


    
    def get_hidden_wdg(self):
        if self.get_option('show_warning') =='false':
            self.show_warning = False
        value = super(CalendarInputWdg, self).get_value(for_display=True)
         
        if value == "":
            display_date = ""
            hidden_value = ""
        else:
            # In some cases the user is allowed to append chars after it
            date = Date( db_date=value, show_warning=self.show_warning )
            # display date format is not used for now
            # but date is instantiated to issue warning where applicable
            # display_date = date.get_display_date()
            hidden_value = value

        hidden_name = self.get_input_name()
        if self.show_value:
            hidden = TextWdg(hidden_name)
            hidden.set_persist_on_submit()
            hidden.set_attr("size", "15")
            hidden.set_value(hidden_value)
        else:
            hidden = HiddenWdg(hidden_name, hidden_value)

        
        return hidden


    def set_onchange_script(self, script):
        ''' script that runs when the user clicks on a date '''
        self.onchange_script = script

    '''
    def get_value(self):
        return self.hidden.get_value()
    

    def get_js_name(self):
        name = self.cal_name
        return "calendar_%s" % name
    '''

    def get_on_script(self, date=None):
        if not date:
            date = ''
        name = self.get_input_name() 
        script = "calendar_tactic.show_calendar('%s', null,'%s')" % (name, date)
        return script


    def set_show_on_wdg(self, flag):
        self.show_on_wdg = flag

    def set_show_value(self, flag):
        self.show_value = flag

    def set_show_warning(self, show):
        self.show_warning = show

    def get_on_wdg(self):
        widget = HtmlElement.img("/context/javascript/jscalendar/img.gif")
        widget.add_event("onclick", self.get_on_script() )
        widget.add_class("hand")
        return widget

        

    def get_display(self):
        widget = Widget()

        name = self.get_input_name()
        # set a default widget if it hasn't been defined
        if self.show_on_wdg:
            widget.add(self.get_on_wdg() )

        self.hidden = self.get_hidden_wdg() 
        widget.add(self.hidden)

        show_week = "false"
        if self.show_week or self.get_option('show_week') == 'true':
            show_week = "true"
       
        
        # on choosing a date, it executes this js
        if self.onchange_script:
            script = "calendar_tactic.init('%s');\
                calendar_tactic.cal.onClose = function() { if (!calendar_tactic.check('%s')) return; %s }"\
                %(name, name, self.onchange_script)
            from pyasm.web import AppServer
            AppServer.add_onload_script(script)
        self.add(widget)

        if not self.label:
            return super(CalendarInputWdg, self).get_display()
        else:
            sel = BaseInputWdg.get_class_display(self)
            span = SpanWdg(self.label, css=self.css)
            span.add(sel)
            return span




class PopupWdg(BaseInputWdg):

    def __init__(self, name=None, type=None, label=None):
        super(PopupWdg,self).__init__(name,type,label)
        self.title = ''
        self.offset_x = 10
        self.offset_y = 0
        self.is_auto_hide = True

    def set_auto_hide(self, hide):
        self.is_auto_hide = hide

    def get_display(self):

        div = DivWdg(css="popup_wdg")
        div.set_id(self.name)
        hidden_name = '%s_hidden' % self.name
        div.add(HiddenWdg(hidden_name))
        div.add_style("display: none")
        div.add_style("margin", "15px 0px 0px 0px")
        div.add_style("position", "absolute")

        from .web_wdg import CloseWdg
        div.add(CloseWdg(self.get_off_script()))
        div.add( HtmlElement.br(clear="all") )

        for widget in self.widgets:
            div.add(widget)

        div.add( HtmlElement.br(clear="all") )
        return div


  


    def get_on_script(self):
        script = "Common.follow_click(event, '%s', %d, %d); Effects.fade_in('%s', 200);"\
            %(self.get_name(),self.offset_x, self.offset_y, self.get_name()) 
        if self.is_auto_hide:
            script += "Common.overlay_setup('mouseup',function(){%s})" %self.get_off_script()
             
        return script

    def get_off_script(self):
        return "Effects.fade_out('%s', 200); document.removeEvents('mouseup')" % self.get_name()






class PopupMenuWdg(BaseInputWdg):

    def __init__(self,name=None, type=None, label=None, action_name=None, \
            multi=False, height='', width=''):
        '''
        Creates a popup widget

        @params
        name: inherited (optional)
        type: inherited (optional)
        label: inherited (optional)
        action_name: name of hidden widget that performs the action.  If not
            specified, defaults to name
        multi: adds checkbox (optional)
        '''
        
        super(PopupMenuWdg,self).__init__(name,type,label)
        if action_name:
            self.action_name = action_name
        else:
            self.action_name = name
        self.multi = multi
        self.title = ''
        self.offset_x = 10
        self.offset_y = 0
        self.height = height
        self.menu_width = width
        self.monitor = None
        self.is_submit = True
        self.is_auto_hide = True
        # this is the group name
        self.item_name = '%s_item' %self.get_input_name()


    
    def set_auto_hide(self, hide):
        self.is_auto_hide = hide

    def add_monitor(self, widget):
        ''' add a monitor div on the right side'''
        self.monitor = widget

    def add_separator(self):
        widget = "<hr/>"
        super(PopupMenuWdg,self).add(widget)

    def add_title(self, title):
        if isinstance(title, basestring):
            widget = FloatDivWdg("<b>%s</b>" % title)
        else:
            widget = "<b>%s</b>" % title.get_buffer_display()
        
        self.title = widget

        self.title.add_style('border-bottom','1px dotted #ccc')
    
    def add(self, widget, name=None):
        if isinstance(widget, six.string_types):
            tmp = widget
            widget = StringWdg(widget)
            if not name:
                name = tmp
            widget.set_name(name)
        else:
            if name:
                widget.set_name(name)

        super(PopupMenuWdg,self).add(widget,name)


    def set_offset(self, x, y):
        self.offset_x = x
        self.offset_y = y

    def set_submit(self, submit):
        self.is_submit = submit


    def get_display(self):

        div = DivWdg(css="popup_wdg")
        div.set_id(self.name)
        select_name = '%s_hidden' % self.action_name
        if not self.multi:
            hidden = HiddenWdg(select_name)
            hidden.set_id(select_name)
            div.add(hidden)
        """
        hidden_name = '%s_hidden' % self.name
        div.add(HiddenWdg(hidden_name))
        """
        div.add_style("display: none")
        div.add_style("margin", "5px 0px 0px 0px")
        div.add_style("position", "absolute")

        from web_wdg import CloseWdg
        
        div.add(self.title)
        div.add(CloseWdg(self.get_off_script()))
        div.add(HtmlElement.br())


        content_div = FloatDivWdg()
        if self.height:
            height = self.height
            try:
                height = int(height)
                height = str(height) + "px"
            except ValueError:
                pass
            content_div.add_style('height', height)
        content_div.add_style('clear', 'left')
        content_div.add_style('padding-top','8px')
        div.add(content_div)



       
        for widget in self.widgets:
            if not widget.get_name():
                item = DivWdg(css='hand')
                item.add(widget)
                if self.menu_width:
                    menu_width = self.menu_width
                    try:
                        menu_width = int(menu_width)
                        menu_width = str(menu_width) + "px"
                    except ValueError:
                        pass
                    item.add_style('width', menu_width)
                content_div.add(item)
                continue
            id='%s_%s' %(self.get_input_name(), widget.get_name())
            item = DivWdg(css="hand")
            item.set_attr('name', self.item_name)
            item.set_attr('tab', id)
            if self.menu_width:
                menu_width = self.menu_width
                try:
                    menu_width = int(menu_width)
                    menu_width = str(menu_width) + "px"
                except ValueError:
                    pass
                item.add_style('width', menu_width)
            item.add_style('padding-left','3px')
            
            
            # checkbox and extra logic is added for named widgets only
            if self.multi:
                span = SpanWdg(widget, css='small')
                #checkbox = CheckboxWdg("%s_select" % self.name)
                checkbox = CheckboxWdg(select_name)
                cb_id = '%s|%s' %(select_name, widget.get_name())
                checkbox.set_id(cb_id)
                checkbox.set_option( "value", widget.get_name())
                
                item.add(checkbox)
                span.add_event("onclick", "var a=get_elements('%s');a.toggle_me('%s')" %(checkbox.get_name(), cb_id))

                item.add(span)
            else:
                item.add(widget)

            # FIXME: these colors should reflect the skin
            #item.add_event("onmouseover", "this.style.backgroundColor='#333'")
            #item.add_event("onmouseout", "this.style.backgroundColor='#555'")
            item.add_event("onmouseover", "this.style.fontWeight='600'")
            item.add_event("onmouseout", "this.style.fontWeight='100'")
            """
            if not self.multi:
                item.add_event("onclick", "el=document.form.elements['%s'];el.value='%s';document.form.submit()" % (select_name,widget.get_name()) )
            else:
                pass

            """
            
            if not self.multi: 
                item.add_event("onclick", "get_elements('%s').tab_me('%s','active_menu_item',\
                'inactive_menu_item'); get_elements('%s').set_value('%s')" \
                % ( self.item_name, id, select_name,widget.get_name()) )
            if self.is_submit:
                 item.add_event("onclick", "document.form.submit()")
            content_div.add(item)

        if self.monitor:
            mon_div = FloatDivWdg(self.monitor, id='%s_monitor' %self.get_input_name(),float='left')
            height = self.height
            try:
                height = int(height)
                height = str(height) + "px"
            except ValueError:
                pass
            mon_div.add_style('height', height)
            mon_div.add_style('display', 'none')
            mon_div.add_class('monitor')
            div.add(mon_div)
        return div


    def get_on_script(self):

        #script = "Common.follow_click(event, '%s', %d, %d); set_display_on('%s');"\
        #    %(self.get_name(),self.offset_x, self.offset_y, self.get_name())
        script = "Effects.fade_in('%s', 30);"%self.get_name()
        if self.is_auto_hide:
            script += "Common.overlay_setup('mouseup',function(){%s})" %self.get_off_script()
             
        return script

    def get_off_script(self):
        return "Effects.fade_out('%s', 200); document.removeEvents('mouseup')" % self.get_name()

    def get_monitor_on_script(self):
        return "Effects.fade_in('%s_monitor', 50)" % self.get_input_name()

    def get_monitor_off_script(self):
        return "set_display_off('%s_monitor')" % self.get_input_name()


    def get_clear_css_script(self):
        ''' clears the css of the menu buttons, make them inactive'''
        return "$$('div[name=%s]').each(function(elem) {elem.className='inactive_menu_item';})" %self.item_name



class ColorWdg(BaseInputWdg):

    def __init__(self,name=None, label=None, css=None):
        super(ColorWdg,self).__init__(name,"input", label)
        self.set_attr("type", "color")
        self.label = label
        self.css = css

        self.add_class("spt_input")


    def get_display(self):
        self.set_attr("name", self.get_input_name())

        if self.is_read_only():
            self.set_attr('disabled', 'disabled')

        if not self.label:
            color_wdg = super(ColorWdg, self).get_display()
            return color_wdg
        else:
            color_wdg = BaseInputWdg.get_class_display(self)
            span = SpanWdg(color_wdg, css=self.css)
            span.add(self.label)
            return span




