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

from pyasm.common import Date, Common, Environment, FormatValue
from pyasm.web import Table, DivWdg, SpanWdg, WebContainer, Widget, HtmlElement
from pyasm.biz import Project
from pyasm.search import Search, SearchType
from pyasm.widget import IconWdg, TextWdg, BaseInputWdg, PasswordWdg, HiddenWdg
from tactic.ui.common import BaseRefreshWdg

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
        'description': 'format key to dispaly the data',
        'type': 'TextWdg',
        'order': 2,
        'category': 'Options'
    }
    }






    def set_value(my, value, set_form_value=False):
        my.text.set_value(value, set_form_value=set_form_value)
 
    def add_behavior(my, behavior):
        my.text.add_behavior(behavior)
 
 
    def get_text(my):
        return my.text
 





    def __init__(my, **kwargs):
        name = kwargs.get("name")
        my.name = name

        my.password = kwargs.get("password")
        if my.password in [True, 'true']:
            my.password = True

        if my.password:
            my.text = PasswordWdg(name)
        else:
            my.text = TextWdg(name)


        class_name = kwargs.get("class")
        if class_name:
            my.text.add_class(class_name)

        my.readonly = kwargs.get("read_only")
        if my.readonly in [True, 'true']:
            my.set_readonly(True)



        my.text.add_class("spt_text_input")
        border_color = my.text.get_color("border")
        my.text.add_style("border: solid 1px %s" % border_color)
        my.text.add_style("padding: 4px")

        if my.readonly:
            bgcolor = my.text.add_color("background", "background", [-20,-20,-20])
        else:
            bgcolor = my.text.get_color("background", -3)
            my.text.add_style("background", bgcolor)

        bgcolor2 = my.text.get_color("background", -10)
        if not my.readonly:
            my.text.add_behavior( {
                'type': 'blur',
                'bgcolor': bgcolor,
                'bgcolor2': bgcolor2,
                'cbjs_action': '''
                
                if (bvr.src_el.hasClass('spt_input_validation_failed'))
                    return;

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
                '''
                } )
 
       
        my.top = SpanWdg()

        my.kwargs = kwargs
        super(TextInputWdg, my).__init__()


        my.width = my.kwargs.get("width")
        if not my.width:
            my.width = 200
        else:
            my.width = my.width.replace("px", "")
            my.width = int(my.width)


    def add_style(my, name, value=None):
        if not value:
            name, value = name.split(": ")

        if name == 'width':
            my.width = int(value.replace("px",""))
        elif name == 'float':
            my.top.add_style(name, value)
        else:
            my.text.add_style(name, value)


    def add_behavior(my, behavior):
        my.text.add_behavior(behavior)





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


    def fill_data(my):
        value = my.kwargs.get("value")
        # value always overrides
        if value:
             my.text.set_value(value)
             return

      
        # fill in the values
        search_key = my.kwargs.get("search_key")
        if search_key and search_key != "None":
            sobject = Search.get_by_search_key(search_key)
            if sobject:

                # look at the current sobject for the data
                column = my.kwargs.get("column")
                if not column:
                    column = my.name

                display = sobject.get_value(column)
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
        top.add_style("height: 20px")
        top.add_style("width: %spx" % my.width)
        top.add_class("spt_input_text_top")



        if my.kwargs.get("required") in [True, 'true']:
            required_div = DivWdg("*")
            required_div.add_style("position: absolute")
            required_div.add_style("font-size: 18px")
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
            edit_div.add_style("margin-left: %spx" % my.width)

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


        text_div = SpanWdg()
        top.add(text_div)
        text_div.add(my.text)




       
        
        if not my.text.value:
            hint_text = my.kwargs.get("hint_text")
            if hint_text:
                my.text.add_attr('title', hint_text)
                # this prevents using this value for search
                my.text.add_behavior({ 'type': 'load',
                    'cbjs_action': '''
                    var over = new OverText(bvr.src_el, {
                        positionOptions: {
                            offset: {x:5, y:5}}});
                    over.text.setStyle('color','#999');
                    over.text.setStyle('font-size','11px');
                    over.text.setStyle('font-family','Arial, Serif');
                    '''})

		

        #my.text.add_style("-moz-border-radius: 5px")
        my.text.set_round_corners()
        my.text.add_style("width: %spx" % my.width)
        text_div.add_style("width: %spx" % my.width)
        text_div.add_style("position: relative")

        icon_wdg = DivWdg()
        text_div.add(icon_wdg)
        icon_wdg.add_style("position: absolute")
        
        if WebContainer.get_web().get_browser() in ['Webkit', 'Qt']:
            top_offset = '-2'
            right_offset = '6'
        #elif WebContainer.get_web().get_browser() == 'Qt':
        #    top_offset = '4'
        #    right_offset = '6'
        else:
            top_offset = '2'
            right_offset = '8'

        icon_wdg.add_style("top: %spx" %top_offset)
        icon_wdg.add_style("right: %spx" % right_offset)


        if not my.readonly:

            icon = IconWdg("Clear", IconWdg.CLOSE_INACTIVE, inline=False)
            icon.add_class("spt_icon_inactive")
            icon_wdg.add(icon)
            icon.add_style("opacity: 0.3")


            icon = IconWdg("Clear", IconWdg.CLOSE_ACTIVE, inline=False)
            icon.add_class("spt_icon_active")
            icon.add_style("display: none")
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

        top.add("&nbsp;")

        return top



class PasswordInputWdg(TextInputWdg):
    def __init__(my, **kwargs):
        kwargs['password'] = True
        super(PasswordInputWdg, my).__init__(**kwargs)


    def set_value(my, value, set_form_value=False):
        '''Password handles the value like an attr'''
        my.text.set_attr('value', value)




class LookAheadTextInputWdg(TextInputWdg):

    def set_name(my, name):
        my.name = name
        my.text.set_name(name)
        my.hidden.set_name(name)


    def init(my):

        my.search_type = my.kwargs.get("search_type")
        filter_search_type = my.kwargs.get("filter_search_type")
        if not my.search_type:
            my.search_type = 'sthpw/sobject_list'
        column = my.kwargs.get("column")
        if not column:
            column = 'keywords'

        value_column = my.kwargs.get("value_column")
        
        my.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
spt.text_input = {}

spt.text_input.is_on = false;
spt.text_input.index = -1;
spt.text_input.last_index = 0;

// async validate when value_column is defined
spt.text_input.async_validate = function(src_el, search_type, column, value, value_column) {
    if (!value) 
        return;

    var cbk = function(data) {
        var top = src_el.getParent(".spt_input_text_top");
        var hidden_el = top.getElement(".spt_text_value");
     
        if (!data && data != 0) {
            src_el.setStyle("background", "#A99");
            hidden_el.value = '';
            src_el.addClass("spt_invalid");
        }
        else {
            hidden_el.value = data;
            src_el.removeClass("spt_invalid");
        }

    }
    // can support having pure ' or " in the value, not mixed
    if (value.test(/"/) && value.test(/'/)) {
        spt.alert("Validation of a mix of ' and \\" is not supported");
        return;
    }

    if (value.test(/"/))
        value_expr = "'" + value + "'";
    else
        value_expr = '"' + value + '"';
        
    var expr = '@GET(' + search_type + '["'  + column +'",' + value_expr + '].' + value_column + ')'; 
   
    var kwargs = {
        single: true,
        cbjs_action: cbk
    };
    
    var server = TacticServerStub.get();
    try {
        server.async_eval(expr, kwargs);
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
            'cbjs_action': '''
          
            
            // put a delay in here so that a click in the results
            // has time to register
            
            setTimeout( function() {
                var top = bvr.src_el.getParent(".spt_input_text_top");
                var el = top.getElement(".spt_input_text_results");
                el.setStyle("display", "none");

                spt.text_input.last_index = 0;
                spt.text_input.index = -1;

                // if there is value_column and something in the input, it tries to validate 
                if (bvr.value_column) {
                    if (bvr.src_el.value) {
                        var value = bvr.src_el.value;
                        spt.text_input.async_validate(bvr.src_el, bvr.search_type, bvr.column, value, bvr.value_column);
                    } else {
                        var hidden_el = top.getElement(".spt_text_value");
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
                    'show_shelf': false,
                }
                spt.tab.set_main_body_tab();
                spt.tab.add_new("Search", "Search", class_name, kwargs);
            ''' % (my.search_type, filter_search_type)
        """
 


        filters = my.kwargs.get("filters")
      
        bgcolor = my.text.get_color("background3")
       

        my.text.add_behavior( {
            'type': 'keyup',
            'custom': custom_cbk,
            'search_type': my.search_type,
            'filter_search_type': filter_search_type,
            'filters': filters,
            'column': column,
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
                    var custom = bvr.custom.enter;
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
                    value: value
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
        results_div.add_style("z-index: 1000")
        results_div.add_style("position: absolute")
        results_div.add_style("top: 20px")
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



    def fill_data(my):

        default = my.kwargs.get("default")


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

    def is_number(my, value):
        if has_numbers_module:
            return isinstance(value, numbers.Number)
        else:
            return isinstance(value, int) or isinstance(value, long) or isinstance(value, float) 

   

    def get_display(my):
        top = my.top
        value = my.kwargs.get("value")
        if value.endswith(" "):
            last_word_complete = True
        else:
            last_word_complete = False


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



        value = value.strip()
        # TODO:  This may apply to normal keyword search as well. to treat the whole phrase as 1 word
        if value_column and value.find(' ') != -1:
            values = [value]
        else:
            values = Common.extract_keywords(value)
            # allow words with speical characters stripped out by Common.extract_keywords to be searched
            if value.lower() != " ".join(values):
                values.append(value.lower())
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
        for search_type, info_dict in search_dict.items():
            search = Search(search_type)

            #search.add_text_search_filter(column, values)
            if search_type == 'sthpw/sobject_list':
                search.add_filter("project_code", project_code)

            if search_type == 'sthpw/sobject_list' and filter_search_type and filter_search_type != 'None':
                search.add_filter("search_type", filter_search_type)
            if filters:
                search.add_op_filters(filters)
            
            search.add_op("begin")

            search_type_obj = SearchType.get(search_type)
            column_info = SearchType.get_column_info(search_type)
            col_list = info_dict.get('col_list')
            for col in col_list:
                
                #info = column_info.get(column)
                #if info and info.get("data_type") == 'integer':
                #    search.add_filter(column,values[0], op='=')
                #else:
                #    search.add_startswith_keyword_filter(column, values)
                search.add_startswith_keyword_filter(col, values)
            
            search.add_op("or")

            search.add_limit(10)
            results = search.get_sobjects()
            info_dict['results'] = results
   

        top.add_style('font-size: 11px')

        # if the value column is specified then don't use keywords
        # this assume only 1 column is used with "value_column" option
        if value_column:
            results = search_dict.get(search_type).get('results')
            for result in results:
                display = result.get_value(column)
                div = DivWdg()
                div.add(display)
                div.add_style("padding: 3px")
                div.add_class("spt_input_text_result")
                # turn off cache to prevent ascii error
                display = HtmlElement.get_json_string(display, use_cache=False)
                div.add_attr("spt_display", display)
                div.add_attr("spt_value", result.get_value(value_column))
                top.add(div)
            if not results:
                div = DivWdg()
                div.add("-- no results --")
                div.add_style("opacity: 0.5")
                div.add_style("font-style: italic")
                div.add_style("text-align: center")
                top.add(div)
            return top

       





        max = 35

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

                # commented out the join and then split. Looks redundant
                # just use comprehension to handle the lower() function
                #keywords = " ".join(keywords)
                
                keywords = [x.lower() for x in keywords]

                # NOTE: not sure what this does to non-english words
                #keywords = str(keywords).translate(None, string.punctuation)


                # show the keyword that matched first
                #keywords = keywords.split(" ")
                #keywords_set = set()
                #for keyword in keywords:
                #    keywords_set.add(keyword)
                keywords = filter(None, keywords)
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
                if first not in first_filtered:
                    first_filtered.append(first)

                # get all the other keywords
                for second in keywords[len(matches):]:
                    if first == second:
                        continue
                    key = "%s %s" % (first, second)
                    if key not in second_filtered:
                        second_filtered.append(key)


        first_filtered.sort()
        filtered.extend(first_filtered)
        second_filtered.sort()
        filtered.extend(second_filtered)

        filtered = filtered[0:10]

        for keywords in filtered:
            div = DivWdg()
            top.add(div)
            div.add_style("padding: 3px")
            
            if isinstance(keywords, str):
                keywords = unicode(keywords, errors='ignore')

            if len(keywords) > max:
                display = "%s..." % keywords[:max-3]
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


        from tactic.ui.input import TextInputWdg, LookAheadTextInputWdg
        #text = TextInputWdg(name="search")
        text = LookAheadTextInputWdg(name="search", custom_cbk=custom_cbk)
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
