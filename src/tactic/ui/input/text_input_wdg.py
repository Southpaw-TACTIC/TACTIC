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

import random, re, string

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






    def set_value(my, value, set_form_value=False):
        my.text.set_value(value, set_form_value=set_form_value)

    def get_value(my):
        return my.text.get_value()
 
 
    def add_behavior(my, behavior):
        my.text.add_behavior(behavior)
 
 
    def get_text(my):
        return my.text
 

    def __init__(my, **kwargs):
        my.kwargs = kwargs

        my.name = my.kwargs.get("name")
        name = my.name

        my.password = kwargs.get("password")
        if my.password in [True, 'true']:
            my.password = True

        if my.password:
            my.text = PasswordWdg(name)
        else:
            my.text = TextWdg(name)

        my.text.set_attr('autocomplete','off')

        class_name = kwargs.get("class")
        if class_name:
            my.text.add_class(class_name)

        my.readonly = kwargs.get("read_only")
        if my.readonly in [True, 'true']:
            my.set_readonly(True)
            bgcolor = my.text.add_color("background", "background", [-10, -10, -10])
        else:
            my.readonly = False
            bgcolor = my.text.get_color("background")
            my.text.add_style("background", bgcolor)

        my.icon_wdg = SpanWdg()


        my.border_color = my.text.get_color("border")

        my.text.add_class("spt_text_input")
        #my.text.add_style("padding: 4px")


        bgcolor2 = my.text.get_color("background", -10)
        if not my.readonly:

            # TODO: replace with bootstrap error classes
            my.text.add_behavior( {
                'type': 'blur',
                'bgcolor': bgcolor,
                'bgcolor2': bgcolor2,
                'cbjs_action': '''
                if (bvr.src_el.hasClass('spt_input_validation_failed')) {
                    return;
                }

                var value = bvr.src_el.value;
                var last_value = bvr.src_el.getAttribute("spt_last_value");
                if (value == "") {
                    bvr.src_el.setStyle("background", bvr.bgcolor);
                }
                else if (!last_value && last_value != value) {
                    bvr.src_el.setStyle("background", bvr.bgcolor2);
                }
                else {
                    bvr.src_el.setStyle("background", bvr.bgcolor);
                }

                bvr.src_el.setAttribute("spt_last_value", value);

                //spt.input.set_success(bvr.src_el);
                if (spt.input.set_error)
                    spt.input.set_error(bvr.src_el);
                '''
                } )
 
       
        my.top = DivWdg()



        height = my.kwargs.get("height")
        if height:
            height = height.replace("px", "")
            height = int(height)
        else:
            height = 35

        my.height = height


        super(TextInputWdg, my).__init__()

        my.icon = my.kwargs.get("icon")
        my.icon_pos = my.kwargs.get("icon_pos")
        if not my.icon_pos:
            my.icon_pos = "left"
        if my.icon:
            my.icon_div = DivWdg()


        my.width = my.kwargs.get("width")
        if not my.width:
            my.width = 230
        else:
            my.width = str(my.width).replace("px", "")
            if not my.width.endswith("%"):
                my.width = int(my.width)

        my.text.add_style("width: %s" % my.width)


    def add_style(my, name, value=None):
        if not name:
            return

        if not value:
            name, value = re.split(":\ ?", name)

        if name == 'width':
            my.width = value
            my.text.add_style(name, value)
        elif name == 'float':
            my.top.add_style(name, value)
        else:
            my.text.add_style(name, value)


    def add_behavior(my, behavior):
        my.text.add_behavior(behavior)


    def get_icon_wdg(my):
        return my.icon_wdg





    def set_readonly(my, flag=True):
        my.readonly = flag
        my.text.set_attr("readonly", "readonly")

    def add_class(my, class_name):
        my.text.add_class(class_name)

    def add_color(my, name, palette_key, modifier=0, default=None):
        my.text.add_color(name, palette_key, modifier, default)

    def set_attr(my, name, value):
        my.text.set_attr(name, value)

    def set_value(my, value, set_form_value=False):
        my.text.set_value(value, set_form_value=set_form_value)

    def set_name(my, name):
        my.name = name
        my.text.set_name(name)

    def is_datetime_col(my, sobject, name):
        '''get_column_info call datetime as timestamp, which is the time tactic_type'''
        tactic_type = SearchType.get_tactic_type(sobject.get_search_type(), name)
        if tactic_type == 'time':
            return True
        else:
            return False

    def fill_data(my):

        if not my.name:
            my.name = my.kwargs.get("name")
        name = my.get_input_name()
        my.text.set_name(name)
        value = my.kwargs.get("value")
        # value always overrides
        if value:
             my.text.set_value(value)
             return

        # fill in the values
        search_key = my.kwargs.get("search_key")
        
        if search_key and search_key != "None" or my.sobjects:
            if my.sobjects:
                sobject = my.sobjects[0]
            else:
                sobject = Search.get_by_search_key(search_key)

            if sobject:
            # look at the current sobject for the data
                display = ""
                if not sobject.is_insert():
                    column = my.kwargs.get("column")
                    if not column:
                        column = my.name
                    
                    display = sobject.get_value(column, no_exception=True)
                if display and my.is_datetime_col(sobject, column) and not SObject.is_day_column(column):
                    display = SPTDate.convert_to_local(display)
                    
                if isinstance(display, str):
                    # this could be slow, but remove bad characters
                    display = unicode(display, errors='ignore').encode('utf-8')

                format_str = my.get_option("display_format")
                if format_str:
                    format = FormatValue()
                    display = format.get_format_value( display, format_str )
                my.text.set_value(display)

        default = my.kwargs.get("default")
        if default and not my.text.value:
            my.text.set_value(default)



    def get_display(my):

        my.fill_data()

        top = my.top
        top.add_style("position: relative")
        top.add_class("spt_text_top")
        top.add_class("spt_input_text_top")


        if my.kwargs.get("required") in [True, 'true']:
            required_div = DivWdg("*")
            required_div.add_style("position: absolute")
            required_div.add_style("font-size: 1.0em")
            top.add(required_div)
            required_div.add_color("color", "color", [50, 0, 0])
            required_div.add_style("margin-left: -10px")
            top.add_class("spt_required")

        validation_js = my.kwargs.get("validation_js")
        validation_scheme = my.kwargs.get("validation_scheme")
        if validation_js or validation_scheme:
            from tactic.ui.app import ValidationUtil
            if validation_js:
                v_util = ValidationUtil( js =validation_js  )
           
            elif validation_scheme:
                v_util = ValidationUtil( scheme =validation_scheme  )

            validation_bvr = v_util.get_validation_bvr()
            validation_change_bvr = v_util.get_input_onchange_bvr()
            if validation_bvr:
                my.text.add_behavior(validation_bvr)
                my.text.add_behavior(validation_change_bvr)
        
                #v_div = DivWdg()
                #v_div.add_class("spt_validation_%s" % name)
                #v_div.add_behavior( validation_bvr )

        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            is_admin = True
        else:
            is_admin = False

        search_type = my.kwargs.get("search_type")
        # FIXME: this should only show up if asked
        show_edit = my.kwargs.get("show_edit")
        if show_edit in [True, 'true']:
            show_edit = True
        else:
            show_edit = False

        if show_edit and is_admin and not my.readonly and search_type:
            from pyasm.widget import IconButtonWdg

            edit_div = DivWdg()
            edit_div.add_style("position: absolute")
            edit_div.add_style("font-size: 18px")
            top.add(edit_div)
            edit_div.add_color("color", "color", [50, 0, 0])
            edit_div.add_style("margin-left: %s" % my.width)

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



            except Exception, e:
                print "WARNING: ", e
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
            label_wdg.add(my.name)


        input_group = DivWdg()
        div.add(input_group)

        input_group.add_style("width: %s" % my.width)
        input_group.add_style("height: %s" % my.height)
        input_group.add_style("margin-right: 5px")
        my.text.add_style("height: %s" % my.height)

        icon_styles = my.kwargs.get("icon_styles")
        icon_class = my.kwargs.get("icon_class")

        if my.icon and my.icon_pos == "left":
            input_group.add_class("input-group")
            if isinstance(my.icon, basestring):
                if len(my.icon) > 1:
                    icon = IconWdg(title="", icon=my.icon, width=16, opacity=1.0)
                else:
                    icon = my.icon
            else:
                icon = my.icon
            input_group.add(my.icon_wdg)
            my.icon_wdg.add_class("input-group-addon")
            my.icon_wdg.add(icon)
            if icon_styles:
                my.icon_wdg.add_styles(icon_styles)
            if icon_class:
                my.icon_wdg.add_class(icon_class)


        input_group.add(my.text)
        my.text.add_class("form-control")
        my.text.add_style('color', div.get_color('color')) 
        text_class = my.kwargs.get("text_class")
        if text_class:
            my.text.add_class(text_class)

        if my.icon and my.icon_pos == "right":
            input_group.add_class("input-group")
            if isinstance(my.icon, basestring):
                if len(my.icon) > 1:
                    icon = IconWdg(title="", icon=my.icon, width=16, opacity=1.0)
                else:
                    icon = my.icon
            else:
                icon = my.icon
            input_group.add(my.icon_wdg)
            my.icon_wdg.add_class("input-group-addon")
            my.icon_wdg.add(icon)
            if icon_styles:
                my.icon_wdg.add_styles(icon_styles)
            if icon_class:
                my.icon_wdg.add_class(icon_class)

            # Below is added only for collection search icon
            # Adding the same custom_cbk from Collections to icon click_up
            is_collection = my.kwargs.get("is_collection")
            if is_collection:
                custom_cbk = my.kwargs.get("custom_cbk")
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
        my.text.add_behavior( {
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


        default = my.kwargs.get("value")
        if not default:
            default = my.kwargs.get("default")
        if default:
            my.text.set_value(default)

        if not my.text.value:
            hint_text = my.kwargs.get("hint_text")
            color = my.text.get_color('color')
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

                my.text.add_attr('placeholder', hint_text)
                my.text.add_style("text-overflow: ellipsis")
                my.text.add_style("overflow: hidden")
                my.text.add_style("white-space: nowrap")

        if not my.readonly:
            # DISABLE for now
            pass
            """
            icon_wdg = DivWdg()
            my.text.add(icon_wdg)
            #icon_wdg.add_style("top: 0px")
            icon_wdg.add_style("float: right")
            icon_wdg.add_style("position: relative")



            icon = IconWdg("Clear", "BS_REMOVE", opacity=0.3)
            icon.add_class("spt_icon_inactive")
            icon.add_styles("margin: auto; position: absolute;top: 0;bottom: 8; right: 0; max-height: 100%")
            icon_wdg.add(icon)
            #icon = IconButtonWdg("Remove Tab", IconWdg.CLOSE_ACTIVE)
            icon = IconWdg("Clear", "BS_REMOVE")
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

            if my.password:
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
    def __init__(my, **kwargs):
        kwargs['password'] = True
        super(PasswordInputWdg, my).__init__(**kwargs)


    def set_value(my, value, set_form_value=False):
        '''Password handles the value like an attr'''
        my.text.set_attr('value', value)




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
    }
    })
    

    def set_name(my, name):
        my.name = name
        my.text.set_name(name)
        my.hidden.set_name(name)



    def init(my):
        my.text.add_attr("autocomplete", "off")

        my.search_type = my.kwargs.get("search_type")
        filter_search_type = my.kwargs.get("filter_search_type")

        event_name = ''
        if filter_search_type:
            base_st = SearchKey.extract_base_search_type(filter_search_type)
            event_name = '%s|%s'%(my.RESULT_SELECT_EVENT, base_st) 

        if not my.search_type:
            my.search_type = 'sthpw/sobject_list'
        column = my.kwargs.get("column")
        relevant = my.kwargs.get("relevant")
        
        if not column:
            column = 'keywords'
    
        case_sensitive  = my.kwargs.get("case_sensitive") in ['true',True]

        value_column = my.kwargs.get("value_column")
        validate = my.kwargs.get("validate") in ['true', None]
        if not validate:
            my.top.add_class('spt_no_validate')
        
        do_search = my.kwargs.get("do_search")
        if not do_search:
            do_search = 'true'

        my.add_behavior( {
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
spt.text_input.async_validate = function(src_el, search_type, column, display_value, value_column, kwargs) {
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
                src_el.setStyle("background", "#A99");
                src_el.addClass("spt_invalid");
            }
        }
        else {
            hidden_el.value = data;
            src_el.removeClass("spt_invalid");
        }

       // run client trigger
       spt.text_input.run_client_trigger(bvr, kwargs.event_name, src_el.value, data);

    }
    // can support having pure ' or " in the value, not mixed
    if (display_value.test(/"/) && display_value.test(/'/)) {
        spt.alert("Validation of a mix of ' and \\" is not supported");
        return;
    }

    if (display_value.test(/"/))
        value_expr = "'" + display_value + "'";
    else
        value_expr = '"' + display_value + '"';
        
    var expr = '@GET(' + search_type + '["'  + column +'",' + value_expr + '].' + value_column + ')'; 
    var kw = {
        single: true,
        cbjs_action: cbk
    };
    
    //TODO: support other kinds of eval for validation
    var server = TacticServerStub.get();
    try {
        server.async_eval(expr, kw);
    } catch(e) {
        log.critical(spt.exception.handler(e));
        return;
    }
    
    
};
            '''
        } )
        if not my.readonly:
            my.text.add_behavior( {
            'type': 'blur',
            'search_type': my.search_type,
            'column': column,
            'value_column': value_column,
            'event_name': event_name,
            'validate': str(validate),
            'do_search': do_search,
            'cbjs_action': '''
          
            // put a delay in here so that a click in the results
            // has time to register
            var validate = bvr.validate == 'True';
            var do_search = bvr.do_search == 'true';
            setTimeout( function() {
                var top = bvr.src_el.getParent(".spt_input_text_top");
                var el = top.getElement(".spt_input_text_results");
                el.setStyle("display", "none");

                spt.text_input.last_index = 0;
                spt.text_input.index = -1;

                // if there is value_column and something in the input, it tries to validate 
                if (bvr.value_column) {
                    var hidden_el = top.getElement(".spt_text_value");
                    if (bvr.src_el.value) {
                        var display_value = bvr.src_el.value;
                        var kwargs = {'validate': validate, 'do_search': do_search, 'event_name': bvr.event_name, 'hidden_value': hidden_el.value};
                        spt.text_input.async_validate(bvr.src_el, bvr.search_type, bvr.column, display_value, bvr.value_column, kwargs);
                    } else {
                        hidden_el.value ='';
                    }
                        
                }
            }, 250 );

            '''
        } )

        my.hidden = HiddenWdg(my.name)
        #my.hidden = TextWdg(my.name)
        my.top.add(my.hidden)
        my.hidden.add_class("spt_text_value")


        class_name = my.kwargs.get("class")
        if class_name:
            my.hidden.add_class("%s" % class_name)
            my.hidden.add_class("%s_value" % class_name)



        if my.readonly:
            return

        results_class_name = my.kwargs.get("results_class_name")
        if not results_class_name:
            results_class_name = 'tactic.ui.input.TextInputResultsWdg';


        custom_cbk = my.kwargs.get("custom_cbk")
        if not custom_cbk:
            custom_cbk = {}


       
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
            ''' % (my.search_type, filter_search_type)
        """
 
        mode = my.kwargs.get("mode")

        filters = my.kwargs.get("filters")
        script_path = my.kwargs.get("script_path")
        bgcolor = my.text.get_color("background3")
       

        my.top.add_relay_behavior( {
            'type': 'keyup',
            'bvr_match_class': "spt_text_input",
            'custom': custom_cbk,
            'do_search': do_search,
            'search_type': my.search_type,
            'filter_search_type': filter_search_type,
            'script_path': script_path,
            'filters': filters,
            'column': column,
            'mode': mode,
            'relevant': relevant,
            'case_sensitive': case_sensitive,
            'value_column': value_column,
            'results_class_name': results_class_name,
            'bg_color': bgcolor,
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
                        alert("tab");
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
            if (value == '') {
                return;
            }

            var class_name = bvr.results_class_name;

            var cbk = function(html) {
                var top = bvr.src_el.getParent(".spt_input_text_top");
                var el = top.getElement(".spt_input_text_results");
                el.setStyle("display", "");
                el.innerHTML = html;

                spt.text_input.is_on = false;
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
                    mode: bvr.mode
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



        results_div = DivWdg()
        my.top.add(results_div)
        results_div.add_style("display: none")
        results_div.add_style("position: absolute")
        #results_div.add_style("top: 25px")
        results_div.add_style("top: %spx" % (my.height - 10))
        results_div.add_style("left: 0px")
        results_div.add_color("background", "background")
        results_div.add_color("color", "color")
        results_div.add_style("padding: 5px 10px 10px 5px")
        results_div.add_style("min-width: 220px")
        results_div.add_style("z-index: 1000")
        results_div.add_style("font-size: 16px")
        results_div.add_style("font-weight: bold")
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

        
        # this is when the user clicks on a result item
        # it doesn't do a search right away, it fires the lookahead|<sType> event
        results_div.add_relay_behavior( {
            'type': "mouseup",
            'bvr_match_class': 'spt_input_text_result',
            'cbjs_action': '''
            var display = bvr.src_el.getAttribute("spt_display");
            display = JSON.parse(display);

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
        

    def fill_data(my):

        default = my.kwargs.get("default")

        # have to set the name with prefix if applicable
        name = my.get_input_name()
        if name:
            my.text.set_name(name)
            my.hidden.set_name(name)

        # fill in the values
        search_key = my.kwargs.get("search_key")
        value_key = my.kwargs.get("value_key")

        current_value_column = my.kwargs.get("current_value_column")
        if not current_value_column:
            current_value_column = my.name



        if value_key:
            column = my.kwargs.get("column")
            column_expr = my.kwargs.get("column_expr")
            value_column = my.kwargs.get("value_column")

            sobject = Search.get_by_search_key(value_key)

            display = sobject.get_value(column)
            value = sobject.get_value(value_column, auto_convert=False)

            
            my.text.set_value(display)
            if value != None:
                my.hidden.set_value(value)


        elif search_key and search_key != "None":
            sobject = Search.get_by_search_key(search_key)
            if sobject:

                column = my.kwargs.get("column")
                column_expr = my.kwargs.get("column_expr")
                value_column = my.kwargs.get("value_column")

                #expression = "@SOBJECT(%s)" % my.search_type
                #related = Search.eval(expression, sobject)

                related = None

                # assume a simple relationship
                value = sobject.get_value(current_value_column, auto_convert=False)
                if value not in ['', None] and value_column:
                    if value_column == "id":
                        related = Search.get_by_id(my.search_type, value)
                    else:
                        search = Search(my.search_type)
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
              
                my.text.set_value(display)
                if value != None:
                    my.hidden.set_value(value)




__all__.append("TextInputResultsWdg")
class TextInputResultsWdg(BaseRefreshWdg):

    # search LIMIT, even if we display only 10, the right balance is to set a limit to 80 to get more diverse results back
    LIMIT = 80
    DISPLAY_LENGTH = 35

    def is_number(my, value):
        if has_numbers_module:
            return isinstance(value, numbers.Number)
        else:
            return isinstance(value, int) or isinstance(value, long) or isinstance(value, float) 

    def init(my):
        my.do_search = True
        if my.kwargs.get('do_search') == 'false':
            my.do_search = False

    def draw_result(my, top, value):
        max = my.DISPLAY_LENGTH
        # assuming it's a list
        results = my.kwargs.get('results')
        if not results:
            script_path = my.kwargs.get('script_path')
            if not script_path:
                return
            try:
                from tactic.command import PythonCmd
                kwargs = {'value' : value}
                cmd = PythonCmd(script_path=script_path, **kwargs)
                Command.execute_cmd(cmd)
        
            except Exception, e:
                print e
                raise

            else:

                info = cmd.get_info()
                results = info.get('spt_ret_val')
                
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
            div = DivWdg()
            top.add(div)
            div.add_style("padding: 3px")
            
            if isinstance(keywords, str):
                keywords = unicode(keywords, errors='ignore')

            if isinstance(keywords, basestring) and  len(keywords) > max:
                display = "%s..." % keywords[:max-3]
            else:
                display = keywords

            div.add(display)
            div.add_class("spt_input_text_result")
            value = value_results[idx]
            div.add_attr("spt_value", value)
            # turn off cache to prevent ascii error
            keywords = HtmlElement.get_json_string(keywords, use_cache=False)
            div.add_attr("spt_display", keywords)




    def get_icon_result_wdg(my, results, values, labels):
        from tactic.ui.panel import ThumbWdg2

        top = DivWdg()
        top.add_style("font-size: 14px")
        top.add_style("width: 300px")
        top.add_style("margin: 3px 0px")
        top.add_style("padding: 0px 0px")

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



            name = result.get_value("name")
            if name:
                info_div.add("<br/>")
                info_div.add("<span style='opacity: 0.5; font-size: 10px;'>%s</span>" % name)


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




    def get_results_wdg(my, results, values, labels):
        top = DivWdg()

        for i, result in enumerate(results):
            display = labels[i]
            div = DivWdg()
            div.add(display)
            div.add_style("padding: 3px")
            div.add_class("spt_input_text_result")
            # turn off cache to prevent ascii error
            display = HtmlElement.get_json_string(display, use_cache=False)
            div.add_attr("spt_display", display)
            div.add_attr("spt_value", values[i])
            top.add(div)
        if not results:
            div = DivWdg()
            div.add("-- no results --")
            div.add_style("opacity: 0.5")
            div.add_style("font-style: italic")
            div.add_style("text-align: center")
            top.add(div)
        return top


    def get_display(my):
        top = my.top
        orig_value = my.kwargs.get("value")
        case_sensitive = my.kwargs.get("case_sensitive") in ['true',True]

        if not my.do_search:
            my.draw_result(top, orig_value)
            return top

        if not case_sensitive:
            orig_value = orig_value.lower()

        # can only support 1 right now
        relevant = my.kwargs.get("relevant") == 'true'
        connected_col = None
        rel_values = []

        if orig_value.endswith(" "):
            last_word_complete = True
        else:
            last_word_complete = False

        # TODO: rename this as top_sType
        search_type = my.kwargs.get("search_type")
        filter_search_type = my.kwargs.get("filter_search_type")
        filters = my.kwargs.get("filters")
        
        column = my.kwargs.get("column")
        value_column = my.kwargs.get("value_column")

        if not search_type:
            search_type = "sthpw/sobject_list"
        if not column:
            column = "keywords"


        if isinstance(column, basestring):
            columns = [column]
        else:
            columns = column


        value = orig_value.strip()

        # TODO:  This may apply to normal keyword search as well. to treat the whole phrase as 1 word
        if value_column and value.find(' ') != -1:
            values = [value]
        else:
            values = Common.extract_keywords(value, lower=not case_sensitive)
            # allow words with speical characters stripped out by Common.extract_keywords to be searched
            # FIXME: THIS CAUSES PROBLEMS and is disabled for now
            #if value.lower() not in values:
            #    values.append(value.lower())
        # why is this done?
        # so the auto suggestion list the items in the same order as they are typed in
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

        top_sType = my.kwargs.get("search_type")
        top_sType = Project.extract_base_search_type(top_sType)
        schema = Schema.get()

        for search_type, info_dict in search_dict.items():
            search = Search(search_type)

            # relevant is ON, then only search for stuff that is relevant in the current table
           

            #search.add_text_search_filter(column, values)
            if search_type == 'sthpw/sobject_list':
                search.add_filter("project_code", project_code)

            if search_type == 'sthpw/sobject_list' and filter_search_type and filter_search_type != 'None':
                search.add_filter("search_type", filter_search_type)
            if filters:
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
                #info = column_info.get(column)
                #if info and info.get("data_type") == 'integer':
                #    search.add_filter(column,values[0], op='=')
                #else:
                #    search.add_startswith_keyword_filter(column, values)
                search.add_startswith_keyword_filter(col, values, \
                   case_sensitive=case_sensitive)
               
            
            
            search.add_op(search_op)
            if connected_col:
                search.add_filters(connected_col, rel_values, op='in')
            search.add_limit(my.LIMIT)
            results = search.get_sobjects()
            info_dict['results'] = results
   
        mode = my.kwargs.get("mode")
        if mode == "icon":

            results = search_dict.get(search_type).get('results')

            labels = [x.get_value(column) for x in results]
            values = [x.get_value(value_column) for x in results]

            widget = my.get_icon_result_wdg(results, values, labels )
            top.add(widget)
            return top


        # if the value column is specified then don't use keywords
        # this assume only 1 column is used with "value_column" option
        elif value_column:

            results = search_dict.get(search_type).get('results')

            labels = [x.get_value(column) for x in results]
            values = [x.get_value(value_column) for x in results]

            widget = my.get_results_wdg(results, values, labels)
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
                    if my.is_number(value): 
                        value = str(value)
                    keywords.append(value)
               
                # NOTE: not sure what this does to non-english words
                #keywords = str(keywords).translate(None, string.punctuation)
                # keywords can be a long space delimited string in global mode
                # join and then split after
                # use comprehension to handle the lower() function
                keywords = " ".join(keywords)

                # show the keyword that matched first
                keywords = keywords.split(" ")
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
                if first.startswith(orig_value) and first not in first_filtered:
                    first_filtered.append(first)
                
                # get all the other keywords
                for second in keywords[len(matches):]:
                    if first == second:
                        continue
                    
                    key = "%s %s" % (first, second)
                    if not key.startswith(orig_value):
                        continue
                    if key not in second_filtered:
                        second_filtered.append(key)

        first_filtered.sort()
        filtered.extend(first_filtered)
        second_filtered.sort()
        filtered.extend(second_filtered)

        filtered = filtered[0:10]

        for keywords in filtered:
            #print "keywords: ", keywords
            div = DivWdg()
            top.add(div)
            div.add_style("padding: 3px")
            div.add_style("cursor: pointer")
            
            if isinstance(keywords, str):
                keywords = unicode(keywords, errors='ignore')

            if len(keywords) > my.DISPLAY_LENGTH:
                display = "%s..." % keywords[:my.DISPLAY_LENGTH-3]
            else:
                display = keywords

            div.add(display)
            div.add_class("spt_input_text_result")
            div.add_attr("spt_value", keywords)
            # turn off cache to prevent ascii error
            keywords = HtmlElement.get_json_string(keywords, use_cache=False)
            div.add_attr("spt_display", keywords)



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
 

    def get_display(my):

        top = my.top


        # DISABLED for now.  The search is on sobject_list which does not
        # display the icon correctly in tile view
        layout = my.kwargs.get("layout")
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

        hint_text = my.kwargs.get("hint_text")
        if not hint_text:
            hint_text = "Search"

        from tactic.ui.input import TextInputWdg, LookAheadTextInputWdg
        #text = TextInputWdg(name="search")
        text = LookAheadTextInputWdg(name="search", custom_cbk=custom_cbk, hint_text=hint_text)
        #text = TextWdg("search")
        text.add_class("spt_main_search")
        search_wdg.add(text)

        show_button = my.kwargs.get("show_button")
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
