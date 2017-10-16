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
"PopupWdg", "PopupMenuWdg"
]


import os, shutil, string, types

from pyasm.common import Common, Marshaller, Date, SPTDate, TacticException
from pyasm.biz import File, Snapshot, Pipeline, NamingUtil, ExpressionParser, PrefSetting
from pyasm.web import *
from pyasm.search import Search, SearchKey, SearchException
from icon_wdg import IconButtonWdg, IconWdg

from operator import itemgetter

class InputException(Exception):
    pass


 
class BaseInputWdg(HtmlElement):

    ARGS_KEYS = {}
    def get_args_keys(cls):
        '''external settings which populate the widget'''
        return cls.ARGS_KEYS
    get_args_keys = classmethod(get_args_keys)


    #def __init__(my, name=None, type=None, label=None):
    def __init__(my, name=None, type=None, label=None, **kwargs):
        super(BaseInputWdg,my).__init__(type)

        # the name of the input element
        my.name = name
        my.input_prefix = None
        my.value = ""
        my.options = {}
        my.options['default'] = ""
        my.options['persist'] = "false"
        if kwargs:
            my.options = kwargs
            my.kwargs = kwargs

        my.persistence = False
        my.persistence_obj = None
        my.cached_values = None
        my.label = label
        my.disabled_look = True
        my.prefix = ''
        my.change_cbjs_action = ''
        # deprecated
        my.element = None

        my.parent_wdg = None
        my.state = {}

        my.title = ''

        my.related_type = None


    # FIXME: need to make this more elegant: these are only put here
    # to conform to the interface of BaseTableElementWdg so that these
    # elements can be put into a TableWdg.  This should be more formal
    # because the relationship here is quite tenuous
    def get_style(my):
        return ""
    def get_bottom(my):
        return ""




    def copy(my, input):
        '''copies the parameters of one widget to the other. This is useful
        for transfering the parameters specified in a config file to a contained
        widget.'''
        my.name = input.name
        my.input_prefix = input.input_prefix
        my.options = input.options
        my.sobjects = input.sobjects
        my.current_index = input.current_index

        my.set_sobject = input.get_current_sobject()


    def set_state(my, state):
        '''Set the state for this table element'''
        my.state = state

    def get_state(my):
        '''get the state for this table element'''
        return my.state



    def get_related_type(my):
        '''Some input widgets will be related to a search type to define
        a list or range of parameters.  This will allow an external
        widget to discover this relationship and provide a means to add
        to this list'''
        return my.related_type




    def set_title(my, title):
        my.title = title
        
    def get_display_title(my):
        '''Function that that gives a title represenation of this widget'''
        if my.title:
            return my.title

        name = my.get_name()
        name = name.replace("_", " ")
        return name.title()
 


    def get_title(my):
        '''Function that that gives a title represenation of this widget'''
        if my.title:
            return my.title

        name = my.get_name()
        title = string.replace(my.name, "_", " ")
        title = title.capitalize()
        span = SpanWdg(title)

       
        return span


    def _add_required(my, span, offset_x=10):
        required_span = DivWdg("*")
        required_span.add_style("position: absolute")
        required_span.add_style("margin-left: -%dpx"% offset_x)

        required_span.add_color("color", "color", [50, 0, 0])
        required_span.add_style("font-size: 1.0em")
        
        span.add(required_span)
        span.add_class("spt_required")

    def set_parent_wdg(my, parent_wdg):
        '''method to set the parent widget.  This is typicaly the EditWdg'''
        my.parent_wdg = parent_wdg

    def get_parent_wdg(my):
        return my.parent_wdg


    def set_layout_wdg(my, layout_wdg):
        my.parent_wdg = layout_wdg

        
    def get_prefs(my):
        '''Function that that gives a preference widget for this input'''
        return ""


    def set_input_prefix(my, input_prefix):
        my.input_prefix = input_prefix

    def get_input_name(my, name=''):
        input_name = my.name
        if name:
            input_name = name
        if my.input_prefix:
            return "%s|%s" % (my.input_prefix, input_name)
        else:
            return input_name


    def set_name(my, name):
        '''set the name externally'''
        my.name = name

    
    def get_name(my):
        return my.name

    def get_label(my):
        if my.label:
            return my.label
        else:
            return my.name

    def set_options(my, options):
        my.options = options
		
        if my.has_option('search_key'):
		    search_key = options.get('search_key')
		    if search_key:
				sobj = SearchKey.get_by_search_key(search_key)
				my.set_sobjects([sobj])

            

    def has_option(my, key):
        return my.options.has_key(key)
 
    def set_option(my, key, value):
        my.options[key] = value
        
    def get_option(my, key):
        '''gets the value of the specified option'''
        if my.options.has_key(key):
            return my.options[key]
        else:
            return ""

    def set_disabled_look(my, disable):
        my.disabled_look = disable

    def is_read_only(my):
        ''' if the read_only option is true, either set disabled or readonly'''
        if my.get_option('read_only') in ['true', True]:
            return True
        return False

    def is_edit_only(my):
        return my.get_option('edit_only') == 'true'

    def is_simple_viewable(my):
        return True

    def is_editable(my):
        return True

    def get_timezone_value(my, value):
        '''given a datetime value, try to convert to timezone specified in the widget.
           If not specified, use the My Preferences time zone'''
        timezone = my.get_option('timezone')
        if not timezone:
            timezone = PrefSetting.get_value_by_key('timezone')
        
        if timezone in ["local", '']:
            value = SPTDate.convert_to_local(value)
        else:
            value = SPTDate.convert_to_timezone(value, timezone)
        
        return value

    def check_persistent_values(my, cgi_values):
        web = WebContainer.get_web()
        if my.is_form_submitted() and web.has_form_key(my.get_input_name()):
            # if the form is submitted, then always use the submitted value
            my._set_persistent_values(cgi_values)
            my.cached_values = cgi_values
            return cgi_values
        else:
            return False

    def check_persistent_display(my, cgi_values):
        # no longer checking for web.get_form_keys()
        web = WebContainer.get_web()
        if my.get_option("persist") == "true":
            # old web implementation
            if web.has_form_key(my.get_input_name()):
                values = cgi_values
                #my._set_persistent_values(values)
                return values
            else:
                # try the json implementation if it has been set
                from tactic.ui.filter import FilterData 
                filter_data = FilterData.get()
                values = filter_data.get_values_by_prefix(my.prefix)
                if values:
                    values = values[0]
                    value = values.get(my.get_input_name())
                    if value:
                        cgi_values = [value]
                        #my._set_persistent_values(cgi_values)
                        return cgi_values
                return False
        else:
            return False

    def get_values(my, for_display=False):
        '''gets the current value of this input element.  The order of
        importance is as follows.  If the form was submitted, this value
        will always take precedence.  Then externally set values through
        code.'''
        values = []
       
        web = WebContainer.get_web()
        if my.has_option('search_key') and not my.get_current_sobject():
            sobject = SearchKey.get_by_search_key(my.options.get('search_key'))
            if sobject:
                my.set_sobjects([sobject])
        
        # getting the value from CGI depends on whether this is for display
        # of the widget or for getting the current value of this widget.
        cgi_values = web.get_form_values( my.get_input_name() )

        if for_display:

            # get it from the sobject: this grabs the values from the
            # sobject in the db for editing
            column = my.get_option('column')
            if not column:
                column = my.name

            if my.get_current_sobject() and \
                    my.get_current_sobject().has_value(column):
                sobject = my.get_current_sobject()
                values = [sobject.get_value(column)]
                if not values:
                    values = []
                return values



            # if set explicitly, then this is the value
            if my.value != '':
                
                values = [my.value]
                my._set_persistent_values(values)
                return values


            # the value is taken from CGI only if the input is persistent
            values = my.check_persistent_display(cgi_values)
            if values != False:
                return values
            else:
                values = []
            
            # This option will read the webstate if no explicit value is
            # present
            if my.get_option("web_state") == "true":
                # this will eventually use the WebState: for now, use cgi
                values = cgi_values
                if values and values[0] != "":
                    my._set_persistent_values(values)
                    return values

        # if this has been called before, get the previous value
        elif my.cached_values != None:
            return my.cached_values
        
       
        # check for key existence only in for_display=False
        #elif my.is_form_submitted() and web.has_form_key(my.get_input_name()):
        #    # if the form is submitted, then always use the submitted value
        #    my._set_persistent_values(cgi_values)
        #    my.cached_values = cgi_values
        #    return cgi_values
        else: 
            temp_values = my.check_persistent_values(cgi_values)
            if temp_values != False:
                return temp_values  
        # if there are values in CGI, use these
        if not for_display and cgi_values:
            values = cgi_values
           
        
        # if the value has been explicitly set, then use that one
        elif my.value != '':
            values = [my.value]
          

        
        # otherwise, get it from the sobject: this grabs the values from the
        # sobject in the db for editing
        elif my.get_current_sobject() and \
                my.get_current_sobject().has_value(my.name):
            sobject = my.get_current_sobject()
            values = [sobject.get_value(my.name)]
            if not values:
                values = []


        # This option will read the webstate if no explicit value is
        # present
        elif my.get_option("web_state") == "true":
            # this will eventually use the WebState: for now, use cgi
            values = cgi_values
            my._set_persistent_values(values)
            my.cached_values = values
            return values




        # otherwise, get it from the persistence (database)
        elif my.persistence:
            class_path = Common.get_full_class_name(my.persistence_obj)
            key = "%s|%s" % (class_path, my.name)
            #values = WidgetSettings.get_key_values(key, auto_create=False)
            values = WidgetSettings.get_key_values(key)
        
        # if all of the above overrides fail, then set to the default
        # the rules for persistent input is slightly different
        if (values == None and my.persistence) or (values == [] and not my.persistence):
            default = my.get_option("default")
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
            #web.set_form_value(my.name, values[0])
            web.set_form_value(my.get_input_name(), values)
            my._set_persistent_values(values)
      
        # only cache if it is not for display: otherwise we have to separate
        # the for display cache and the non for display cache
        if not for_display:
            my.cached_values = values

        return values


    def _set_persistent_values(my, values):

        if my.persistence:

            class_path = Common.get_full_class_name(my.persistence_obj)
            key = "%s|%s" % (class_path, my.name)

            # make sure the value is not empty
            if not values:
                values = []

            # if the current value is different from stored value, then update
            # this check is done in set_key_values()
            WidgetSettings.set_key_values(key, values)


    

    def get_value(my, for_display=False):
        values = my.get_values(for_display)
        if not values:
            return ""
        else:
            return values[0]



    def set_value(my, value, set_form_value=True):
        my.value = value

        # some widgets do not have names (occasionally)
        name = my.get_input_name()
        if not name:
            return


        # when the value is explicitly set, the set then form value as such
        if set_form_value:
            web = WebContainer.get_web()
            web.set_form_value(name, value)



    def set_persistence(my, object=None):
        my.persistence = True
        if object == None:
            object = my
        my.persistence_obj = object

        # this implies persist on submit (it is also faster)
        my.set_persist_on_submit()


    def set_persist_on_submit(my, prefix=''):
        my.set_option("persist", "true")
        my.prefix = prefix

    def set_submit_onchange(my, set=True):
        if set:
            my.change_cbjs_action = 'spt.panel.refresh( bvr.src_el.getParent(".spt_panel") );'
            #my.add_behavior(behavior)

        else:
            print("DEPRECATED: set_submit_onchange, arg set=False")
            my.remove_event('onchange')

    def is_form_submitted(my):
        web = WebContainer.get_web()
        if web.get_form_value("is_from_login") == "yes":
            return False

        # all ajax interactions are considered submitted as well
        if web.get_form_value("ajax"):
            return True

        return web.get_form_value("is_form_submitted") == "yes"

    def set_form_submitted(my, event='onchange'):
        '''TODO: deprecated this: to declare if a form is submitted, used primarily for FilterCheckboxWdg'''
        my.add_event(event, "document.form.elements['is_form_submitted'].value='yes'", idx=0)

    def set_style(my, style):
        '''Sets the style of the top widget contained in the input widget'''
        my.element.set_style(style)

    def get_key(my):
        if not my.persistence_obj:
            my.persistence_obj = my
        key = "%s|%s"%(Common.get_full_class_name(my.persistence_obj), my.name)
        return key

    def get_save_script(my):
        '''get the js script to save the value to widget settings for persistence'''
        key = my.get_key()
        return "spt.api.Utility.save_widget_setting('%s', bvr.src_el.value)" %key;

    def get_refresh_script(my):
        '''get a general refresh script. use this as a template if you need to pass in 
           bvr.src_el.value to values'''
        return "var top=spt.get_parent_panel(bvr.src_el); spt.panel.refresh(top, {}, true)"

class BaseTextWdg(BaseInputWdg):
    def handle_mode(my):
        return
        '''
        # DISABLED for now
        mode = my.options.get("mode")
        if mode == "string":
            behavior = {
                'type': 'keyboard',
                'kbd_handler_name': 'DgTableMultiLineTextEdit'
            }
            my.add_behavior(behavior)
        elif mode in ["float", "integer"]:
            behavior = {
                'type': 'keyboard',
                'kbd_handler_name': 'FloatTextEdit' 
            }
            my.add_behavior(behavior)
        '''

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
 

    def __init__(my,name=None, label=None):
        super(TextWdg,my).__init__(name,"input", label=label)
        my.css = "inputfield"
        my.add_class("spt_input")
    
   

    def get_display(my):
        input_type = my.get_option("type")
        if not input_type:
            input_type = "text"

        my.set_attr("type", input_type)
        my.set_attr("name", my.get_input_name())


        if my.is_read_only():
            # do not set disabled attr to disabled cuz usually we want the data to
            # get read and passed to callbacks
            my.set_attr('readonly', 'readonly')
            if my.disabled_look == True:
                #my.add_class('disabled')
                my.add_color("background", "background", -10)
        value = my.get_value(for_display=True)
        # this make sure that the display
        if isinstance(value, basestring):
            value = value.replace('"', '&quot;')
        my.set_attr("value", value)

        size = my.get_option("size")
        if size:
            my.set_attr("size", size)

        my.handle_mode()
        required = my.get_option("required")
        if required == "true":
            text = BaseInputWdg.get_class_display(my)
            wdg = SpanWdg()

            my._add_required(wdg)
            wdg.add(text)
            return wdg

        else:    
            return super(TextWdg,my).get_display()

class FilterTextWdg(TextWdg):
    '''This composite text acts as a filter and can be, for instance, 
        used in prefs area in TableWdg'''
    def __init__(my,name=None, label=None, css=None , is_number=False, has_persistence=True):
        super(FilterTextWdg,my).__init__(name, label=label)
        if is_number:
            my.add_event('onchange',\
                "val=document.form.elements['%s'].value; if (Common.validate_int(val))\
                    document.form.submit(); else \
                    {alert('[' + val + '] is not a valid integer.')}" %name)  
                
        else:
            my.set_submit_onchange()

        if has_persistence:
            my.set_persistence()
        else:
            my.set_persist_on_submit()
        my.css = css
        my.unit = ''

    def set_unit(my, unit):
        my.unit = unit
        
    
    def get_display(my):
        my.handle_behavior()
        if not my.label:
            return super(FilterTextWdg, my).get_display()
        else:
            text = TextWdg.get_class_display(my)
            span = SpanWdg(my.label, css=my.css)
            span.add(text)
            span.add(my.unit)
            return span

    def handle_behavior(my):
        if my.persistence:
            key = my.get_key()
            value = WidgetSettings.get_value_by_key(key)
            if value:
                my.set_value(value)

            behavior = {"type" : "change",
                    "cbjs_preaction":\
                    "spt.api.Utility.save_widget_setting('%s',bvr.src_el.value)"%key}
            if my.change_cbjs_action:
                behavior['cbjs_action'] = my.change_cbjs_action
            my.add_behavior(behavior)

    

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

    def __init__(my,name=None, **kwargs):
        super(TextAreaWdg,my).__init__(name,"textarea", **kwargs)
        
        my.kwargs = kwargs
        # on OSX rows and cols flag are not respected
        width = kwargs.get("width")
        if width:
            my.add_style("width", width)
        height = kwargs.get("height")
        if height:
            my.add_style("height", height)

    
        web = WebContainer.get_web()
        browser = web.get_browser()
        if browser == "Qt":
            rows = None
            cols = None
        else:
            rows = kwargs.get("rows")
            cols = kwargs.get("cols")
            if rows:
                my.set_attr("rows", rows)
            if cols:
                my.set_attr("cols", cols)

        browser = web.get_browser()
        if not width and not cols:
            width = 300
            my.add_style("width", width)



        my.add_class("spt_input")
        my.add_border()



    def get_display(my):
        my.set_attr("name", my.get_input_name())
        #my.add_style("font-family: Courier New")

        my.add_color("background", "background", 10)
        my.add_color("color", "color")
        #my.add_border()


        rows = my.get_option("rows")
        cols = my.get_option("cols")
        if not rows:
            rows = 3
        my.set_attr("rows", rows)

        if not cols:
            cols = 50

        my.set_attr("cols", cols)

        if my.is_read_only():
            my.set_attr('readonly', 'readonly')
            if my.disabled_look == True:
                #my.add_class('disabled')
                my.add_color("background", "background", -10)
        
        # value always overrides
        value = my.kwargs.get("value")
        if not value:
            value = my.get_value(for_display=True)
        my.add(value)

        #my.handle_mode()
        if my.get_option("required") in [True, 'true']:
            text_area = BaseInputWdg.get_class_display(my)
            wdg = SpanWdg()
            my._add_required(wdg)
            wdg.add(text_area)
            return wdg

        return super(TextAreaWdg,my).get_display()



class RadioWdg(BaseInputWdg):
    def __init__(my,name=None, label=None):
        super(RadioWdg,my).__init__(name,"input")
        my.set_attr("type", "radio")
        my.label = label

    def set_checked(my):
        my.set_attr("checked", "1")


    def get_display(my):

        my.set_attr("name", my.get_input_name())
        my.add_class("spt_input")

        # This is a little confusing.  the option value is mapped to the
        # html attribute value, however, the value from get_value() is the
        # state of the element (on or off)
        values = my.get_values(for_display=True)

        # determine if this is checked
        if my.name != None and len(values) != 0 \
                and my.get_option("value") in values:
            my.set_checked()

        # convert all of the options to attributes
        for name, option in my.options.items():
            my.set_attr(name,option)

        if my.label:
            span = SpanWdg()
            span.add(" %s" % my.label)
            my.add(span)
            span.add_style("top: 3px")
            span.add_style("position: relative")

        return super(RadioWdg,my).get_display()




class CheckboxWdg(BaseInputWdg):
    def __init__(my,name=None, label=None, css=None):
        super(CheckboxWdg,my).__init__(name,"input", label)
        my.set_attr("type", "checkbox")
        my.label = label
        my.css = css

        my.add_class("spt_input")

        my.add_style("display: inline-block")
        my.add_style("vertical-align: middle")
        my.add_style("margin: 0")



    def set_default_checked(my):
        ''' this is used for checkbox that has no value set'''
        my.set_option("default", "on")

    def set_checked(my):
        my.set_option("checked", "1")


    def is_checked(my, for_display=False):
        # Checkbox needs special treatment when comes to getting values
        values = my.get_values(for_display=for_display)
        value_option = my._get_value_option()
        # FIXME if values is boolean, it will raise exception
        if value_option in values:
            return True
        else:
            return False
        #return my.get_value() == my._get_value_option()

    def _get_value_option(my):
        value_option = my.get_option("value")
        if value_option == "":
            value_option = 'on'
        return value_option

    def get_key(my):
        class_path = Common.get_full_class_name(my)
        key = "%s|%s" % (class_path, my.name)
        return key
   
    def check_persistent_values(my, cgi_values):
        web = WebContainer.get_web()
        if my.is_form_submitted():# and web.has_form_key(my.get_input_name):
            # if the form is submitted, then always use the submitted value
            if not my.persistence_obj:
                return False
            class_path = Common.get_full_class_name(my.persistence_obj)
            key = "%s|%s" % (class_path, my.name)
            setting = WidgetSettings.get_by_key(key, auto_create=False)
            if setting == None:
                return False
            if not my.is_ajax(check_name=False):
                my._set_persistent_values(cgi_values)
            my.cached_values = cgi_values
                
            return cgi_values
        else:
            return False

   

    def get_display(my):
        my.set_attr("name", my.get_input_name())

        # This is a little confusing.  the option value is mapped to the
        # html attribute value, however, the value from get_value() is the
        # state of the element (on or off) or the "value" option
        values = my.get_values(for_display=True)
        # for multiple checkboxes using the same name

        my.add_style("width", "16px", override=False)
        my.add_style("height", "16px", override=False)

        if my.is_read_only():
            my.set_attr('disabled', 'disabled')

        if len(values) == 1:
            # skip boolean
            value = values[0]
            if value and not isinstance(value, bool) and '||' in value:
                values = value.split('||')
        # determine if this is checked
        value_option = my._get_value_option()
        if values and len(values) != 0:
            if value_option in values:
                my.set_checked()
            elif True in values: # for boolean columns
                my.set_checked()

        # convert all of the options to attributes
        for name, option in my.options.items():
            my.set_attr(name,option)

        my.handle_behavior()

        if not my.label:
            return super(CheckboxWdg, my).get_display()
        else:
            cb = BaseInputWdg.get_class_display(my)
            span = SpanWdg(cb, css=my.css)
            span.add(my.label)
            return span

        return super(CheckboxWdg,my).get_display()

    def handle_behavior(my):
        if my.persistence:
            key = "%s|%s"%(Common.get_full_class_name(my.persistence_obj), my.name)
            value = WidgetSettings.get_value_by_key(key)
     
            if value:
                my.set_value(value)

            behavior = {"type" : "click_up",
                    'propagate_evt': True,
                    "cbjs_preaction":
                    "spt.input.save_selected(bvr, '%s','%s')"%(my.name, key)}
                    #"spt.api.Utility.save_widget_setting('%s',bvr.src_el.value)"%key}
            #if my.change_cbjs_action:
            #    behavior['cbjs_action'] = my.change_cbjs_action
            my.add_behavior(behavior)

class FilterCheckboxWdg(CheckboxWdg):
    '''This composite checkbox acts as a filter and can be, for instance, 
        used in prefs area in TableWdg'''
    def __init__(my,name=None, label=None, css=None ):
        super(FilterCheckboxWdg,my).__init__(name, label=label, css=css)
        #my.set_submit_onchange()
        
        my.set_persistence()
       
    

    def get_display(my):
        # order matters here
        return super(FilterCheckboxWdg, my).get_display()
        

       
        

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
        'order': 0,
        'category': 'Options'

    },
    'labels': {
        'description': 'A list of values separated by | that determine the label of the selection',

        'order': 1,
        'category': 'Options'
    },
     'values_expr': {
        'description': 'A list of values retrieved through an expression. e.g. @GET(prod/shot.code)',
        'type': 'TextAreaWdg',
        'order': 2
    },
    'labels_expr': {
        'description': 'A list of labels retrieved through an expression. e.g. @GET(prod/shot.name)',
        'type': 'TextAreaWdg',
        'order': 3
    },
    'mode_expr': {
        'description': 'Specify if it uses the current sObject as a starting point',
        'type': 'SelectWdg',
        'values': 'relative',
        'empty': 'true',
        'order': 4,
    },
    'empty': {
        'description': 'The label for an empty selection',
        #'default': '-- Select --',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 3,
        'category': 'Options'
    },
    'default': {
        'description': 'The default selection value in an edit form. Can be a TEL variable.',
        'type': 'TextWdg',
        'category': 'Options',
        'order': 2,
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


    def __init__(my, name=None, **kwargs):
        my.kwargs = kwargs
        css = kwargs.get('css')
        label = kwargs.get('label')
        bs = kwargs.get('bs')

        my.sobjects_for_options = None
        my.empty_option_flag = False
        my.empty_option_label, my.empty_option_value = (my.SELECT_LABEL, "")
        my.append_list = []
        my.values = []
        my.labels = []
        my.has_set_options = False
        my.css = css
        my.append_widget = None
        super(SelectWdg,my).__init__(name, type="select", **kwargs)
        
        # add the standard style class
        my.add_class("inputfield")
        my.add_class("spt_input")

        # BOOTSTRAP
        if bs != False:
            my.add_class("form-control")
            my.add_class("input-sm")



    def get_related_type(my):
        # In order to get the related type, the dom options need to have
        # been processed
        if not my.has_set_options:
            my.set_dom_options(is_run=False)

        return my.related_type


    def add_empty_option(my, label='---', value= ''):
        '''convenience function to an option with no value'''
        my.empty_option_flag = True
        my.empty_option_label, my.empty_option_value = label, value

    def add_none_option(my):
        my.append_option("-- %s --" %SelectWdg.NONE_MODE,\
                SelectWdg.NONE_MODE)

    def remove_empty_option(my):
        my.empty_option_flag = False

    def append_option(my, label, value):
        my.append_list.append((label, value))

    def set_search_for_options(my, search, value_column=None, label_column=None):
        assert value_column != ""
        assert label_column != ""
        sobjects = search.do_search()
        my.set_sobjects_for_options(sobjects,value_column,label_column)


    def set_sobjects_for_options(my,sobjects,value_column=None,label_column=None):
        if value_column == None:
            my.value_column = my.name
        else:
            my.value_column = value_column

        if label_column == None:
            my.label_column = my.value_column
        else:
            my.label_column = label_column

        assert my.value_column
        assert my.label_column

        my.sobjects_for_options = sobjects


    def _get_setting(my):
        ''' this check setting and add warnings if it's empty'''
        values_option = [] 
        labels_option = []
        setting = my.get_option("setting")
        if setting:
            from pyasm.prod.biz import ProdSetting

            values_option = ProdSetting.get_seq_by_key(setting)
            
            if not values_option:
                data_dict = {'key': setting}
                prod_setting = ProdSetting.get_by_key(setting)
                search_id = -1
                setting_value = my.DEFAULT_SETTING.get(setting)
                if prod_setting:
                    if setting_value:
                        # use the default if available
                        prod_setting.set_value('value', setting_value)
                        prod_setting.commit()
                        values_option = ProdSetting.get_seq_by_key(setting)
                        labels_option = values_option
                    else:
                        # prompt the user to do it instead
                        my._set_append_widget(prod_setting.get_id(), data_dict)
                     
                
                # if it is a new insert
                else:
                    if setting_value:
                        data_dict['value'] = setting_value
                        type = 'sequence'
                        ProdSetting.create(setting, setting_value, type)
                        values_option = ProdSetting.get_seq_by_key(setting)
                        labels_option = values_option
                    else:
                       my._set_append_widget(search_id, data_dict)
                
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
  

    def _set_append_widget(my, search_id, data_dict):
        from web_wdg import ProdSettingLinkWdg
        prod_setting_link = ProdSettingLinkWdg(search_id)
        prod_setting_link.set_value_dict(data_dict) 

        # HACK: usually when there is an iframe, there is a widget value
        #if WebContainer.get_web().get_form_value('widget'):
        #    prod_setting_link.set_layout('plain')
        my.append_widget = prod_setting_link

    def set_dom_options(my, is_run=True):
        ''' set the dom options for the Select. It should only be called once
        or there will be some unexpected behaviour'''
        # get the values
        my.values = []
        labels_option = my.get_option("labels")
        values_option = my.get_option("values")
        
        # if there are no values, check if there is a project setting
        # which will provide both values_option and labels_option
        if not values_option:
            values_option, labels_option = my._get_setting()
        
        if type(values_option) == types.ListType:
            my.values.extend(values_option)
            
            
        elif my.values != "":
            my.values = string.split( my.get_option("values"), "|" )
        else:
            my.values = ["None"]

        # get the labels for the select options
        
        my.labels = []
        if type(labels_option) == types.ListType:
            my.labels = labels_option[:]
        elif labels_option != "":
            my.labels = string.split( labels_option, "|" )
            if len(my.values) != len(my.labels):
                raise InputException("values [%s] does not have the same number of elements as [%s]" % (`my.values`, `my.labels`))

        else:
            my.labels = my.values[:]

        query = my.get_option("query")
        if query and query != "" and query.find("|") != -1:
            search_type, value, label = query.split("|")
            project_code = None
            search = None

            current_sobj = my.get_current_sobject()
            if current_sobj:
                project_code = current_sobj.get_project_code()
            try:
                search = Search(search_type, project_code=project_code)
            except SearchException, e:
                # skip if there is an unregistered sType or the table does not exist in the db
                if e.__str__().find('does not exist for database') != -1 or 'not registered' != -1:
                    my.values = ['ERROR in query option. Remove it in Edit Mode > Other Options']
                    my.labels =  my.values[:]
                    return
        

            query_filter = my.get_option("query_filter")
            if query_filter:
                search.add_where(query_filter)
            query_limit = my.get_option("query_limit")
            if query_limit:
                search.add_limit(int(query_limit))

            if '()' not in label:
                search.add_order_by(label)
            elif '()' not in value:
                search.add_order_by(value)

            if not value or not label:
                raise InputException("Query string for SelectWdg is malformed [%s]" % query)

            # store the related type
            my.related_type = search_type

            my.set_search_for_options(search,value,label)



        values_expr = my.get_option("values_expr")
        if not values_expr:
            values_expr = my.kwargs.get("values_expr")

        labels_expr = my.get_option("labels_expr")
        if not labels_expr:
            labels_expr = my.kwargs.get("labels_expr")

        mode_expr = my.get_option("mode_expr")
        if not mode_expr:
            mode_expr = my.kwargs.get("mode_expr")
        if values_expr:
            if mode_expr == 'relative':
                sobjects = my.sobjects
                if not sobjects:
                    parent_wdg = my.get_parent_wdg()
                    if parent_wdg:
                        # use the search_key as a starting point if applicable
                        sk = parent_wdg.kwargs.get('search_key')
                        if sk:
                            sobjects = [Search.get_by_search_key(sk)]
                    else:
                        sk = my.kwargs.get('search_key')
                        if sk:
                            sobjects = [Search.get_by_search_key(sk)]

            else:
                sobjects = []
            try:
                parser = ExpressionParser()
                my.values = parser.eval(values_expr, sobjects=sobjects)
            except Exception, e:
                print "Expression error: ", str(e)
                my.values = ['Error in values expression']
                my.labels = my.values[:]
                # don't raise anything yet until things are properly drawn
				#raise InputException(e) 

            
            if labels_expr:
                try:
                    my.labels = parser.eval(labels_expr, sobjects=sobjects)
                    # expression may return it as a string when doing concatenation is done on a 1-item list
                    if isinstance(my.labels, basestring):
                        my.labels = [my.labels]
                except Exception, e:
                    print "Expression error: ", str(e)
                    my.labels = ['Error in labels expression']
            else:
                my.labels = my.values[:]

            # create a tuple for sorting by label if it's a list
            if my.values:
                zipped = zip(my.values, my.labels)
                zipped = sorted(zipped, key=itemgetter(1))
                unzipped = zip(*zipped)
                my.values = list(unzipped[0])
                my.labels = list(unzipped[1])
           
        # if there is a search for options stored, then use these
        if my.sobjects_for_options != None:
            my.values = []
            my.labels = [] 
            for sobject in my.sobjects_for_options:
                # if there was a function call, use it
                if my.value_column.find("()") != -1:
                    my.values.append( eval("sobject.%s" % my.value_column ) )
                else:
                    my.values.append(sobject.get_value(my.value_column, no_exception=True))


                if my.label_column.find("()") != -1:
                    my.labels.append( eval("sobject.%s" % my.label_column ) )
                else:
                    my.labels.append(sobject.get_value(my.label_column, no_exception=True))

        # manually add extra values and labes
        extra_values = my.get_option("extra_values") 
        if extra_values:
            extra_values = extra_values.split("|")
            my.values.extend(extra_values)

            extra_labels = my.get_option("extra_labels") 
            if extra_labels:
                extra_labels = "|".split(extra_labels)
                my.labels.extend(extra_labels)
            else:
                my.labels.extend(extra_values)

        
        # add empty option
        is_empty = my.get_option("empty") not in ['','false'] or my.get_option("empty_label")
        if my.empty_option_flag or is_empty:
            my.values.insert(0, my.empty_option_value)
            # empty_label takes prescedence over empty (boolean)
            
            if my.get_option("empty_label"):
                my.labels.insert(0, my.get_option("empty_label"))
            else:
                my.labels.insert(0, my.empty_option_label)

        # append any custom ones
        if my.append_list:
            for label, value in my.append_list:
                my.values.append(value)
                my.labels.append(label)
                
        if is_run:
            my.has_set_options = True
                
    def get_select_values(my):
        if not my.has_set_options:
            my.set_dom_options()
        return my.labels, my.values


    def init(my):
        my.add_color("background", "background", 10)
        my.add_color("color", "color")


    def get_display(my):
        class_name = my.kwargs.get('class')
        if class_name:
            my.add_class(class_name)

        if my.is_read_only():
            # don't disable it, just have to look disabled
            my.set_attr('disabled', 'disabled')
            my.add_class('disabled')
        assert my.get_input_name() != None

        my.set_attr("name", my.get_input_name())

        width = my.get_option("width")
        if width:
            my.add_style("width: %s" % width)

        my.add_border()
        #my.add_style("margin: 0px 5px")

        # default select element size to max of 20 ...
        sz = '20'

        # look for a site-wide configuration for SELECT element size ...
        from pyasm.common import Config
        select_element_size = Config.get_value('web_ui','select_element_size')
        if select_element_size:
            sz = select_element_size

        # see if the configuration of this widget specified a SELECT size (local config overrides site-wide) ...
        wdg_config_select_size = my.get_option("select_size")
        if wdg_config_select_size:
            sz = wdg_config_select_size

        # store configured size of SELECT to be used later on the client side to set the
        # SELECT drop down size ...
        my.set_attr('spt_select_size',sz)


        # assign all the labels and values
        if not my.has_set_options:
            my.set_dom_options()

        # get the current value for this element
        current_values = my.get_values(for_display=True)
        #if not current_value and my.has_option("default"):
            #current_value = my.get_option("default")
        # go through each value and set the select options
        selection_found = False
        for i in range(0, len(my.values)):
            if i >= len(my.labels): break
            value = my.values[i]
            label = my.labels[i]
            option = HtmlElement("option")

            # always compare string values.  Not sure if this is a good
            # idea, but it should work for most cases
            if my._is_selected(value, current_values):
                option.set_attr("selected", "selected")
                selection_found = True

            option.set_attr("value", value)
            option.add(label)

            my.add(option)

        # if no valid values are found, then show the current value in red
        show_missing = my.get_option("show_missing")
        if show_missing in ['false', False]:
            show_missing = False
        else:
            show_missing = True

        if show_missing and not selection_found: #and (my.empty_option_flag or my.get_option("empty") != ""):
            option = HtmlElement("option")
            value = my.get_value()
            # this converts potential int to string
            my.values = [Common.process_unicode_string(x) for x in my.values]
            if value and value not in my.values:
                option.add("%s" % value)
                option.set_attr("value", value)
                option.add_style("color", "red")
                option.set_attr("selected", "selected")
                my.add_style("color", "#f44")
                my.add(option)
            

        my.handle_behavior()
        

       
        if not my.label and not my.append_widget:
            if my.kwargs.get("required") in [True, 'true']:
                sel = BaseInputWdg.get_class_display(my)
                wdg = SpanWdg()
                my._add_required(wdg, offset_x=6)
                wdg.add(sel)
                return wdg
            else:
                return super(SelectWdg, my).get_display()
        else:
            sel = BaseInputWdg.get_class_display(my)
            span = SpanWdg(my.label, css=my.css)
            span.add(sel)
            span.add(my.append_widget)
            return span
            


    def _is_selected(my, value, current_values):
        if current_values:

            if not isinstance(value, basestring):
                value = str(value)

            cur_value = current_values[0]
            if not isinstance(cur_value, basestring):
                cur_value = str(cur_value)
            return value == cur_value
        else:
            return False


    def handle_behavior(my):
        # if this interferes with something else, please leave a comment so it can be fixed.. Similar logic is found in FilterCheckboxWdg and FilterTextWdg

        if my.persistence:
            key = my.get_key()
            value = WidgetSettings.get_value_by_key(key)
            if value:
                my.set_value(value)

            behavior = {"type" : "change",
                    "cbjs_preaction":\
                    "spt.api.Utility.save_widget_setting('%s',bvr.src_el.value)"%key}
            if my.change_cbjs_action:
                behavior['cbjs_action'] = my.change_cbjs_action
            my.add_behavior(behavior)


        onchange = my.get_option("onchange")
        if onchange:
            my.add_behavior( {
                'type': 'change',
                'cbjs_action': onchange
            } )
 



class FilterSelectWdg(SelectWdg):
    def __init__(my, name=None, label='', css=None):
        super(FilterSelectWdg,my).__init__(name, label=label, css=css)
        
        my.set_submit_onchange()
        my.set_persistence()
       
    def get_display(my):
        return super(FilterSelectWdg, my).get_display()
      
class ActionSelectWdg(SelectWdg):
    def __init__(my,name=None):
        super(ActionSelectWdg,my).__init__(name)
        my.add_class("action")
       


class MultiSelectWdg(SelectWdg):
    def __init__(my,name=None, label='', css=None):
        super(MultiSelectWdg,my).__init__(name, label=label, css=css)
        my.set_attr("multiple", "1")
        my.set_attr("size", "6")

    def _is_selected(my, value, current_values):
        if not current_values:
            return False
        # if there is only one value, then try and make the assumption that
        # this may be a single string array
        if len(current_values) == 1:
            current_value = current_values[0]
            if current_value.startswith("||") and current_value.endswith("||"):
                current_value = current_value.strip("||")
                current_values = current_value.split("||")


        return value in current_values




class ItemsNavigatorWdg(HtmlElement):
    ''' a navigator that breaks down a long list of items into chunks 
        selected by a drop-down menu '''
    DETAIL = "detail_style"
    LESS_DETAIL = "less_detail_style"

    def __init__(my, label, max_length, step, refresh=True, max_items=100):
        assert isinstance(max_length, int) and step > 0
        if max_length < 0:
            max_length = 0
        my.max_length = max_length
        my.step = step
        my.label = label
        my.show_label = True
        my.style = my.DETAIL
        my.refresh = refresh
        my.refresh_script = ''
        my.select = SelectWdg(my.label)
        my.select.add_color("background-color", "background", -8)
        my.select.add_style("font-size: 0.9em")
        my.select.add_style("margin-top: 3px")
        my.select.set_persist_on_submit()
        my.max_items = max_items
        super(ItemsNavigatorWdg, my).__init__('span')

    def set_style(my, style):
        my.style = style
    
    def set_refresh_script(my, script):
        my.refresh_script = script

    def get_display(my):
        if not my.refresh:
            my.select.add_event('onchange', my.refresh_script)

        list_num = int(my.max_length / my.step)
        value_list = []
        label_list = []

        # set limit
        if list_num > my.max_items:
            past_max = list_num - my.max_items
            list_num = my.max_items 
        else:
            past_max = 0
       
        for x in xrange(list_num):
            value_list.append("%s - %s" %(x* my.step + 1, (x+1) * my.step))

        # handle the last item
        if not past_max:
            if list_num  * my.step + 1 <= my.max_length:
                value_list.append("%s - %s" %(list_num * my.step + 1,\
                    my.max_length ))
        else:
            value_list.append( "+ %s more" % past_max)


        if my.style == my.DETAIL:
            label_list = value_list
        else:
            for x in xrange(list_num):
                label_list.append("Page %s" %(x+1) )
            if list_num  * my.step + 1 <= my.max_length:
                label_list.append("Page %s" % (list_num+1))
           
        my.select.add_empty_option(my.select.SELECT_LABEL, '')
        my.select.set_option("values", value_list)
        my.select.set_option("labels", label_list)
        if my.max_length < my.step:
            my.step = my.max_length
        my.select.set_option("default", "%s - %s" %(1, my.step))

        if my.show_label:
            my.add("%s:" %my.label)

        my.add(my.select)
        return super(ItemsNavigatorWdg, my).get_display() 
   
    def set_display_label(my, visible=True):
        my.show_label = visible
        
    def set_value(my, value):
        my.select.set_value(value)

    def get_value(my):
        return my.select.get_value()



class ButtonWdg(BaseInputWdg):
    def __init__(my,name=None):
        super(ButtonWdg,my).__init__(name,"input")
        #my.add_style("background-color: #f0f0f0")

    def get_display(my):
        my.set_attr("type", "button")
        my.set_attr("name", my.get_input_name())

        value = my.name
        my.set_attr("value",value)
        return super(ButtonWdg,my).get_display()


class SubmitWdg(BaseInputWdg):
    def __init__(my,name=None,value=None):
        super(SubmitWdg,my).__init__(name, "input")
        my.add_style("background-color: #f0f0f0")
        my.value = value

    def get_display(my):
        my.set_attr("type", "submit")
        my.set_attr("name", my.get_input_name())

        if my.value == None:
            my.value = my.name

        my.set_attr("value",my.value)
        return super(SubmitWdg,my).get_display()


class ResetWdg(BaseInputWdg):
    def __init__(my,name=None):
        super(ResetWdg,my).__init__(name, "input")

    def get_display(my):
        my.set_attr("type", "reset")
        my.set_attr("name", my.get_input_name())

        return super(ResetWdg,my).get_display()



class PasswordWdg(BaseInputWdg):
    def __init__(my,name=None):
        super(PasswordWdg,my).__init__(name,"input")
        my.css = "inputfield"
        my.add_class(my.css)
        my.add_class("spt_input")
        my.add_color("background", "background", 10)
        my.add_color("color", "color")
        my.add_style("border: solid 1px %s" % my.get_color("border_color") )
        #my.add_style("width: 200px") 

    def get_display(my):
        my.set_attr("type", "password")
        my.set_attr("name", my.get_input_name())

        my.add_class(my.css)
        return super(PasswordWdg,my).get_display()





class HiddenWdg(BaseInputWdg):
    def __init__(my,name=None, value=''):
        super(HiddenWdg,my).__init__(name,"input")
        my.value = value

    def get_title(my):
        return None

    def get_display(my):
        if my.options.get("value"):
            my.value = my.options.get("value")

        my.set_attr("type", "hidden")
        my.set_attr("name", my.get_input_name())
        my.set_attr("value", my.get_value(for_display=True))

        my.add_class("spt_input")

        return super(HiddenWdg,my).get_display()


class NoneWdg(BaseInputWdg):
    '''An empty widget'''
    def __init__(my,name=None):
        super(NoneWdg,my).__init__(name)

    def get_title(my):
        if my.is_read_only():
            
            return super(NoneWdg, my).get_title()
        else:
            return ''

    def get_display(my):
        if my.is_read_only():
            my.set_attr('readonly', 'readonly')
            my.add(my.get_value())
            return super(NoneWdg, my).get_display() 
        else:
            return ''


class ThumbInputWdg(BaseInputWdg):
    '''Wrapper around the thumb widget, so that it can be display in the
    input form'''
    def __init__(my,name=None):
        super(ThumbInputWdg,my).__init__(name)

    def get_title(my):
        return '&nbsp;'

    def get_display(my):

        sobject = my.get_current_sobject()
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

        from file_wdg import ThumbWdg
        icon = ThumbWdg()
        icon.set_name(column)
        icon.set_show_orig_icon(True)
        icon.set_show_filename(True)
        if my.get_option('latest_icon') == 'true':
            icon.set_show_latest_icon(True)
        icon.set_sobject( my.get_current_sobject() )
        return icon.get_display()



    


class SimpleUploadWdg(BaseInputWdg):
    def __init__(my,name=None):
        super(SimpleUploadWdg,my).__init__(name)

    def get_display(my):
       
        input = HtmlElement.input()
        input.set_attr("type","file")
        input.set_attr("name",my.get_input_name())
        input.add_class("inputfield")
        my.add(input)


        context = my.get_option("context")
        if context == "":
            context = Snapshot.get_default_context()
        context_input = HiddenWdg("%s|context" % my.get_input_name(), context)
        my.add(context_input)


        # override the column
        column = my.get_option("column")
        if column != "":
            column_input = HiddenWdg("%s|column" % my.get_input_name(), column)
            my.add(column_input)

        # create an event that will trigger a copy to handoff
        """
        web = WebContainer.get_web()
        handoff_dir = web.get_client_handoff_dir()
        path_hidden = HiddenWdg("%s|path" % my.get_input_name(), "")
        my.add(path_hidden)
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
        ''' % (handoff_dir, my.get_input_name(), my.get_input_name() ) )
        my.add(script)
        from pyasm.widget import GeneralAppletWdg
        my.add(GeneralAppletWdg())

        event_container = WebContainer.get_event_container()
        event_container.add_listener('sthpw:submit', 'foo()')
        """


        return super(SimpleUploadWdg,my).get_display()





class UploadWdg(BaseInputWdg):
    def __init__(my,name=None):
        super(UploadWdg,my).__init__(name)

    def add_upload(my, table, name, is_required=False):
        span = SpanWdg()
        if is_required:
            my._add_required(span)
        
        table.add_row()
        span.add("File (%s)" %name)
        table.add_cell(span)
        input = HtmlElement.input()
        input.set_attr("type","file")
        input.set_attr("name", my.get_input_name(name))
        input.set_attr("size", "40")
        
        table.add_cell(input)
    

    def get_display(my):

        icon_id = 'upload_div'
        div = DivWdg()

        if my.get_option('upload_type') == 'arbitrary':
            counter = HiddenWdg('upload_counter','0')
            div.add(counter)
            icon = IconButtonWdg('add upload', icon=IconWdg.ADD)
            icon.set_id(icon_id)
            icon.add_event('onclick', "Common.add_upload_input('%s','%s','upload_counter')" \
                %(icon_id, my.get_input_name()))
            div.add(icon)
        
        table = Table()
        table.set_class("minimal")
        table.add_style("font-size: 0.8em")

        names = my.get_option('names')
        required = my.get_option('required')
        if not names:
            my.add_upload(table, my.name)
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
                 my.add_upload(table, name, is_required)

        table.add_row()
        

        context_option = my.get_option('context')
        pipeline_option = my.get_option('pipeline')
        setting_option = my.get_option('setting')
        context_name = "%s|context" % my.get_input_name()
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
            subcontext_name = "%s|subcontext" % my.get_input_name()
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
            sobject = my.sobjects[0]
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
      
        revision_cb = CheckboxWdg('%s|is_revision' %my.get_input_name(),\
            label='is revision', css='med')
        table.add_data(revision_cb)
        table.add_row()
        table.add_cell("Comment")
        textarea = TextAreaWdg("%s|description"% my.get_input_name())
        table.add_cell(textarea)
        div.add(table)

        return div



class MultiUploadWdg(BaseInputWdg):
    UPLOAD_ID = "upload"
    
    def __init__(my,name=None):
        super(MultiUploadWdg,my).__init__(name)


    def get_display(my):

        # put in a default name
        if my.name == None:
            my.name = "upload_files"
       
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
            
            ''' % (my.UPLOAD_ID,my.name) ))
       
        # bind this to the edit button
        event = WebContainer.get_event("sthpw:submit")
        event.add_listener("do_upload()")

        context_url = WebContainer.get_web().get_context_url()
        
        # add the applet
        
        applet = HtmlElement("applet")
        applet.set_attr("code", "upload.UploadApplet")
        applet.set_attr("codebase", "%s/java" % context_url.get_url() )
        applet.set_attr("archive", "Upload-latest.jar")
        applet.set_attr("width", "450")
        applet.set_attr("height", "120")
        applet.set_attr("id", my.UPLOAD_ID)
        
        # create param for applet
        param = HtmlElement("param")
        param.set_attr("name","scriptable")
        param.set_attr("value","true")

        applet.add(param)
        widget.add(applet)
       

        # hidden element which fills in the file names that were
        # uploaded
        hidden = HiddenWdg(my.name)
        hidden.set_attr('id', my.name)
        widget.add(hidden)

        return widget




class DownloadWdg(BaseInputWdg):

    def __init__(my,name=None):
        super(DownloadWdg,my).__init__(name)

    def get_display(my):

        context_url = WebContainer.get_web().get_context_url()

        download_id = "download"

        # create applet
        applet = HtmlElement("applet")
        applet.set_attr("code", "upload.DownloadApplet")
        applet.set_attr("codebase", "%s/java" % context_url.get_url() )
        applet.set_attr("archive", "Upload-latest.jar")
        applet.set_attr("width", "1")
        applet.set_attr("height", "1")
        applet.set_attr("id", download_id)
    
        # create param for applet
        param = HtmlElement("param")
        param.set_attr("name","scriptable")
        param.set_attr("value","true")

        applet.add(param)
        my.add(applet)

        my.do_download()

        return super(DownloadWdg,my).get_display()


    def do_download(my):

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


            my._download_sobject(sobject,sub_dir)

            # for each shot download all of the dependent files
            if search_type.startswith("flash/shot"):
                instances = sobject.get_all_instances()
                for instance in instances:
                    from pyasm.flash import FlashAsset
                    asset = FlashAsset.get_by_code(instance.get_value("asset_code"))

                    asset_sub_dir = "%s/design" % sub_dir

                    my._download_sobject(asset, asset_sub_dir)


    def _download_sobject(my, sobject, sub_dir):

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

            my.add(script)


# DEPRECATED
class CalendarWdg(BaseInputWdg):
    ''' this can be instantiated multiple times in a page'''
    def __init__(my,name=None,id=None):

        my.id = id
        my.cal_options = {}
        my.on_wdg = None
        my.trigger = my.generate_unique_id("f_trigger_c")

        super(CalendarWdg,my).__init__(name,"div")

    def set_cal_option(my, name, value):
        my.cal_options[name] = value

    def set_on_wdg(my, widget):
        my.on_wdg = widget
        my.on_wdg.set_id(my.trigger)
        my.on_wdg.add_class("hand")
        
        

    def class_init(my):
        
        if WebContainer.get_web().is_IE():
            my.add( '''
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

        my.add("<!-- main script for calendar -->")
        my.add("<!-- language for the calendar -->")
        my.add("<!-- the following script defines the Calendar.setup helper function -->")
        script = []
        script.append("var js=new Script()")
        script.append("js.include_once('/context/javascript/jscalendar/calendar.js')")
        script.append("js.include_once('/context/javascript/jscalendar/lang/calendar-en.js')")
        script.append("js.include_once('/context/javascript/jscalendar/calendar-setup.js')")
        init_script = HtmlElement.script(";".join(script))
        init_script.set_attr('mode','dynamic')
        my.add(init_script)


    def get_id(my):
        return my.id

    def get_display(my):
        value = my.get_value(for_display=True)

        if value == "":
            display_date = ""
            #hidden_value = "__NONE__"
            hidden_value = ""
        else:
            date = Date( value )
            display_date = date.get_display_date()
            hidden_value = value

        input_field = None
        if my.id:
            input_field = my.id
        else:
            input_field = my.get_input_name()
        hidden = HiddenWdg(input_field, hidden_value)
        hidden.set_id(input_field)
        my.add(hidden)


        display_area = "%s|display_area" % input_field
        text = SpanWdg()

        text.add( display_date )
        text.add_style("padding: 3px")
        text.set_id(display_area)
        my.add(text)


        #shows_time = "true"
        shows_time = "false"
        da_format = "%b %e, %Y"
        if_format = "%Y-%m-%e %H:%M"

        cal_options_str = ", ".join( [ "%s\t: %s" % (x,my.cal_options[x]) for x in my.cal_options.keys() ] )
        if cal_options_str != "":
            comma = ","
        else:
            comma = ""

        # set a default widget if it hasn't been defined
        if not my.on_wdg:
            img = HtmlElement.img("/context/javascript/jscalendar/img.gif")
            my.set_on_wdg(img)
            my.add(my.on_wdg)



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
        })'''% (cal_options_str, comma, input_field, display_area, if_format, da_format, my.trigger, shows_time))
        script.set_attr('mode', 'dynamic')
        my.add(script)

        return super(CalendarWdg,my).get_display()

  
class CalendarInputWdg(BaseInputWdg):
    ''' this one is the newer version with or without a TextWdg''' 
    def __init__(my, name=None, label=None, css=None, show_week=False):
        my.show_on_wdg = True
        my.show_value = True
        #my.cal_name = my.generate_unique_id()
        my.show_warning = True
        my.onchange_script = ''
        my.hidden = HiddenWdg(name)
        my.show_week = show_week
        my.css = css 
        super(CalendarInputWdg,my).__init__(name, "span", label=label)

    def class_init(my):
        if WebContainer.get_web().is_IE():
            my.add('''
<!-- main calendar program -->
<script type="text/javascript" src="/context/javascript/jscalendar/calendar.js"></script>

<!-- language for the calendar -->
<script type="text/javascript" src="/context/javascript/jscalendar/lang/calendar-en.js"></script>

<script type="text/javascript" src="/context/javascript/TacticCalendar.js"></script>

            ''')
            show_week = "false"
            if my.show_week :#or my.get_option('show_week') == 'true':
                show_week = "true"
            script = HtmlElement.script('''
                var calendar_tactic = new TacticCalendar(%s)
                ''' % (show_week) )
            my.add(script)
            return

        my.add('''
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
        if my.show_week :#or my.get_option('show_week') == 'true':
            show_week = "true"
        script = HtmlElement.script('''
            var calendar_tactic = new TacticCalendar(%s)
            ''' % (show_week) )
        my.add(script)


    
    def get_hidden_wdg(my):
        if my.get_option('show_warning') =='false':
            my.show_warning = False
        value = super(CalendarInputWdg, my).get_value(for_display=True)
         
        if value == "":
            display_date = ""
            hidden_value = ""
        else:
            # In some cases the user is allowed to append chars after it
            date = Date( db_date=value, show_warning=my.show_warning )
            # display date format is not used for now
            # but date is instantiated to issue warning where applicable
            # display_date = date.get_display_date()
            hidden_value = value

        hidden_name = my.get_input_name()
        if my.show_value:
            hidden = TextWdg(hidden_name)
            hidden.set_persist_on_submit()
            hidden.set_attr("size", "15")
            hidden.set_value(hidden_value)
        else:
            hidden = HiddenWdg(hidden_name, hidden_value)

        
        return hidden


    def set_onchange_script(my, script):
        ''' script that runs when the user clicks on a date '''
        my.onchange_script = script

    '''
    def get_value(my):
        return my.hidden.get_value()
    

    def get_js_name(my):
        name = my.cal_name
        return "calendar_%s" % name
    '''

    def get_on_script(my, date=None):
        if not date:
            date = ''
        name = my.get_input_name() 
        script = "calendar_tactic.show_calendar('%s', null,'%s')" % (name, date)
        return script


    def set_show_on_wdg(my, flag):
        my.show_on_wdg = flag

    def set_show_value(my, flag):
        my.show_value = flag

    def set_show_warning(my, show):
        my.show_warning = show

    def get_on_wdg(my):
        widget = HtmlElement.img("/context/javascript/jscalendar/img.gif")
        widget.add_event("onclick", my.get_on_script() )
        widget.add_class("hand")
        return widget

        

    def get_display(my):
        widget = Widget()

        name = my.get_input_name()
        # set a default widget if it hasn't been defined
        if my.show_on_wdg:
            widget.add(my.get_on_wdg() )

        my.hidden = my.get_hidden_wdg() 
        widget.add(my.hidden)

        show_week = "false"
        if my.show_week or my.get_option('show_week') == 'true':
            show_week = "true"
       
        
        # on choosing a date, it executes this js
        if my.onchange_script:
            script = "calendar_tactic.init('%s');\
                calendar_tactic.cal.onClose = function() { if (!calendar_tactic.check('%s')) return; %s }"\
                %(name, name, my.onchange_script)
            from pyasm.web import AppServer
            AppServer.add_onload_script(script)
        my.add(widget)

        if not my.label:
            return super(CalendarInputWdg, my).get_display()
        else:
            sel = BaseInputWdg.get_class_display(my)
            span = SpanWdg(my.label, css=my.css)
            span.add(sel)
            return span




class PopupWdg(BaseInputWdg):

    def __init__(my, name=None, type=None, label=None):
        super(PopupWdg,my).__init__(name,type,label)
        my.title = ''
        my.offset_x = 10
        my.offset_y = 0
        my.is_auto_hide = True

    def set_auto_hide(my, hide):
        my.is_auto_hide = hide

    def get_display(my):

        div = DivWdg(css="popup_wdg")
        div.set_id(my.name)
        hidden_name = '%s_hidden' % my.name
        div.add(HiddenWdg(hidden_name))
        div.add_style("display: none")
        div.add_style("margin", "15px 0 0 0px")
        div.add_style("position", "absolute")

        from web_wdg import CloseWdg
        div.add(CloseWdg(my.get_off_script()))
        div.add( HtmlElement.br(clear="all") )

        for widget in my.widgets:
            div.add(widget)

        div.add( HtmlElement.br(clear="all") )
        return div


  


    def get_on_script(my):
        script = "Common.follow_click(event, '%s', %d, %d); Effects.fade_in('%s', 200);"\
            %(my.get_name(),my.offset_x, my.offset_y, my.get_name()) 
        if my.is_auto_hide:
            script += "Common.overlay_setup('mouseup',function(){%s})" %my.get_off_script()
             
        return script

    def get_off_script(my):
        return "Effects.fade_out('%s', 200); document.removeEvents('mouseup')" % my.get_name()






class PopupMenuWdg(BaseInputWdg):

    def __init__(my,name=None, type=None, label=None, action_name=None, \
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
        
        super(PopupMenuWdg,my).__init__(name,type,label)
        if action_name:
            my.action_name = action_name
        else:
            my.action_name = name
        my.multi = multi
        my.title = ''
        my.offset_x = 10
        my.offset_y = 0
        my.height = height
        my.menu_width = width
        my.monitor = None
        my.is_submit = True
        my.is_auto_hide = True
        # this is the group name
        my.item_name = '%s_item' %my.get_input_name()


    
    def set_auto_hide(my, hide):
        my.is_auto_hide = hide

    def add_monitor(my, widget):
        ''' add a monitor div on the right side'''
        my.monitor = widget

    def add_separator(my):
        widget = "<hr/>"
        super(PopupMenuWdg,my).add(widget)

    def add_title(my, title):
        if isinstance(title, basestring):
            widget = FloatDivWdg("<b>%s</b>" % title)
        else:
            widget = "<b>%s</b>" % title.get_buffer_display()
        
        my.title = widget

        my.title.add_style('border-bottom','1px dotted #ccc')
    
    def add(my, widget, name=None):
        if type(widget) in types.StringTypes:
            tmp = widget
            widget = StringWdg(widget)
            if not name:
                name = tmp
            widget.set_name(name)
        else:
            if name:
                widget.set_name(name)

        super(PopupMenuWdg,my).add(widget,name)


    def set_offset(my, x, y):
        my.offset_x = x
        my.offset_y = y

    def set_submit(my, submit):
        my.is_submit = submit


    def get_display(my):

        div = DivWdg(css="popup_wdg")
        div.set_id(my.name)
        select_name = '%s_hidden' % my.action_name
        if not my.multi:
            hidden = HiddenWdg(select_name)
            hidden.set_id(select_name)
            div.add(hidden)
        """
        hidden_name = '%s_hidden' % my.name
        div.add(HiddenWdg(hidden_name))
        """
        div.add_style("display: none")
        div.add_style("margin", "5px 0 0 0px")
        div.add_style("position", "absolute")

        from web_wdg import CloseWdg
        
        div.add(my.title)
        div.add(CloseWdg(my.get_off_script()))
        div.add(HtmlElement.br())


        content_div = FloatDivWdg()
        if my.height:
            content_div.add_style('height', my.height)
        content_div.add_style('clear', 'left')
        content_div.add_style('padding-top','8px')
        div.add(content_div)



       
        for widget in my.widgets:
            if not widget.get_name():
                item = DivWdg(css='hand')
                item.add(widget)
                if my.menu_width:
                    item.add_style('width', my.menu_width)
                content_div.add(item)
                continue
            id='%s_%s' %(my.get_input_name(), widget.get_name())
            item = DivWdg(css="hand")
            item.set_attr('name', my.item_name)
            item.set_attr('tab', id)
            if my.menu_width:
                item.add_style('width', my.menu_width)
            item.add_style('padding-left','3px')
            
            
            # checkbox and extra logic is added for named widgets only
            if my.multi:
                span = SpanWdg(widget, css='small')
                #checkbox = CheckboxWdg("%s_select" % my.name)
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
            if not my.multi:
                item.add_event("onclick", "el=document.form.elements['%s'];el.value='%s';document.form.submit()" % (select_name,widget.get_name()) )
            else:
                pass

            """
            
            if not my.multi: 
                item.add_event("onclick", "get_elements('%s').tab_me('%s','active_menu_item',\
                'inactive_menu_item'); get_elements('%s').set_value('%s')" \
                % ( my.item_name, id, select_name,widget.get_name()) )
            if my.is_submit:
                 item.add_event("onclick", "document.form.submit()")
            content_div.add(item)

        if my.monitor:
            mon_div = FloatDivWdg(my.monitor, id='%s_monitor' %my.get_input_name(),float='left')
            mon_div.add_style('height', my.height)
            mon_div.add_style('display', 'none')
            mon_div.add_class('monitor')
            div.add(mon_div)
        return div


    def get_on_script(my):

        #script = "Common.follow_click(event, '%s', %d, %d); set_display_on('%s');"\
        #    %(my.get_name(),my.offset_x, my.offset_y, my.get_name())
        script = "Effects.fade_in('%s', 30);"%my.get_name()
        if my.is_auto_hide:
            script += "Common.overlay_setup('mouseup',function(){%s})" %my.get_off_script()
             
        return script

    def get_off_script(my):
        return "Effects.fade_out('%s', 200); document.removeEvents('mouseup')" % my.get_name()

    def get_monitor_on_script(my):
        return "Effects.fade_in('%s_monitor', 50)" % my.get_input_name()

    def get_monitor_off_script(my):
        return "set_display_off('%s_monitor')" % my.get_input_name()


    def get_clear_css_script(my):
        ''' clears the css of the menu buttons, make them inactive'''
        return "$$('div[name=%s]').each(function(elem) {elem.className='inactive_menu_item';})" %my.item_name
