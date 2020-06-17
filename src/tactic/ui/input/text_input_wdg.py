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


__all__ = ['TextInputWdg', 'PasswordInputWdg', 'LookAheadTextInputWdg', 'GlobalSearchWdg']

from pyasm.common import Date, Common, Environment, FormatValue, SPTDate, TacticException
from pyasm.web import Table, DivWdg, SpanWdg, WebContainer, Widget, HtmlElement, Palette
from pyasm.biz import Project, Schema
from pyasm.search import Search, SearchType, SObject, SearchKey
from pyasm.widget import IconWdg, TextWdg, BaseInputWdg, PasswordWdg, HiddenWdg
from tactic.ui.common import BaseRefreshWdg
from pyasm.command import Command

import re, string

import six
basestring = six.string_types



try:
    import numbers
    has_numbers_module = True
except:
    has_numbers_module = False


class TextInputWdg(BaseInputWdg):

   
    ARGS_KEYS = {
    'width': {
        'description': 'width of the text element',
        'type': 'TextWdg',
        'order': 1,
        'category': 'Options'
    },
    'hint_text': {
        'description': 'initial hint text',
        'type': 'TextWdg',
        'order': 3,
        'category': 'Options'
    },
    'required': {
        'description': 'designate this field to have some value',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 4,
        'category': 'Options'
    },
  
    'validation_js': {
        'description': 'an inline validation javascript can be provided',
        'type': 'TextWdg',
        'order': 5,
        'category': 'Options'
    },
    'validation_scheme': {
        'description': 'a built-in validation scheme like INTEGER, NUMERIC, POS_INTEGER be provided',
        'type': 'SelectWdg',
        'values': 'INTEGER|NUMERIC|POS_INTEGER',
        'order': 6,
        'category': 'Options'
    },
    'display_format': {
        'description': 'format key to display the data',
        'type': 'TextWdg',
        'order': 2,
        'category': 'Options'
    }
    }






    def set_value(self, value, set_form_value=False):
        self.text.set_value(value, set_form_value=set_form_value)

    def get_value(self):
        return self.text.get_value()
 
 
    def add_behavior(self, behavior):
        self.text.add_behavior(behavior)
 
 
    def get_text(self):
        return self.text


    def get_input_group_wdg(self):
        
        input_group = DivWdg()
        
        width = self.width
        if width:
            try:
                width = int(width)
                width = str(width) + "px"
                input_group.add_style("width: %s" % width)
            except ValueError:
                pass
        
        height = self.height
        if height:
            try:
                height = int(height)
                height = str(height) + "px"
                input_group.add_style("height: %s" % height)
            except ValueError:
                pass
        
        return input_group

 

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.name = self.kwargs.get("name")
        name = self.name

        self.password = kwargs.get("password")
        if self.password in [True, 'true']:
            self.password = True

        input_type = kwargs.get("type")

        if self.password:
            self.text = PasswordWdg(name)
        elif input_type:
            self.text = TextWdg(name)
            self.text.set_option("type", input_type)
        else:
            self.text = TextWdg(name)

        self.text.set_attr('autocomplete','off')

        align = kwargs.get("align")
        if align:
            self.text.add_style("text-align", align)

        ignore = self.kwargs.get("ignore")
        if ignore in [True, 'true']:
            self.text.remove_class("spt_input")


        class_name = kwargs.get("class")
        if class_name:
            self.text.add_class(class_name)

        self.readonly = kwargs.get("read_only")
        if self.readonly in [True, 'true']:
            self.set_readonly(True)
            bgcolor = self.text.add_color("background", "background", [-10, -10, -10])
        else:
            self.readonly = False
            bgcolor = self.kwargs.get("background") or self.text.get_color("background")
            #self.text.add_style("background", bgcolor)

        self.icon_wdg = SpanWdg()


        self.border_color = self.text.get_color("border")

        self.text.add_class("spt_text_input")
        #self.text.add_style("padding: 4px")


        bgcolor2 = self.text.get_color("background", -10)
        if not self.readonly:

            # TODO: replace with bootstrap error classes
            self.text.add_behavior( {
                'type': 'blur',
                'bgcolor': bgcolor,
                'bgcolor2': bgcolor2,
                'cbjs_action': '''
                if (bvr.src_el.hasClass('spt_input_validation_failed')) {
                    return;
                }

                var value = bvr.src_el.value;
                var last_value = bvr.src_el.getAttribute("spt_last_value");

                bvr.src_el.setAttribute("spt_last_value", value);

                //spt.input.set_success(bvr.src_el);
                if (spt.input.set_error)
                    spt.input.set_error(bvr.src_el);
                '''
                } )


        custom_cbk = self.kwargs.get("custom_cbk")
        if custom_cbk:
            self.text.add_behavior( {
                'type': 'keyup',
                'custom': custom_cbk,
                'cbjs_action': '''
                var key = evt.key;
                var custom;
                try {
                    if (key == 'enter') {
                        var custom = bvr.custom.enter;
                    } else if (key == 'tab') {
                        var custom = bvr.custom.tab;
                    }

                    if (custom) {
                        eval(custom);
                    }
 
                }
                catch(e) {
                }
                '''
            } )


        onblur = self.kwargs.get("onblur")
        if onblur:
            self.text.add_behavior( {
                'type': 'blur',
                'cbjs_action': onblur
            } )
 
       
        self.top = DivWdg()



        height = self.kwargs.get("height")
        if height:
            height = height.replace("px", "")
            height = int(height)
        else:
            height = 35

        self.height = height


        super(TextInputWdg, self).__init__(self.name, "text")


        self.icon = self.kwargs.get("icon")
        self.icon_pos = self.kwargs.get("icon_pos")
        if not self.icon_pos:
            self.icon_pos = "left"
        if self.icon:
            self.icon_div = DivWdg()


        self.width = self.kwargs.get("width")
        if not self.width:
            self.width = None
        else:
            self.width = str(self.width).replace("px", "")
            if not self.width.endswith("%"):
                self.width = int(self.width)
        width = self.width
        
        if width:
            try:
                width = int(width)
                width = str(width) + "px"
            except ValueError:
                pass
            self.text.add_style("width: %s" % width)


    def add_style(self, name, value=None):
        
        if not name:
            return

        if not value:
            name, value = re.split(":\ ?", name)
        
        if name == 'width':
            self.width = value
            self.text.add_style(name, value)
        elif name == 'float':
            self.top.add_style(name, value)
        else:
            self.text.add_style(name, value)


    def add_behavior(self, behavior):
        self.text.add_behavior(behavior)


    def get_icon_wdg(self):
        return self.icon_wdg





    def set_readonly(self, flag=True):
        self.readonly = flag
        self.text.set_attr("readonly", "readonly")

    def add_class(self, class_name):
        self.text.add_class(class_name)

    def add_color(self, name, palette_key, modifier=0, default=None):
        self.text.add_color(name, palette_key, modifier, default)

    def set_attr(self, name, value):
        self.text.set_attr(name, value)

    def set_value(self, value, set_form_value=False):
        self.text.set_value(value, set_form_value=set_form_value)

    def set_name(self, name):
        self.name = name
        self.text.set_name(name)

    def is_datetime_col(self, sobject, name):
        '''get_column_info call datetime as timestamp, which is the time tactic_type'''
        tactic_type = SearchType.get_tactic_type(sobject.get_search_type(), name)
        if tactic_type == 'time':
            return True
        else:
            return False

    def fill_data(self):

        if not self.name:
            self.name = self.kwargs.get("name")
        name = self.get_input_name()
        self.text.set_name(name)
        value = self.kwargs.get("value")
        # value always overrides
        if value:
             self.text.set_value(value)
             return

        # fill in the values
        search_key = self.kwargs.get("search_key")
        
        if search_key and search_key != "None" or self.sobjects:
            if self.sobjects:
                sobject = self.sobjects[0]
            else:
                sobject = Search.get_by_search_key(search_key)

            if sobject:
            # look at the current sobject for the data
                display = ""
                if not sobject.is_insert():
                    column = self.kwargs.get("column")
                    if not column:
                        column = self.name
                    
                    display = sobject.get_value(column, no_exception=True)
                if display and self.is_datetime_col(sobject, column) and not SObject.is_day_column(column):
                    display = SPTDate.convert_to_local(display)
                    
                if isinstance(display, str):
                    # this could be slow, but remove bad characters
                    if not Common.IS_Pv3:
                        display = unicode(display, errors='ignore').encode('utf-8')

                format_str = self.get_option("display_format")
                if format_str:
                    format = FormatValue()
                    display = format.get_format_value( display, format_str )
                self.text.set_value(display)

        default = self.kwargs.get("default")
        if default and not self.text.value:
            self.text.set_value(default)



    def get_display(self):

        self.fill_data()

        top = self.top
        top.add_style("position: relative")
        top.add_class("spt_text_top")
        top.add_class("spt_input_text_top")


        if self.kwargs.get("required") in [True, 'true']:
            required_div = DivWdg("*")
            required_div.add_style("position: absolute")
            required_div.add_style("font-size: 1.0em")
            top.add(required_div)
            required_div.add_color("color", "color", [50, 0, 0])
            required_div.add_style("margin-left: -10px")
            top.add_class("spt_required")

        validation_js = self.kwargs.get("validation_js")
        validation_scheme = self.kwargs.get("validation_scheme")
        if validation_js or validation_scheme:
            from tactic.ui.app import ValidationUtil
            if validation_js:
                v_util = ValidationUtil( js =validation_js  )
           
            elif validation_scheme:
                v_util = ValidationUtil( scheme =validation_scheme  )

            validation_bvr = v_util.get_validation_bvr()
            validation_change_bvr = v_util.get_input_onchange_bvr()
            if validation_bvr:
                self.text.add_behavior(validation_bvr)
                self.text.add_behavior(validation_change_bvr)
        
                #v_div = DivWdg()
                #v_div.add_class("spt_validation_%s" % name)
                #v_div.add_behavior( validation_bvr )

        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            is_admin = True
        else:
            is_admin = False

        search_type = self.kwargs.get("search_type")
        # FIXME: this should only show up if asked
        show_edit = self.kwargs.get("show_edit")
        if show_edit in [True, 'true']:
            show_edit = True
        else:
            show_edit = False

        if show_edit and is_admin and not self.readonly and search_type:
            from pyasm.widget import IconButtonWdg

            edit_div = DivWdg()
            edit_div.add_style("position: absolute")
            edit_div.add_style("font-size: 18px")
            top.add(edit_div)
            edit_div.add_color("color", "color", [50, 0, 0])
            
            width = self.width
            try:
                width = int(width)
                width = str(width) + "px"
            except ValueError:
                pass
            edit_div.add_style("margin-left: %s" % width)

            try:
                search_type_obj = SearchType.get(search_type)
                title = search_type_obj.get_title()
                icon = IconButtonWdg(name="Edit '%s' List" % title, icon=IconWdg.EDIT)
                edit_div.add_behavior( {
                    'type': 'click_up',
                    'search_type': search_type,
                    'cbjs_action': '''
                    var class_name = 'tactic.ui.panel.ViewPanelWdg';
                    var kwargs = {
                        search_type: bvr.search_type,
                        view: 'table'
                    }
                    spt.panel.load_popup("Manage List", class_name, kwargs);
                    '''
                } )



            except Exception as e:
                print("WARNING: ", e)
                icon = IconButtonWdg(name="Error: %s" % str(e), icon=IconWdg.ERROR)

            edit_div.add(icon)



        # BOOTSTRAP
        div = DivWdg()
        top.add(div)
        label = None
        if label:
            div.add_class("form-group")
            label_wdg = HtmlElement.label()
            div.add(label)
            label_wdg.add_class("control-label")
            label_wdg.add_attr("for", "inputSuccess1")
            label_wdg.add(self.name)


        input_group = self.get_input_group_wdg()

        div.add(input_group)
       
        height = self.height
        try:
            height = int(height)
            height = str(height) + "px"
        except ValueError:
            pass
        self.text.add_style("height: %s" % height)

        icon_styles = self.kwargs.get("icon_styles")
        icon_class = self.kwargs.get("icon_class")

        if self.icon and self.icon_pos == "left":
            input_group.add_class("input-group")
            if isinstance(self.icon, basestring):
                if len(self.icon) > 1:
                    icon = IconWdg(title="", icon=self.icon, width=16, opacity=1.0)
                else:
                    icon = self.icon
            else:
                icon = self.icon
            input_group.add(self.icon_wdg)
            self.icon_wdg.add_class("input-group-addon")
            self.icon_wdg.add(icon)
            if icon_styles:
                self.icon_wdg.add_styles(icon_styles)
            if icon_class:
                self.icon_wdg.add_class(icon_class)


        input_group.add(self.text)
        self.text.add_class("spt_text_input_wdg")
        self.text.add_class("form-control")
        self.text.add_style('color', div.get_color('color')) 
        text_class = self.kwargs.get("text_class")
        if text_class:
            self.text.add_class(text_class)

        if self.icon and self.icon_pos == "right":
            input_group.add_class("input-group")
            if isinstance(self.icon, basestring):
                if len(self.icon) > 1:
                    icon = IconWdg(title="", icon=self.icon, width=16, opacity=1.0)
                else:
                    icon = self.icon
            else:
                icon = self.icon
            input_group.add(self.icon_wdg)
            self.icon_wdg.add_class("input-group-addon")
            self.icon_wdg.add(icon)
            if icon_styles:
                self.icon_wdg.add_styles(icon_styles)
            if icon_class:
                self.icon_wdg.add_class(icon_class)

            # Below is added only for collection search icon
            # Adding the same custom_cbk from Collections to icon click_up
            is_collection = self.kwargs.get("is_collection")
            if is_collection:
                custom_cbk = self.kwargs.get("custom_cbk")
                icon.add_behavior( {
                    'type': 'mouseover',
                    'cbjs_action': '''
                    bvr.src_el.setStyle('opacity', 1.0);
                    '''
                } )
                icon.add_behavior( {
                    'type': 'mouseout',
                    'cbjs_action': '''
                    bvr.src_el.setStyle('opacity', 0.6);
                    '''
                } )
                icon.add_behavior( {
                    'type': 'click_up',
                    'cbjs_action': custom_cbk['enter']
                } )
            



        # Bootstrap example hierarchy
        """
        <div class="form-group">
          <label class="control-label" for="inputSuccess1">Test Input</label>
          <input type="text" class="form-control" id="inputSuccess1"/>
        </div>
        """


        # Example validation
        """
        self.text.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
            var value = bvr.src_el.value;
            var el = bvr.src_el.getParent(".form-group");
            if (!el) return;

            if (value == "foo") {
                el.addClass("has-error");
                el.removeClass("has-success");
            }
            else {
                el.addClass("has-success");
                el.removeClass("has-error");
            }
            '''
        } )
        """


        default = self.kwargs.get("value")
        if not default:
            default = self.kwargs.get("default")
        if default:
            self.text.set_value(default)

        if not self.text.value:
            hint_text = self.kwargs.get("hint_text")
            color = self.text.get_color('color')
            # lower the visibility of the hint text according to color of palette
            if color > '#999': 
                # case where background too dark
                new_color = Palette.modify_color(color, -10)
            elif color < '#222':
                # case where background too bright
                new_color = Palette.modify_color(color, 50)
            else: 
                new_color = color
                
            if hint_text:
                if new_color:
                    from pyasm.web import HtmlElement
                    style = HtmlElement.style()
                    top.add(style)
                    style.add('''
                        ::-webkit-input-placeholder {
                            color: %s !important;
                        }

                        ::-moz-placeholder {
                            color: %s !important;
                        }

                        /* firefox 19+ */
                        :-ms-input-placeholder {
                            color: %s !important;
                        }

                        /* ie */
                        input:-moz-placeholder {
                            color: %s !important;
                        }

                    ''' % (new_color,new_color,new_color,new_color))

                self.text.add_attr('placeholder', hint_text)

        if not self.readonly:
            # DISABLE for now
            pass
            """
            icon_wdg = DivWdg()
            self.text.add(icon_wdg)
            #icon_wdg.add_style("top: 0px")
            icon_wdg.add_style("float: right")
            icon_wdg.add_style("position: relative")



            icon = IconWdg("Clear", "FA_TIMES", opacity=0.3)
            icon.add_class("spt_icon_inactive")
            icon.add_styles("margin: auto; position: absolute;top: 0;bottom: 8; right: 0; max-height: 100%")
            icon_wdg.add(icon)
            #icon = IconButtonWdg("Remove Tab", IconWdg.CLOSE_ACTIVE)
            icon = IconWdg("Clear", "FA_TIMES")
            icon.add_class("spt_icon_active")
            icon.add_style("display: none")
            icon.add_styles("margin: auto; position: absolute;top: 0;bottom: 8; right: 0; max-height: 100%")
            icon_wdg.add(icon)

            icon_wdg.add_behavior( {
            'type': 'hover',
            'cbjs_action_over': '''
            var inactive = bvr.src_el.getElement(".spt_icon_inactive");
            var active = bvr.src_el.getElement(".spt_icon_active");
            spt.show(active);
            spt.hide(inactive);
            ''',
            'cbjs_action_out': '''
            var inactive = bvr.src_el.getElement(".spt_icon_inactive");
            var active = bvr.src_el.getElement(".spt_icon_active");
            spt.show(inactive);
            spt.hide(active);
            '''
            })

            if self.password:
                input_type ='password'
            else:
                input_type = 'text'
            icon.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_text_top");
                var text = top.getElement("input[type=%s].spt_input");
                text.value = '';
                var hidden = top.getElement("input[type=hidden].spt_input");
                if (hidden) {
                    hidden.value = '';
                    if (spt.has_class(text, 'spt_invalid')) {
                        text.removeClass("spt_invalid");
                        text.setStyle('background','white');
                    }
                }
                var bvr2 = {src_el: text};
                spt.validation.onchange_cbk(evt, bvr2);
                '''%input_type
            } )
            """
        return top



class PasswordInputWdg(TextInputWdg):
    def __init__(self, **kwargs):
        kwargs['password'] = True
        super(PasswordInputWdg, self).__init__(**kwargs)


    def set_value(self, value, set_form_value=False):
        '''Password handles the value like an attr'''
        self.text.set_attr('value', value)




class LookAheadTextInputWdg(TextInputWdg):

    RESULT_SELECT_EVENT = 'lookahead'

    ARGS_KEYS = TextInputWdg.ARGS_KEYS.copy()
    ARGS_KEYS.update({
        'validate': {
            'description': 'whether to activate the validate action, which defaults to true with value_column set',
            'type': 'SelectWdg',
            'order': 10,
            'values': 'true|false',
            'category': 'Options'
        },
        'results_class_name': {
            'description': 'widget used to draw results from look ahead.',
            'type': 'TextWdg',
            'order': 11,
            'default': 'tactic.ui.input.TextInputResultsWdg',
            'category': 'Options'

        },
        'search_type': {
            'description': 'search type used in search to draw results',
            'type': 'TextWdg',
            'order': 12,
            'category': 'Options'
        },
        'value_column': {
            'description': 'column used as input value',
            'type': 'TextWdg',
            'order': 13,
            'category': 'Options'
        },
        'column': {
            'description': 'column used as input label and results label',
            'type': 'TextWdg',
            'order': 14,
            'category': 'Options'
        },
        'do_search': { 
            'description': 'when true, the resutls widget will use search to create results.',
            'type': 'SelectWdg',
            'values': 'true|false',
            'default': 'true',
            'order': 15,
            'category': 'Options'
        },
        'script_path': {
            'description': 'when do_search is false, override results using custom Python script. \
                    Script should return either list of values, or tuple of values and labels.',
            'type': 'TextWdg',
            'order': 16,
            'category': 'Options'
        }
    })
    

    def set_name(self, name):
        self.name = name
        self.text.set_name(name)
        self.hidden.set_name(name)


    def set_hidden_value(self, value, set_form_value=False):
        self.hidden.set_value(value, set_form_value=set_form_value)


    def get_styles(self):

        styles = HtmlElement.style("")

        return styles



    def init(self):


        self.text.add_attr("autocomplete", "off")

        self.search_type = self.kwargs.get("search_type")
        filter_search_type = self.kwargs.get("filter_search_type")

        event_name = ''
        if filter_search_type:
            base_st = SearchKey.extract_base_search_type(filter_search_type)
            event_name = '%s|%s'%(self.RESULT_SELECT_EVENT, base_st) 

        if not self.search_type:
            self.search_type = 'sthpw/sobject_list'
        column = self.kwargs.get("column")
        relevant = self.kwargs.get("relevant")
        
        if not column:
            column = 'keywords'
    
        case_sensitive  = self.kwargs.get("case_sensitive") in ['true',True]

        value_column = self.kwargs.get("value_column")
        validate = self.kwargs.get("validate") in ['true', None]
        if not validate:
            self.top.add_class('spt_no_validate')
        
        do_search = self.kwargs.get("do_search")
        if not do_search:
            do_search = 'true'

        results_on_blur = self.kwargs.get("results_on_blur")
        if not results_on_blur:
            results_on_blur = "none"

        neglect_label_value = self.kwargs.get("neglect_label_value")
        if neglect_label_value:
            self.text.add_behavior({
                'type': 'load',
                'cbjs_action': '''

                bvr.src_el.removeClass("spt_input");

                '''
                })

        self.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
spt.text_input = {}

spt.text_input.is_on = false;
spt.text_input.index = -1;
spt.text_input.last_index = 0;
spt.text_input.run_client_trigger = function(bvr, event_name, display, value) {
    try {
        var e_name = event_name;
        if (e_name) {
            bvr.options = {'value': value, 'display': display};
            spt.named_events.fire_event(e_name, bvr);
        }
    }
    catch(e) {
        spt.alert("Error firing event: " + e_name);
    }
}
    
// async validate when value_column is defined
spt.text_input.async_validate = function(src_el, search_type, column, display_value, value_column, value, kwargs) {
    if (!display_value) 
        return;
    if (!kwargs)  kwargs = {};
    
    if (kwargs.do_search == false){
        bvr2 = {};
        bvr2.src_el = src_el;
        spt.text_input.run_client_trigger(bvr2, kwargs.event_name, display_value, kwargs.hidden_value);
        return;
    }
    var cbk = function(data) {
        var top = src_el.getParent(".spt_input_text_top");
        var hidden_el = top.getElement(".spt_text_value");

        if (!data && data != 0) {
            hidden_el.value = '';
            if (kwargs.validate != false) {
                //src_el.setStyle("background", "#A99");
                src_el.addClass("spt_invalid");
            } else {
                src_el.value = '';
            }
        }
        else {
            // This should not attempt to "correct" the data
            src_el.removeClass("spt_invalid");
            hidden_el.value = data;
        }

       // run client trigger
       spt.text_input.run_client_trigger(bvr, kwargs.event_name, src_el.value, data);

    }
    // can support having pure ' or " in the value, not mixed
    if (display_value.test(/"/) && display_value.test(/'/)) {
        spt.alert("Validation of a mix of ' and \\" is not supported");
        return;
    }

/*
    if (display_value.test(/"/))
        value_expr = "'" + display_value + "'";
    else
        value_expr = '"' + display_value + '"';
*/
    value_expr = display_value;
       

    if (value) {
        var expr = "@GET(" +search_type+ "['" +value_column+ "','" +value+ "'].code)";
    }
    else {
        var expr = "@GET(" +search_type+ "['" +column+ "','" +value_expr+ "'].code)";
    }
    var kw = {
        single: true,
        cbjs_action: cbk
    };
    
    //TODO: support other kinds of eval for validation
    var server = TacticServerStub.get();
    try {
        server.eval(expr, kw);
    } catch(e) {
        log.critical(spt.exception.handler(e));
        return;
    }
    
    
};
            '''
        } )
        if not self.readonly:
            self.text.add_behavior( {
            'type': 'blur',
            'search_type': self.search_type,
            'column': column,
            'value_column': value_column,
            'event_name': event_name,
            'validate': str(validate),
            'do_search': do_search,
            'results_on_blur': results_on_blur,
            'cbjs_action': '''
         
            var validate = bvr.validate == 'True';
            var do_search = bvr.do_search == 'true';
            var top = bvr.src_el.getParent(".spt_input_text_top");
            var el = top.getElement(".spt_input_text_results");
            el.setStyle("display", bvr.results_on_blur);

            spt.text_input.last_index = 0;
            spt.text_input.index = -1;

            var hidden_el = top.getElement(".spt_text_value");
            if (bvr.src_el.value) {
                var display_value = bvr.src_el.value;
                var value = hidden_el.value;

                if (bvr.value_column) {
                    var kwargs = {'validate': validate, 'do_search': do_search, 'event_name': bvr.event_name, 'hidden_value': hidden_el.value};
                    spt.text_input.async_validate(bvr.src_el, bvr.search_type, bvr.column, display_value, bvr.value_column, value, kwargs);
                } else {
                    hidden_el.value = display_value;
                }
            } else {
                hidden_el.value ='';
            }

            '''
            })



        self.hidden = HiddenWdg(self.name)
        self.top.add(self.hidden)
        self.hidden.add_class("spt_text_value")

        multiple_hidden = self.kwargs.get("multiple_hidden")
        if multiple_hidden:
            self.hidden.add_attr("spt_is_multiple", "true")


        class_name = self.kwargs.get("class")
        if class_name:
            self.hidden.add_class("%s" % class_name)
            self.hidden.add_class("%s_value" % class_name)



        if self.readonly:
            return

        results_class_name = self.kwargs.get("results_class_name")
        if not results_class_name:
            results_class_name = 'tactic.ui.input.TextInputResultsWdg';


        highlight = self.kwargs.get("highlight") or ""
        highlight_color = self.kwargs.get("highlight_color") or ""

        custom_cbk = self.kwargs.get("custom_cbk")
        if not custom_cbk:
            custom_cbk = {}

        on_search_complete = self.kwargs.get("on_search_complete") or ""

       
        """
        if not custom_cbk.get('enter'):
            # this is an example used for the Project startup page and already added there
            custom_cbk['enter'] = '''
                var top = bvr.src_el.getParent(".spt_main_top");
                var search_el = top.getElement(".spt_main_search");
                var keywords = search_el.value;
               

                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    'search_type': '%s',
                    'filter_search_type': '%s',
                    'view': 'table',
                    'keywords': keywords,
                    'simple_search_view': 'simple_search',
                    //'show_shelf': false,
                }
                spt.tab.set_main_body_tab();
                spt.tab.add_new("Search", "Search", class_name, kwargs);
            ''' % (self.search_type, filter_search_type)
        """
 
        mode = self.kwargs.get("mode")
        keyword_mode = self.kwargs.get("keyword_mode")

        filters = self.kwargs.get("filters")
        script_path = self.kwargs.get("script_path")
        bgcolor = self.text.get_color("background3")

        postaction = self.kwargs.get("postaction")
        if not postaction:
            postaction = self.get_postaction()

        default_show = self.kwargs.get("default_show")
       

        self.top.add_relay_behavior( {
            'type': 'keyup',
            'bvr_match_class': "spt_text_input",
            'custom': custom_cbk,
            'do_search': do_search,
            'search_type': self.search_type,
            'filter_search_type': filter_search_type,
            'script_path': script_path,
            'filters': filters,
            'column': column,
            'mode': mode,
            'keyword_mode': keyword_mode,
            'relevant': relevant,
            'case_sensitive': case_sensitive,
            'value_column': value_column,
            'results_class_name': results_class_name,
            'highlight': highlight,
            'highlight_color': highlight_color,
            'bg_color': bgcolor,
            'postaction': postaction,
            'default_show': default_show,
            'on_search_complete': on_search_complete,
            'cbjs_action': '''
            var key = evt.key;
            try {
                if (key == 'down') {
                    var top = bvr.src_el.getParent(".spt_input_text_top");
                    var els = top.getElements(".spt_input_text_result");
                    spt.text_input.last_index = spt.text_input.index;
                    spt.text_input.index += 1;
                    // index is redundant, just to make variable shorter
                    var index = spt.text_input.index;
                    // rewind
                    if (index == els.length) {
                        spt.text_input.index = 0;
                        index = 0;
                    }
                    if (spt.text_input.last_index > -1 && els)
                        els[spt.text_input.last_index].setStyle('background','');
                    if (els && els.length > 0 && index > -1)
                        els[index].setStyle('background',bvr.bg_color);
                    return;
                }
                else if (key == 'up') {
                    var top = bvr.src_el.getParent(".spt_input_text_top");
                    var els = top.getElements(".spt_input_text_result");
                    spt.text_input.last_index = spt.text_input.index;
                    spt.text_input.index -= 1;
                    var index = spt.text_input.index;
                    if (index < 0) {
                        index = els.length - 1;
                        spt.text_input.index = index;
                    }
                   
                    if (0 <= spt.text_input.last_index && spt.text_input.last_index <= els.length-1) {
                        els[spt.text_input.last_index].setStyle('background','');
                    }
                    if (els && index > -1 ) 
                        els[index].setStyle('background',bvr.bg_color);
                    return;
                }
                else if (key == 'enter' || key =='tab') {
                    var top = bvr.src_el.getParent(".spt_input_text_top");
                    var els = top.getElements(".spt_input_text_result");
                    if (els && spt.text_input.index > -1) {
                        var el = els[spt.text_input.index];
                        if (el) {
                            var display = el.getAttribute('spt_display');
                            display = JSON.parse(display);

                            if (!display)
                                display = bvr.src_el.getAttribute("spt_label");

                            var value =  el.getAttribute('spt_value');
                            if (!display) {
                                display = value;
                            }
                            bvr.src_el.value = display;
                            var hidden = top.getElement(".spt_text_value");
                            hidden.value = value;
                        }
                    }
                    if (key == 'enter') {
                        var custom = bvr.custom.enter;
                    } else {
                        var custom = bvr.custom.tab;
                    }

                    if (custom) {
                        eval(custom);
                    }
                    var res_top = top.getElement(".spt_input_text_results");
                    spt.hide(res_top);
                   
                    //reset
                    spt.text_input.last_index = spt.text_input.index = -1;

                    return;
                }
                else if (key == 'esc') {
                    var top = bvr.src_el.getParent(".spt_input_text_top");
                    var res_top = top.getElement(".spt_input_text_results");
                    spt.hide(res_top);
                    return;
                }
                else if (key == 'backspace') {
                   //reset
                   spt.text_input.last_index = spt.text_input.index = -1;
                }
                else if (key == 'left'|| key == 'right') {
                   //reset
                   spt.text_input.last_index = spt.text_input.index = -1;
                   return;
                }
            }
            catch(e) {
                spt.text_input.last_index = -1;
                spt.text_input.index = 0;
            }

            var value = bvr.src_el.value;
            if (value == '' && !bvr.default_show) {
                return;
            }

            var class_name = bvr.results_class_name;

            var cbk = function(html) {
                var top = bvr.src_el.getParent(".spt_input_text_top");
                var el = top.getElement(".spt_input_text_results");
                el.setStyle("display", "");
                //el.innerHTML = html;
                spt.behavior.replace_inner_html(el, html);

                spt.text_input.is_on = false;

                if (bvr.postaction) {
                    postaction_cbk = function(el) {
                        eval(bvr.postaction);
                    }
                    postaction_cbk(el);
                }
            }
            var kwargs = {
                args: {
                    search_type: bvr.search_type,
                    filter_search_type: bvr.filter_search_type,
                    filters: bvr.filters,
                    column: bvr.column,
                    value_column: bvr.value_column,
                    relevant: bvr.relevant,
                    script_path: bvr.script_path,
                    do_search: bvr.do_search,
                    case_sensitive: bvr.case_sensitive,
                    value: value,
                    mode: bvr.mode,
                    keyword_mode: bvr.keyword_mode,
                    highlight: bvr.highlight,
                    highlight_color: bvr.highlight_color,
                    on_complete: bvr.on_search_complete
                },
                cbjs_action: cbk,
            }

            var server = TacticServerStub.get();
            if (spt.text_input.is_on == false) {
                spt.text_input.is_on = true;
                server.async_get_widget(class_name, kwargs);
            }
            '''
        } )

        if default_show:
            self.top.add_behavior({
                'type': 'load',
                'custom': custom_cbk,
                'do_search': do_search,
                'search_type': self.search_type,
                'filter_search_type': filter_search_type,
                'script_path': script_path,
                'filters': filters,
                'column': column,
                'mode': mode,
                'keyword_mode': keyword_mode,
                'relevant': relevant,
                'case_sensitive': case_sensitive,
                'value_column': value_column,
                'results_class_name': results_class_name,
                'highlight': highlight,
                'highlight_color': highlight_color,
                'bg_color': bgcolor,
                'postaction': postaction,
                'cbjs_action': '''

                var class_name = bvr.results_class_name;

                var cbk = function(html) {
                    var el = bvr.src_el.getElement(".spt_input_text_results");
                    //el.innerHTML = html;
                    spt.behavior.replace_inner_html(el, html);

                    if (bvr.postaction) {
                       postaction_cbk = function(el) {
                           eval(bvr.postaction);
                       }
                       postaction_cbk(el);
                    }
                }
                var kwargs = {
                    args: {
                        search_type: bvr.search_type,
                        filter_search_type: bvr.filter_search_type,
                        filters: bvr.filters,
                        column: bvr.column,
                        value_column: bvr.value_column,
                        relevant: bvr.relevant,
                        script_path: bvr.script_path,
                        do_search: bvr.do_search,
                        case_sensitive: bvr.case_sensitive,
                        value: "",
                        mode: bvr.mode,
                        keyword_mode: bvr.keyword_mode,
                        highlight: bvr.highlight,
                        highlight_color: bvr.highlight_color
                    },
                    cbjs_action: cbk,
                }

                var server = TacticServerStub.get();
                server.async_get_widget(class_name, kwargs);
                '''
                })



        results_div = self.get_results_div()
        self.top.add(results_div)

        
        exp = "@SOBJECT(config/client_trigger['event','%s'])" %event_name 
        client_triggers = Search.eval(exp)
        for client_trigger in client_triggers:
            results_div.add_behavior( {
                'type': 'listen',
                'unique' : True,
                'event_name': event_name,
                'script_path': client_trigger.get_value('callback'),
                'cbjs_action': '''

                var input = bvr.firing_data;
                input.firing_element = bvr.firing_element; 
                // 2nd arg is the args for this script
                spt.CustomProject.run_script_by_path(bvr.script_path, input);
                '''
                })

        self.top.add(self.get_styles())


    def get_results_div(self):

        results_div = DivWdg()
        results_div.add_style("display: none")
        results_div.add_style("position: absolute")
        #results_div.add_style("top: 25px")
        results_div.add_style("top: %spx" % (self.height))
        results_div.add_style("left: 0px")
        results_div.add_color("background", "background")
        results_div.add_color("color", "color")
        results_div.add_style("padding: 5px 10px 10px 5px")
        results_div.add_style("min-width: 220px")
        results_div.add_style("z-index: 1000")
        results_div.add_style("font-size: 14px")
        results_div.add_border()
        results_div.set_box_shadow()
        results_div.add_class("spt_input_text_results")

        bgcolor = results_div.get_color("background3")
        results_div.add_relay_behavior( {
            'type': "mouseover",
            'bgcolor': bgcolor,
            'bvr_match_class': 'spt_input_text_result',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.bgcolor);
            '''
        } )
        results_div.add_relay_behavior( {
            'type': "mouseout",
            'bvr_match_class': 'spt_input_text_result',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "");
            '''
        } )

        # default event order is mousedown>blur>mouseup
        # we don't want a blur preceding mouseup
        results_div.add_relay_behavior( {
            'type': "mousedown",
            'bvr_match_class': 'spt_input_text_result',
            'cbjs_action': '''
            evt.preventDefault();
            '''
        } )

        # this is when the user clicks on a result item
        # it doesn't do a search right away, it fires the lookahead|<sType> event
        results_div.add_relay_behavior( {
            'type': "mouseup",
            'bvr_match_class': 'spt_input_text_result',
            'cbjs_action': '''
            var display = bvr.src_el.getAttribute("spt_display");
            display = JSON.parse(display);

            if (!display)
                display = bvr.src_el.getAttribute("spt_label");

            var value = bvr.src_el.getAttribute("spt_value");
            if (!display) {
                display = value;
            }

            var top = bvr.src_el.getParent(".spt_input_text_top");
            var el = top.getElement(".spt_input_text_results");
            el.setStyle("display", "none");

            var text_el = top.getElement(".spt_text_input");
            text_el.value = display;
            var hidden_el = top.getElement(".spt_text_value");
            hidden_el.value = value


            '''
        } )

        return results_div


    def fill_data(self):

        default = self.kwargs.get("default")

        # have to set the name with prefix if applicable
        name = self.get_input_name()
        if name:
            self.text.set_name(name)
            self.hidden.set_name(name)

        # fill in the values
        search_key = self.kwargs.get("search_key")
        value_key = self.kwargs.get("value_key")

        current_value_column = self.kwargs.get("current_value_column")
        if not current_value_column:
            current_value_column = self.name



        if value_key:
            column = self.kwargs.get("column")
            column_expr = self.kwargs.get("column_expr")
            value_column = self.kwargs.get("value_column")

            sobject = Search.get_by_search_key(value_key)

            if sobject:
                display = sobject.get_value(column)
                value = sobject.get_value(value_column, auto_convert=False)

                
                self.text.set_value(display)
                if value != None:
                    self.hidden.set_value(value)


        elif search_key and search_key != "None":
            sobject = Search.get_by_search_key(search_key)
            if sobject:

                column = self.kwargs.get("column")
                column_expr = self.kwargs.get("column_expr")
                value_column = self.kwargs.get("value_column")

                #expression = "@SOBJECT(%s)" % self.search_type
                #related = Search.eval(expression, sobject)

                related = None

                # assume a simple relationship
                value = sobject.get_value(current_value_column, auto_convert=False)
                if value not in ['', None] and value_column:
                    if value_column == "id":
                        related = Search.get_by_id(self.search_type, value)
                    else:
                        search = Search(self.search_type)
                        search.add_filter(value_column, value)
                        related = search.get_sobject()

                if related:
                    value = related.get_value(value_column,  auto_convert=False)
                    if column_expr:
                        display = Search.eval(column_expr, related, single=True)
                    else:
                        display = related.get_value(column)
                    
                    if value in ['', None]:
                        value = display

                    # a related value should never display 0??
                    value = value or ""
                else:
                    display = value

                display = display or "" 
              
                self.text.set_value(display)
                if value != None:
                    self.hidden.set_value(value)

    # postaction script runs after the result wdg is loaded
    def get_postaction(self):
        return ""



__all__.append("TextInputResultsWdg")
class TextInputResultsWdg(BaseRefreshWdg):

    # search LIMIT, even if we display only 10, the right balance is to set a limit to 80 to get more diverse results back
    DISPLAY_LENGTH = 35

    def is_number(self, value):
        if has_numbers_module:
            return isinstance(value, numbers.Number)
        else:
            return isinstance(value, int) or isinstance(value, long) or isinstance(value, float) 

    def get_limit(self):
        return 80

    def init(self):
        self.do_search = True
        if self.kwargs.get('do_search') == 'false':
            self.do_search = False
        

    def draw_result(self, top, value):
        # assuming it's a list
        results = self.kwargs.get('results')
        if not results:
            script_path = self.kwargs.get('script_path')
            if not script_path:
                return
            try:
                from tactic.command import PythonCmd
                kwargs = {'value' : value}
                cmd = PythonCmd(script_path=script_path, **kwargs)
                results = cmd.execute()
        
            except Exception as e:
                print(e)
                raise

            else:

                # expect it to return a tuple of 2 lists or a single list
                if isinstance(results, tuple):
                    display_results = results[0]
                    value_results = results[1]
                elif isinstance(results, list):
                    display_results = value_results = results
            if not display_results:
                return

            if len(display_results) != len(value_results):
                raise TacticException("The length of value list and display list needs to match in [%s]" %script_path)

        for idx, keywords in enumerate(display_results):
            div = self.get_result_wdg(keywords)
            top.add(div)
            value = value_results[idx]
            div.add_attr("spt_value", value)

            # turn off cache to prevent ascii error
            keywords = HtmlElement.get_json_string(keywords, use_cache=False)
            div.add_attr("spt_display", keywords)


    def get_result_wdg(self, keywords):
        div = DivWdg()
        div.add_style("padding: 3px")
        div.add_class("spt_input_text_result")

        if not Common.IS_Pv3 and isinstance(keywords, str):
            keywords = unicode(keywords, errors='ignore')

        max_display_length = self.DISPLAY_LENGTH
        if isinstance(keywords, basestring) and  len(keywords) > max_display_length:
            display = "%s..." % keywords[:max_display_length-3]
        else:
            display = keywords
        div.add(display)

        return div


    def get_icon_result_wdg(self, results, values, labels):
        from tactic.ui.panel import ThumbWdg2

        top = DivWdg()
        top.add_style("font-size: 14px")
        top.add_style("width: 300px")
        top.add_style("margin: 3px 0px")
        top.add_style("padding: 0px 0px")

        first_column = self.kwargs.get("value_column")
        if not first_column:
            first_column = self.kwargs.get("column")

        if first_column == "name":
            second_column = "code"
        elif first_column == "code":
            second_column = "name"
        else:
            second_column = "code"

        # display only the first 8 (arbitrary)
        results = results[:8]

        for i, result in enumerate(results):
            div = DivWdg()
            top.add(div)
            div.add_style("padding: 3px 3px")
            div.add_style("height: 45px")

            thumb = ThumbWdg2()
            thumb.set_sobject(result)
            thumb.add_style("height: 40px")
            thumb.add_style("max-width: 45px")
            thumb.add_style("margin-right: 5px")
            thumb.add_style("display: inline-block")
            thumb.add_style("vertical-align: middle")
            div.add(thumb)

            display = labels[i]

            info_div = DivWdg()
            div.add(info_div)
            info_div.add(display)
            info_div.add_style("display: inline-block")
            info_div.add_style("overflow-x: hidden")
            info_div.add_style("text-overflow: ellipsis")
            info_div.add_style("white-space: nowrap")
            #info_div.add_style("width: 250px")
            info_div.add_style("vertical-align: middle")
            info_div.add_style("max-width: 225px")


            second_value = result.get_value("title", no_exception=True)
            if not second_value:
                second_value = result.get_value(second_column)

            #second_value = result.get_value(second_column)
            if second_value == display:
                pass
            elif second_value:
                info_div.add("<br/>")
                info_div.add("<span style='opacity: 0.5; font-size: 10px;'>%s</span>" % second_value)


            div.add_class("spt_input_text_result")
            # turn off cache to prevent ascii error
            display = HtmlElement.get_json_string(display, use_cache=False)

            div.add_attr("spt_display", display)
            div.add_attr("spt_value", values[i])

            if result != results[-1]:
                top.add("<hr style='margin: 0px; padding: 0px'/>")


        if not results:
            div = DivWdg()
            div.add("-- no results --")
            div.add_style("opacity: 0.5")
            div.add_style("font-style: italic")
            div.add_style("text-align: center")
            top.add(div)

        return top




    def get_results_wdg(self, results, values, labels):
        top = DivWdg()

        for i, result in enumerate(results):
            display = labels[i]
            div = self.get_result_wdg(display)
            div.add_attr("spt_value", values[i])
            div.add_attr("spt_label", labels[i])
            top.add(div)
        if not results:
            div = DivWdg()
            div.add("-- no results --")
            div.add_style("opacity: 0.5")
            div.add_style("font-style: italic")
            div.add_style("text-align: center")
            top.add(div)
        return top


    def get_display(self):
        top = self.top
        orig_value = self.kwargs.get("value")
        case_sensitive = self.kwargs.get("case_sensitive") in ['true',True]
        highlight = self.kwargs.get("highlight")
        highlight_color = self.kwargs.get("highlight_color") or "yellow"

        if not self.do_search:
            self.draw_result(top, orig_value)
            return top

        if not case_sensitive:
            orig_value = orig_value.lower()

        on_complete = self.kwargs.get("on_complete") or ""
        top.add_behavior({
            'type': 'load',
            'cbjs_action': on_complete
            })

        # can only support 1 right now
        relevant = self.kwargs.get("relevant") == 'true'
        connected_col = None
        rel_values = []

        if orig_value.endswith(" "):
            last_word_complete = True
        else:
            last_word_complete = False

        # TODO: rename this as top_sType
        search_type = self.kwargs.get("search_type")
        filter_search_type = self.kwargs.get("filter_search_type")
        filters = self.kwargs.get("filters")
        
        column = self.kwargs.get("column")
        value_column = self.kwargs.get("value_column")
        keyword_mode = self.kwargs.get("keyword_mode") or "startswith"

        if not search_type:
            search_type = "sthpw/sobject_list"
        if not column:
            column = "keywords"


        if isinstance(column, basestring):
            columns = column.split(",")
        else:
            columns = column


        value = orig_value.strip()

        # TODO:  This may apply to normal keyword search as well. to treat the whole phrase as 1 word
        if value_column and value.find(' ') != -1:
            values = [value]
        elif keyword_mode == "contains":
            values = Common.extract_keywords(value, lower=not case_sensitive)
        else:
            values = value.split(" ")


        # reverse so the auto suggestion list the items in the same order as they are typed in
        values.reverse()

        project_code = Project.get_project_code()

        # group the columns by sTypes
        search_dict = {}
        for col in columns:
            if col.find('.') != -1:
                parts = col.split(".")
                column = parts[-1]
                tmp_search_types = parts[:-1]
                tmp_search_type = tmp_search_types[-1]
                info_dict = search_dict.get(tmp_search_type)
                if info_dict:
                    col_list = info_dict.get('col_list')
                    col_list.append(col)
                else:
                    col_list = [col]
                    search_dict[tmp_search_type] = {'col_list': col_list}

            else:
                info_dict = search_dict.get(search_type)
                if info_dict:
                    col_list = info_dict.get('col_list')
                    col_list.append(col)
                else:
                    col_list = [col]
                    search_dict[search_type] = {'col_list': col_list}

      

        result_list = []

        top_sType = self.kwargs.get("search_type")
        top_sType = Project.extract_base_search_type(top_sType)
        schema = Schema.get()

        for search_type, info_dict in search_dict.items():
            search = Search(search_type)

            # relevant is ON, then only search for stuff that is relevant in the current table
           

            if search_type == 'sthpw/sobject_list':
                search.add_filter("project_code", project_code)

            if search_type == 'sthpw/sobject_list' and filter_search_type and filter_search_type != 'None' and filter_search_type != 'sthpw/sobject_list':
                search.add_filter("search_type", filter_search_type)

            if filters:
                if isinstance(filters, basestring):
                    import json
                    search.add_op_filters(json.loads(filters))
                else:
                    search.add_op_filters(filters)
            search.add_op("begin")

            search_type_obj = SearchType.get(search_type)
            #column_info = SearchType.get_column_info(search_type)
            col_list = info_dict.get('col_list')

            if relevant:
                plain_search_type = Project.extract_base_search_type(search_type)
                from_col = None
                to_col = None
                try:
                    #TODO: add path kwarg derived from expression here
                    from_col, to_col = schema.get_foreign_keys(plain_search_type, top_sType)
                
                except TacticException:
                    pass
                if from_col:
                    # While this can support multi sTypes, should use it for 1 sType for similipicity for now
                    rel_search = Search(top_sType)
                    rel_search.add_column(from_col)
                    rel_search.add_group_by(from_col)
                    rel_sobjs = rel_search.get_sobjects()
                    rel_values = SObject.get_values(rel_sobjs, from_col)

                connected_col = to_col
           
            single_col = len(col_list) == 1
            search_op = 'and'
            if not single_col:
                search_op = 'or'
            for col in col_list:
                if keyword_mode == "contains":
                    search.add_keyword_filter(col, values, case_sensitive=case_sensitive)
                else:
                    search.add_startswith_keyword_filter(col, values,
                       case_sensitive=case_sensitive)
               
            search.add_op(search_op)


            if connected_col:
                search.add_filters(connected_col, rel_values, op='in')

            limit = self.get_limit()
            if limit:
                search.add_limit(limit)

            results = search.get_sobjects()

            info_dict['results'] = results
  


        mode = self.kwargs.get("mode")
        if mode == "icon":

            results = search_dict.get(search_type).get('results')

            labels = [x.get_value(column) or "" for x in results]
            values = [x.get_value(value_column) or "" for x in results]

            widget = self.get_icon_result_wdg(results, values, labels )
            top.add(widget)
            return top


        # if the value column is specified then don't use keywords
        # this assume only 1 column is used with "value_column" option
        elif value_column:

            results = search_dict.get(search_type).get('results')

            display_column = column.split(",")[0]
            labels = [x.get_value(display_column) for x in results]
            values = [x.get_value(value_column) for x in results]

            widget = self.get_results_wdg(results, values, labels)
            top.add(widget)
            return top




        # use keywords


        top.add_style('font-size: 12px')

        # English: ???
        ignore = set()
        ignore.add("of")
        ignore.add("in")
        ignore.add("the")
        ignore.add("for")
        ignore.add("a")
        ignore.add("and")

        filtered = []
        first_filtered = []
        second_filtered = []

        for search_type, info_dict in search_dict.items():
            results = info_dict.get('results')
            col_list = info_dict.get('col_list')
            for result in results:
                keywords = []
                for column in col_list:
                    if column.find(".") != -1:
                        parts = column.split(".")
                        column = parts[-1]
                    
                    # this result could be a join of columns from 2 tables 
                    value = result.get_value(column)
                    if self.is_number(value): 
                        value = str(value)
                    keywords.append(value)
               
                # NOTE: not sure what this does to non-english words
                #keywords = str(keywords).translate(None, string.punctuation)
                # keywords can be a long space delimited string in global mode
                # join and then split after
                # use comprehension to handle the lower() function
                keywords = " ".join(keywords)

                # split again
                keywords = keywords.split(" ")

                import string
                for i, k in enumerate(keywords):
                    leftovers = set(k) - set(string.ascii_letters+string.digits)
                    if leftovers:
                        k2 = k.strip("".join(leftovers))
                        keywords[i] = k2

                # show the keyword that matched first
                if case_sensitive: 
                    keywords = [x.strip() for x in keywords if x]
                else:
                    keywords = [x.lower().strip() for x in keywords if x]
                #keywords_set = set()
                #for keyword in keywords:
                #    keywords_set.add(keyword)
                # if x in the comprehension above already does None filtering
                #keywords = filter(None, keywords)
                matches = []
                for i, value in enumerate(values):
                    for keyword in keywords:
                        # only the last is compared with start
                        if i == 0 and not last_word_complete:
                            compare = keyword.startswith(value)
                        else:
                            compare = keyword == value

                        if compare:
                            matches.append(keyword)
                            break
                # if nothing matches, 2nd guess by loosening the rule to find something broader
                # this only runs most likely in global mode and sometimes in keyword mode
                # Just take the first value to maintain performance
                if not matches and values and values[0].strip():
                    for keyword in keywords:
                        compare = values[0] in keyword
                        if compare:
                            matches.append(keyword)
                            break
                # the length don't necessarily match since we could add the value the user types in as is
                #if len(matches) != len(values):
                if len(matches) < 1:
                    continue
                for match in matches:
                    keywords.remove(match)
                    keywords.insert(0, match)

                # get the first match
                first = keywords[:len(matches)]
                first = filter(None, first)
                first = " ".join(first)

                # add the first word filtered
                if keyword_mode == "contains" and orig_value in first:
                    first_filtered.append(first)
                elif first.startswith(orig_value) and first not in first_filtered:
                    first_filtered.append(first)
                
                # get all the other keywords
                for second in keywords[len(matches):]:
                    if first == second:
                        continue
                    
                    key = "%s %s" % (first, second)
                    if keyword_mode == "contains" and orig_value not in key:
                        continue
                    elif not key.startswith(orig_value):
                        continue

                    if key not in second_filtered:
                        second_filtered.append(key)

        first_filtered.sort()
        filtered.extend(first_filtered)
        second_filtered.sort()
        filtered.extend(second_filtered)

        filtered = filtered[0:10]

        for keywords in filtered:
            #print("keywords: ", keywords)
            div = DivWdg()
            top.add(div)
            div.add_style("padding: 3px")
            div.add_style("cursor: pointer")
            
            if not Common.IS_Pv3 and isinstance(keywords, str):
                keywords = unicode(keywords, errors='ignore')

            if len(keywords) > self.DISPLAY_LENGTH:
                display = "%s..." % keywords[:self.DISPLAY_LENGTH-3]
            else:
                display = keywords

            if highlight:
                substring_list = display.split(orig_value)

                display_el = ""
                for i in range(len(substring_list)):
                    substring = substring_list[i]
                    display_el += substring

                    if (i != len(substring_list)-1):
                        display_el += "<span style='background: %s'>%s</span>" % (highlight_color, orig_value)
                div.add(display_el)
            else:
                div.add(display)
            div.add_class("spt_input_text_result")
            div.add_attr("spt_value", keywords)
            # turn off cache to prevent ascii error
            keywords = HtmlElement.get_json_string(keywords, use_cache=False)
            div.add_attr("spt_display", keywords)


        if len(filtered) == 0:
            div = DivWdg()
            div.add("-- no results --")
            div.add_style("opacity: 0.5")
            div.add_style("font-style: italic")
            div.add_style("text-align: center")
            top.add(div)


        return top







class GlobalSearchWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    'show_button': {
        'description': 'Determines whether or not to show a button beside the search text field',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 1,
        'category': 'Options'
    },
    'hint_text': {
        'description': 'initial hint text',
        'type': 'TextWdg',
        'order': 3,
        'category': 'Options'
    },
    }
 

    def get_display(self):

        top = self.top


        # DISABLED for now.  The search is on sobject_list which does not
        # display the icon correctly in tile view
        layout = self.kwargs.get("layout")
        if not layout:
            layout = ''
        layout = ''


        search_wdg = DivWdg()
        search_wdg.add_class("spt_main_top")
        top.add(search_wdg)
        #search_wdg.add_style("padding: 10px")
        #search_wdg.add_style("margin: 10px auto")
        #search_wdg.add("Search: ")
        #search_wdg.add("&nbsp;"*3)


        custom_cbk = {}
        custom_cbk['enter'] = '''
            var top = bvr.src_el.getParent(".spt_main_top");
            var search_el = top.getElement(".spt_main_search");
            var keywords = search_el.value;

            if (keywords != '') {
                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    'search_type': 'sthpw/sobject_list',
                    'view': 'result_list',
                    'keywords': keywords,
                    'simple_search_view': 'simple_filter',
                    'show_shelf': false,
                    'layout': '%s',
                }
                spt.tab.set_main_body_tab();
                spt.tab.add_new("Search Results", "Search Results", class_name, kwargs);
            }
         ''' % layout

        hint_text = self.kwargs.get("hint_text")
        if not hint_text:
            hint_text = "Search"

        from tactic.ui.input import TextInputWdg, LookAheadTextInputWdg
        #text = TextInputWdg(name="search")
        text = LookAheadTextInputWdg(name="search", custom_cbk=custom_cbk, hint_text=hint_text)
        #text = TextWdg("search")
        text.add_class("spt_main_search")
        search_wdg.add(text)

        show_button = self.kwargs.get("show_button")
        if show_button in [True, 'true']:
            button = HtmlElement.button("GO")
            search_wdg.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'layout': layout,
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_main_top");
                var search_el = top.getElement(".spt_main_search");
                var keywords = search_el.value;

                if (keywords == '') {
                    return;
                }

                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    'search_type': 'sthpw/sobject_list',
                    'view': 'result_list',
                    'keywords': keywords,
                    'simple_search_view': 'simple_filter',
                    'show_shelf': false,
                    'layout': bvr.layout,
                }
                spt.tab.set_main_body_tab();
                spt.tab.add_new("Search Results", "Search Results", class_name, kwargs);
                '''
            } )

 
        return top
