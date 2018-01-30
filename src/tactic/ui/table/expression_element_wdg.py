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

__all__ = ['ExpressionElementWdg', "ExpressionValueElementWdg"]

import types, re

from pyasm.common import TacticException, Container, FormatValue, jsonloads, jsondumps, SPTDate
from pyasm.search import Search, SearchKey, SearchType
from pyasm.web import DivWdg, Widget
from pyasm.widget import IconWdg, TextWdg, TextAreaWdg, SelectWdg, CheckboxWdg
from pyasm.biz import ExpressionParser
from tactic.ui.common import BaseTableElementWdg, SimpleTableElementWdg

from table_element_wdg import TypeTableElementWdg
import datetime


class ExpressionElementWdg(TypeTableElementWdg):
    '''General purpose element widget for expressions'''

    ARGS_KEYS = {
    'expression': {
        'description': 'Expression to evaluate the widget',
        'type': 'TextAreaWdg',
        'order': 1,
        'category': 'Options'
    },
    'display_expression': {
        'description': 'Expression for display purposes',
        'type': 'TextAreaWdg',
        'order': 2,
        'category': 'Options'
    },
    'display_format': {
        'description': 'Predefined format for display',
        'type': 'TextWdg',
        'order': 3,
        'category': 'Options'
    },
    'link_expression': {
        'description': 'Expression for linking to another sobject',
        'type': 'TextAreaWdg',
        'order': 4,
        'category': 'Options',
    },
    'link_view': {
        'description': 'View to link result to another view',
        'type': 'TextWdg',
        'order': 5,
        'category': 'Options',
    },
    'inline_styles': 'Styles to add to the DIV generated that contains the result of the expression',
    'return':   {
        'descripton' : 'Determines what the expression return type should be',
        'type': 'SelectWdg',
        'values': 'single|list'
    },
    'bottom':   {
        'description': 'Expression to calculate the bottom row of the table',
        'type': 'TextAreaWdg',
    },
    'group_bottom':   {
        'description': 'Expression to calculate the bottom of a group',
        'type': 'TextAreaWdg',
    },
    'mode':     {
        'description': 'Display mode for this widget',
        'type': 'SelectWdg',
        'values': 'value|check|boolean',
        'order': 3

    },
    'expression_mode':     {
        'description': 'If absolute mode is selected, it does not relate to the current SObject',
        'type': 'SelectWdg',
        'values': 'default|absolute',
        'order': 6

    },
    'calc_mode':     {
        'description': '(ALPHA) fast|slow - fast uses new calculation mode. Only @SUM, @COUNT, @SOBJECT and @GET are current supported',
        'type': 'SelectWdg',
        'values': 'slow|fast',
        'order': 7
    },

    'show_retired':     {
        'description': 'true|false - true shows all the retired entries during the expression evaluation',
        'type': 'SelectWdg',
        'values': 'true|false',
        'category': 'Options',
        'order': 8
    },


    'enable_eval_listener': {
        'description': '''Currently javascript expression evaluation is not fully baked, so only use the client side evaluation listener when needed and NOT by default''',
        'category': 'internal'
    ,
    },
    'use_cache':     {
        'description': 'Determines whether or not to use the cached value.  Gets value from column with the same name as the element',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 0,
        'category': 'Cache'
    },
    'order_by': {
        'description': 'Turn on Order by',
        'type': 'TextWdg',
        
        'order': 8,
        'category': 'Options'
    },
     'group_by': {
        'description': 'Turn on Group by',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 9,
        'category': 'Options'
    },
    
     'group_by_time': {
        'description': 'Turn on Group by',
        'type': 'SelectWdg',
        'values': 'true|false',
        'order': 10,
        'category': 'Options'
    },

    'justify': {
        'description': 'Result justification',
        'type': 'SelectWdg',
        'values': 'default|left|right|center',
        'order': 11,
        'category': 'Options'
    },
    'filter_name': {
        'description': 'Name of filter to use',
        'type': 'TextWdg',
        'order': 12,
        'category': 'Options'
    },

    'empty': {
        'description': "vAlue to display if empty"
    }

    }
  




    def init(self):
        self.td = None
        self.expression = None
        self.alt_expression = None
        self.alt_result = None

        self.cache_results = None



    def preprocess(self):
        order_by = self.get_option("order_by")
        # for backward compatibility when order_by used to be true/false
        if not order_by or order_by =='true':
            expression = self.get_option("expression")
            if expression.startswith("@GET(") and expression.endswith(")") and expression.count("@") == 1:
                template = expression.lstrip("@GET(")
                template = template.rstrip(")")
                # remove white spaces
                template= template.strip()
                # if it's a simple local sType expression e.g. @GET(.id), strip the .
                if template.startswith("."):
                    template = template.lstrip('.')

                self.set_option("order_by", template)


        self.init_kwargs()

    def get_required_columns(self):
        '''method to get the require columns for this'''
        return []



    def get_header_option_wdg(self):

        return

        if self.kwargs.get("use_cache2") not in ['true', True]:
            return

        div = DivWdg()

        div.add("Last Calculated: 5 days ago<br/><hr/>")

        div.add("Recalculate")
        div.add_class("hand")

        #from tactic.ui.widget import ActionButtonWdg
        #button = ActionButtonWdg(title="Recalculate")
        #div.add(button)

        div.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var table = bvr.src_el.getParent(".spt_table");
        //var search_keys = spt.dg_table.get_search_keys();
        var search_keys = spt.dg_table.get_selected_search_keys(table);

        if (search_keys.length == 0) {
            spt.alert("No rows selected");
            return;
        }

        var header = bvr.src_el.getParent(".spt_table_th");
        var element_name = header.getAttribute("spt_element_name");

        spt.app_busy.show("Recalculating ...");
        var kwargs = {
            element_name: element_name,
            search_keys: search_keys,
        }
        spt.app_busy.show("Recalculating ...");
        var server = TacticServerStub.get();
        var class_name = 'tactic.ui.table.ExpressionRecalculateCmd';
        server.execute_cmd(class_name, kwargs);
        spt.app_busy.hide("Recalculating ...");
        '''
        } )
        
        return div




    def is_sortable(self):

        use_cache = self.get_option("use_cache") in ['true', True]
        if use_cache:
            return True

        order_by = self.get_option("order_by")

        # false is the word to prevent the auto-adoption (preprocess) of the expression to order-by
        if order_by and order_by !='false':
            parts = order_by.split(".")
            if "connect" in parts:
                return False
            return True
        else:
            return False


    def is_groupable(self):

        use_cache = self.get_option("use_cache") in ['true', True]
        if use_cache:
            return True


        group_by = self.get_option("group_by")
        if group_by:
            return True
        else:
            return False

    def is_time_groupable(self):
        group_by = self.get_option("group_by_time")
        if group_by:
            return True
        else:
            return False





    def get_vars(self):
        # create variables
        element_name = self.get_name()
        self.vars = {
            'ELEMENT_NAME': element_name
        }

        # get info from search critiera
        # FIXME: this should be formalized
        search_vars = Container.get("Message:search_vars")
        if search_vars:
            for name, value in search_vars.items():
                self.vars[name] = value

        return self.vars


    def get_input_by_arg_key(self, key):
        if key == 'expression':
            input = TextAreaWdg("option_expression")
        else:
            input = TextWdg("value")
        return input
    get_input_by_arg_key = classmethod(get_input_by_arg_key)


    def handle_td(self, td):

        if self.alt_result:
            td.add_attr("spt_input_value", self.alt_result)
        elif self.alt_result:
            td.add_attr("spt_input_value", self.value)

        super(ExpressionElementWdg,self).handle_td(td)


    def is_editable(self):
        return 'optional'



    def _get_result(self, sobject, expression):
        '''get the result of the expression'''

        element_name = self.get_name()

        use_cache = self.kwargs.get("use_cache")
        if use_cache == "true":
            try:
                return sobject.get_value(element_name)
            except Exception as e:
                print "Error: ", e.message


        if type(sobject) != types.ListType:
            if sobject.is_insert():
                return ''

        self.vars = {
            'ELEMENT_NAME': element_name,
            'ELEMENT': element_name,
            'SOBJECT_ID': sobject.get_id(),
            'SOBJECT_CODE': sobject.get_code(),
        }

        return_type = self.kwargs.get("return")
        if return_type == 'single':
            single = True
            list = False
        elif return_type == 'list':
            single = False
            list = True
        else:
            single = True
            list = False

        # if this expression is an absolute expression, then don't bother
        # with the sobject
        expression_mode = self.get_option('expression_mode')
        if expression_mode == 'absolute':
            sobject = None

        calc_mode = self.get_option("calc_mode")
        if not calc_mode:
            calc_mode = 'slow'
        #calc_mode = 'fast'
        # parse the expression
        parser = ExpressionParser()
        
        if calc_mode == 'fast':
            if self.cache_results == None:
                self.cache_results = parser.eval(expression, self.sobjects, vars=self.vars, dictionary=True, show_retired=self.show_retired)
                if isinstance(self.cache_results, basestring):
                    if self.cache_results:
                        self.cache_results = eval(self.cache_results)
                    else:
                        self.cache_results = {}

            search_key = sobject.get_search_key()
            result = self.cache_results.get(search_key)
            if single:
                if result and len(result):
                    result = result[0]
                else:
                    result = ''
        else:
          
            result = parser.eval(expression, sobject, vars=self.vars, single=single, list=list, show_retired=self.show_retired)



        # FIXME: don't know how to do this any other way
        try:
            if not list:
                result = result.get_display_value()
        except AttributeError, e:
            pass

        if list and result:
            # turn non basestring into string
            encoded_result = []
            for res in result:
                if isinstance(res, datetime.datetime):
                    res = SPTDate.convert_to_local(res)
                    res = str(res)
                elif not isinstance(res, basestring): 
                    res = unicode(res).encode('utf-8','ignore')

                encoded_result.append(res)

            #delimiter = ', '
            #result = delimiter.join(encoded_result)

            result = encoded_result

        if result == None or result == []:
            result = ''

       
        if isinstance(result, datetime.datetime):
            result = SPTDate.convert_to_local(result)
        return result


    def init_kwargs(self):
        '''initialize kwargs'''
        state = self.kwargs.get("state")
        if state:
            parent_key = state.get("parent_key")
            if parent_key:
                self.sobject = SearchKey.get_by_search_key(parent_key)


        self.expression = self.get_option("expression")
        if not self.expression:
            self.expression = self.kwargs.get("expression")

        self.alt_expression = self.get_option("alt_expression")
        if not self.alt_expression:
            self.alt_expression = self.kwargs.get("alt_expression")

        self.mode = self.get_option("mode")
        if not self.mode:
            self.mode = self.kwargs.get("mode")
        if not self.mode:
            self.mode = 'value'

        self.show_retired = self.get_option("show_retired")
        if not self.show_retired:
            self.show_retired = self.kwargs.get("show_retired")

        # default to False
        if self.show_retired == 'true':
            self.show_retired = True
        else:
            self.show_retired = False


        self.enable_eval_listener = False
        if self.get_option("enable_eval_listener") in [ True, "true", "True", "TRUE" ]:
            self.enable_eval_listener = True


    def get_text_value(self):
        '''for csv export'''
        self.sobject = self.get_current_sobject()

        #self.init_kwargs()
        if not self.expression and not self.alt_expression: 
            return super(ExpressionElementWdg, self).get_display()

        if self.alt_expression:
            result = self._get_result(self.sobject, self.alt_expression)
        else:
            result = self._get_result(self.sobject, self.expression)


        if isinstance(result, list):
            delimiter = ','
            result = delimiter.join(result)



        format_str = self.kwargs.get("display_format")
        if format_str:
            format_val = FormatValue()
            format_value = format_val.get_format_value( result, format_str )
            result = format_value

        name = self.get_name()
        self.sobject.set_value(name, result)
        return result


    def set_td(self, td):
        self.td = td


    def get_display(self):

        #self.init_kwargs()

        self.sobject = self.get_current_sobject()
        if not self.sobject or self.sobject.is_insert():
            return ""

        name = self.get_name()

        if not self.expression: 
            div = DivWdg()
            sobject_id = '000'
            if self.sobject:
                sobject_id = self.sobject.get_id()
            div.add_class( "spt_%s_expr_id%s" % ( name, sobject_id ) )
            div.add_class( "spt_%s_expr" % name )

            raw_result = super(ExpressionElementWdg, self).get_display()

            div.add( raw_result )
            # Now check to see if there are inline CSS styles provided ...
            inline_styles = self.kwargs.get('inline_styles')
            if inline_styles:
                style_list = inline_styles.split(";")
                for style in style_list:
                    div.add_style( style )
            return div


        try:
            use_cache = self.get_option("use_cache") in ['true', True]
            if use_cache:
                result = self.sobject.get_value(self.get_name())
            else:
                result = self._get_result(self.sobject, self.expression)


            # calculte the alt expression if defined
            # DEPRECATED: use format expression instead
            if self.alt_expression:
                self.alt_result = self._get_result(self.sobject, self.alt_expression)
            else:
                self.alt_result = result
        except Exception as e:
            print "Expression error: ", e
            print "    in column [%s] with [%s]" % (self.get_name(), self.expression)
            #from pyasm.widget import ExceptionWdg
            #widget = ExceptionWdg(e)
            #return widget
            widget = DivWdg()
            widget.add("Expression error: %s" % e)
            return widget

        if isinstance(result, list):
            delimiter = ', '
            self.value = delimiter.join(result)
            results = result
        else:
            self.value = result
            results = [result]

        if not results or (len(results) == 1 and results[0] == ''):
            empty = self.get_option("empty")
            if empty:
                div = DivWdg()
                div.add_style("white-space: nowrap")
                div.add(empty)
                div.add_style("opacity: 0.5")
                return div
            


        if self.sobject:
            # only set if the value does not exist as a key.  This widget should
            # not be able to change existing data of an sobject
            self.sobject.set_value(name, result)


        outer = DivWdg()
        for i, result in enumerate(results):
            div = DivWdg()
            outer.add(div)
            if len(results) == 1:
                div.add_style("display: inline-block")

            if self.sobject:
                div.add_class( "spt_%s_expr_id%s" % ( name, self.sobject.get_id() ) )
                div.add_class( "spt_%s_expr" % name )


            # by default, the value is added
            if self.mode == 'value':
                display_expr = self.kwargs.get("display_expression")
                format_str = self.get_option('display_format')

                if display_expr:
                    if not isinstance( result, basestring ):
                        display_result = str(result)
                    else:
                        display_result = result

                    return_type = self.kwargs.get("return")
                    if return_type == 'single':
                        single = True
                        _list = False
                    elif return_type in ['list']:
                        single = False
                        _list = True
                    else:
                        single = True
                        _list = False

                    try:
                        display_result = Search.eval(display_expr, self.sobject, list=_list, single=single, vars={'VALUE': display_result }, show_retired=self.show_retired)
                    except Exception as e:
                        print "WARNING in display expression [%s]: " % display_expr, e
                        display_result = "ERROR: %s" % e

                elif format_str:
                    # This import needs to be here because of a deep
                    # circular import
                    from tactic.ui.widget import FormatValueWdg
                    format_wdg = FormatValueWdg(format=format_str, value=result)
                    display_result = format_wdg

                else:
                    display_result = result

                return_type = self.kwargs.get("return")
                if return_type in ['list']:
                    div.add( "- " )
                    div.add_style("max-width: 400px")

                div.add( display_result )
                div.add_style("min-height: 15px")
                outer.add_style("width: 100%")



                # if a DG table td has been provided and if there is an alternate expression
                # specified then use it for the 'spt_input_value' of the td ...
                #if self.td and alt_result:
                #    self.td.set_attr("spt_input_value", str(alt_result))
                justify = self.get_option("justify")
                if justify and justify != 'default':
                    if justify != "left":
                        div.add_style("width: 100%")
                    if justify == "right":
                        div.add_style("margin-right: 10px")
                    div.add_style("text-align: %s" % justify)

                elif isinstance(result, datetime.datetime):
                    div.add_style("text-align: left")

                elif not type(result) in types.StringTypes:
                    div.add_style("text-align: right")
                    div.add_style("margin-right: 5px")

                # Now check to see if there are inline CSS styles provided ...
                inline_styles = self.kwargs.get('inline_styles')
                if inline_styles:
                    style_list = inline_styles.split(";")
                    for style in style_list:
                        div.add_style( style )


                # display a link if specified
                link_expr = self.kwargs.get("link_expression")
                if link_expr:
                    # using direct behavior because new_tab isn't working consistently
                    div.add_style("text-decoration", "underline")
                    div.add_attr("search_key", self.sobject.get_search_key())
                    div.add_attr("expression", link_expr)
                    div.add_class("hand")

                    search_type_sobj = self.sobject.get_search_type_obj()
                    sobj_title = search_type_sobj.get_title()


                    #div.add_attr("name", "%s: %s" % (sobj_title, name))
                    div.add_attr("name", display_result)

                    # click up blocks any other behavior
                    div.add_behavior( {
                        'type': 'click_up',
                        'cbjs_action': '''
                        spt.table.open_link(bvr);
                        '''
                    } )

                link_view = self.kwargs.get("link_view")
                if link_view:
                    # using direct behavior because new_tab isn't working consistently
                    div.add_style("text-decoration", "underline")
                    div.add_attr("search_key", self.sobject.get_search_key())
                    div.add_attr("view", link_view)
                    div.add_class("hand")

                    search_type_sobj = self.sobject.get_search_type_obj()
                    sobj_title = search_type_sobj.get_title()


                    #div.add_attr("name", "%s: %s" % (sobj_title, name))
                    div.add_attr("name", display_result)

                    # click up blocks any other behavior
                    div.add_behavior( {
                        'type': 'click_up',
                        'cbjs_action': '''
                        spt.table.open_link(bvr);
                        '''
                    } )






            elif self.mode == 'boolean':
                div.add_style("text-align: center")

                if not result:
                    color = 'red'
                elif result in [False, 'false']:
                    color = 'red'
                elif result in [True, 'true']:
                    color = 'green'
                else:
                    color = 'green'

                if color == 'red':
                    div.add( IconWdg("None", IconWdg.DOT_RED) )
                else:
                    div.add( IconWdg(str(result), IconWdg.DOT_GREEN) )
            elif self.mode == 'check':
                div.add_style("text-align: center")
                try:
                    value = int(result)
                except ValueError:
                    value = 0
                if value > 0:
                    div.add( IconWdg(str(result), IconWdg.CHECK) )
                else:
                    div.add( '&nbsp;' )
            elif self.mode == 'icon':
                if not result:
                    result = 0
                vars = {
                    'VALUE': result
                }
                icon_expr = self.get_option("icon_expr")
                icon = Search.eval(icon_expr, vars=vars)
                icon = str(icon).upper()
                div.add_style("text-align: center")
                try:
                    icon_wdg = eval("IconWdg.%s" % icon)
                except:
                    icon = "ERROR"
                    icon_wdg = eval("IconWdg.%s" % icon)
                div.add( IconWdg(str(result), icon_wdg ) )
            else:
                raise TacticException("Unsupported expression display mode [%s] for column [%s]" % (self.mode, self.get_name() ))


            if self.sobject and self.enable_eval_listener:
                self.add_js_expression(div, self.sobject, self.expression)

            # test link
            #link = self.get_option("link")
            #if link:
            #    div.add_behavior( {
            #        'type': 'click_up',
            #        'cbjs_action': 'document.location = "http://%s"' % link
            #    } )


            # test behavior
            behavior = self.get_option("behavior")
            if behavior:
                behavior = behavior.replace('\\\\', '\\')
                behavior = jsonloads(behavior)
                if behavior.get("type") in ['click_up', 'click']:
                    div.add_class('hand')

                behavior['cbjs_action'] = '''
                var search_key = bvr.src_el.getParent('.spt_table_tbody').getAttribute('spt_search_key');
                bvr = {
                    script_code: '61MMS',
                    search_key: search_key
                };
                spt.CustomProject.custom_script(evt, bvr);
                '''
                div.add_behavior( behavior )


        """
        # test dynamic updates on expressions
        if self.get_name() == "customer":
            outer.add_update( {
                'search_key': self.sobject.get_search_key(),
                'column': "customer_code",
                'interval': 4,
                'cbjs_action': "spt.panel.refresh_element(bvr.src_el)",
            } )

        self.set_as_panel(outer);
        """

        return outer


 

    def get_bottom_wdg(self):

        self.init_kwargs()

        sobjects = self.sobjects
        # ignore the first 2 (edit and insert) if it's on the old TableLayoutWdg
        if self.get_layout_wdg().get_layout_version() == '1':
            sobjects = sobjects[2:]
        
        if not sobjects:
            return None


        expression = self.get_option("bottom")
        if not expression:
            return None

        # parse the expression
        self.vars = self.get_vars()
 
        parser = ExpressionParser()
        result = parser.eval(expression, sobjects=sobjects, vars=self.vars)

        format_str = self.kwargs.get("display_format")
        if format_str:
            from tactic.ui.widget import FormatValueWdg
            format_wdg = FormatValueWdg(format=format_str, value=result)
            result = format_wdg
        else:
            result = str(result)

        div = DivWdg()
        div.add(result)
        div.add_style("text-align: right")
        div.add_class( "spt_%s_expr_bottom" % (self.get_name()) )

        # add a listener
        for sobject in sobjects:
            if sobject.is_insert():
                continue
            if self.enable_eval_listener:
                self.add_js_expression(div, sobject, expression)

        return div


 

    def get_group_bottom_wdg(self, sobjects):

        expression = self.get_option("group_bottom")
        if not expression:
            return None

        # parse the expression
        self.vars = self.get_vars()
 
        parser = ExpressionParser()
        raw_result = parser.eval(expression, sobjects=sobjects, vars=self.vars)

        format_str = self.kwargs.get("display_format")
        if format_str:
            from tactic.ui.widget import FormatValueWdg
            format_wdg = FormatValueWdg(format=format_str, value=raw_result)
            result = format_wdg
        else:
            result = str(raw_result)



        div = DivWdg()
        div.add(result)
        div.add_style("text-align: right")
        #div.add_class( "spt_%s_expr_bottom" % (self.get_name()) )


        # add a listener
        #for sobject in sobjects:
        #    if sobject.is_insert():
        #        continue
        #
        #    if self.enable_eval_listener:
        #        self.add_js_expression(div, sobject, expression)

        return div, raw_result





    def add_js_expression(self, widget, sobject, expression):

        js_expression, columns = self.convert_to_js(sobject, expression)

        element_name = self.get_name()

        for column in columns:
            # ignore itself
            #if column == element_name:
            #    continue

            search_key = SearchKey.get_by_sobject(sobject)
            event_name = 'change|%s|%s' % (search_key, column)
            behavior = {
                'type': 'listen',
                'event_name': event_name,
                'expression': js_expression,
                'cbjs_action': 'spt.expression.calculate_cbk(evt, bvr)'
            }
            widget.add_behavior(behavior)


 
    def convert_to_js(self, sobject, expression):

        # HACK!!: to very robust implementation
        pattern = re.compile('@(\w+)\((.*?)\)')
        matches = pattern.findall(expression)
        if not matches:
            return '', expression

        js_expression = expression
        columns = []

        for match in matches:
            method = match[0]
            item = match[1]

            if method == 'GET':
                search_key = SearchKey.build_by_sobject(sobject)

                parts = item.split(".")
                column = parts[-1]
                replace = '"%s","%s"' % (search_key, parts[-1])

                columns.append(column)

                
            else:
                parts = item.split(".")
                column = parts[-1]
                replace = '"%s"' % column

                columns.append(column)

            js_expression = js_expression.replace(item, replace)


        return js_expression, columns




__all__.append("ExpressionRecalculateCmd")
from pyasm.command import Command
class ExpressionRecalculateCmd(Command):

    def execute(self):

        search_keys = self.kwargs.get("search_keys")
        if not search_keys:
            return


        element_name = self.kwargs.get("element_name")


        # get all of the sobjects
        sobjects = Search.get_by_search_keys(search_keys)
        if not sobjects:
            return

        from pyasm.widget import WidgetConfigView
        search_type = sobjects[0].get_base_search_type()
        view = "definition"

        config = WidgetConfigView.get_by_search_type(search_type, view)

        # TEST
        widget = config.get_display_widget(element_name)
        for sobject in sobjects:
            widget.set_sobject(sobject)
            value = widget.get_text_value()
            sobject.set_value(element_name, value)
            sobject.commit()


        #for result, sobject in zip(results, sobjects):
        #    sobject.set_value(element_name, result)
        #    sobject.commit()




class ExpressionValueElementWdg(SimpleTableElementWdg):

    ARGS_KEYS = {
    }

    def is_editable(self):
        return True

    def get_text_value(self):

        sobject = self.get_current_sobject()
        if sobject.is_insert():
            return

        value = self.get_value()

        # assume the value is an expression
        try:
            value = Search.eval(value)
        except Exception as e:
            value = 0

        return value

    def get_display(self):

        sobject = self.get_current_sobject()
        if sobject.is_insert():
            return

        value = self.get_value()

        # assume the value is an expression
        try:
            value = Search.eval(value)
        except Exception as e:
            print e.message
            value = "Error [%s]" % value

        return "%s" % value



