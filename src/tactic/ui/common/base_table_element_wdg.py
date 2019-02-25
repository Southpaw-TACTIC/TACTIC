###########################################################
#
# Copyright (c) 2005-2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['BaseTableElementWdg', 'RawTableElementWdg', 'SimpleTableElementWdg', 'WidgetTableElementWdg']

import types
import locale
from pyasm.widget import BaseTableElementWdg as FormerBaseTableElementWdg
from pyasm.web import WikiUtil, DivWdg, Widget
from pyasm.common import Date, SPTDate, Common, TacticException
from pyasm.search import Search, SearchType, SObject

from pyasm.command import Command, ColumnDropCmd, ColumnAlterCmd, ColumnAddCmd, ColumnAddIndexCmd
from base_refresh_wdg import BaseRefreshWdg
from pyasm.biz import PrefSetting
from dateutil import parser

class BaseTableElementWdg(BaseRefreshWdg, FormerBaseTableElementWdg):
    '''remaps the old BaseTableElementWdg to use BaseRefreshWdg'''

    def __init__(self, **kwargs):
        # Handle the base refresh directly instead of calling __init__.
        # This is because FormerBaseTableelementWdg also does the same
        # thing causing a buch of function to be run twice
        #BaseRefreshWdg.__init__(self, **kwargs)
        self.top = DivWdg()
        self.handle_args(kwargs)

        FormerBaseTableElementWdg.__init__(self, **kwargs)
        
    def get_args_keys(cls):
        '''external settings which populate the widget'''
        return cls.ARGS_KEYS
    get_args_keys = classmethod(get_args_keys)




    def set_attributes(self, attrs):
        '''set attributes dict like access, width, or edit'''
        self.attributes = attrs

    def handle_th(self, th, wdg_idx=None):

        order_by = self.get_option("order_by")

        if order_by:
            # backward-compatible with true or false, don't set this
            # it will retrieve the element name instead thru js 
            if order_by not in ['true', 'false']:
                th.set_attr("spt_order_by", order_by)

        self.add_simple_search(th)


    def add_simple_search(self, th):

        filter_name = self.get_option("filter_name")
        if not filter_name:
            filter_name = self.get_name()


        th.add_style("position: relative")
        filter_wdg = self.get_filter_wdg(filter_name)
        th.add( filter_wdg )
        filter_wdg.add_style("position: absolute")
        filter_wdg.add_style("right: 8px")
        filter_wdg.add_style("width: 25px")
        filter_wdg.add_style("top: 10px")
        filter_wdg.add_style("display: none")


        th.add_behavior( {
            'type': 'mouseenter',
            'element_name': filter_name,
            'cbjs_action': '''
            if (!spt.simple_search) {
                return;
            }

            if (!spt.simple_search.has_element(bvr.element_name) ) {
                return;
            }

            var el = bvr.src_el.getElement(".spt_filter_button");
            el.setStyle("display", "");
            '''
        } )

        th.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            var el = bvr.src_el.getElement(".spt_filter_button");
            el.setStyle("display", "none");
            '''
        } )



    def _add_css_style(self, element, prefix, name=None, value=None):
        # skip the edit/ insert row
        #sobject = self.get_current_sobject()
        #if not sobject or sobject.get_id() == -1:
        #    return

        if value is None:
            value = self.get_value()
        if name is None:
            name = self.get_name()

        if not value:
            value = 0
        
        vars = {
            "ELEMENT":  name,
            "VALUE":    value
        }

        for key, expr in self.kwargs.items():
            if not key.startswith(prefix):
                continue

            if expr:
                sobject = self.get_current_sobject()
                prefix, property = key.split("_", 1)
                value = Search.eval(expr, sobject, vars=vars)
                if value:
                    element.add_style("%s: %s" % (property, value) )



 
    def handle_td(self, td):
        name = self.name
        value = self.value
        self._add_css_style(td, 'css_', name, value)

       

    def handle_tr(self, tr):
        name = self.name
        value = self.value
        self._add_css_style(tr, 'rowcss_', name, value)


    def get_title(self):
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


    def get_filter_wdg(self, filter_name):

        if not filter_name:
            filter_name = self.get_name()

        from pyasm.web import DivWdg
        from tactic.ui.widget import IconButtonWdg
        filter_wdg = DivWdg()
        button = IconButtonWdg(title="Show Filter", icon="BS_SEARCH")
        filter_wdg.add_class("spt_filter_button")


        filter_wdg.add(button)
        filter_wdg.add_style("display: inline-block")
        filter_wdg.add_style("vertical-align: middle")
        filter_wdg.add_style("opacity: 0.5")

        filter_wdg.add_attr("spt_filter_name", filter_name)
        filter_wdg.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var panel = bvr.src_el.getParent(".spt_view_panel_top");
            var th = bvr.src_el.getParent("th");
            var pos = th.getPosition(panel);

            var name = bvr.src_el.getAttribute("spt_filter_name");

            if (! spt.simple_search.has_element(name) ) {
                return;
            }

            pos.y += 35;


            spt.simple_search.show_elements([name]);
            spt.simple_search.set_position(pos);
            spt.simple_search.hide_title();
            spt.simple_search.show();

            var top = spt.simple_search.get_top();
            var size = top.getSize();
            var cur_pos = top.getPosition( document.id(document.body) );
            var window_size = document.id(document.body).getSize();
            if (cur_pos.x + size.x > window_size.x) {
                var panel_size = panel.getSize();
                pos.x = panel_size.x - size.x;
                spt.simple_search.set_position(pos);
            }

            '''
        } )



        return filter_wdg



    def create_required_columns(self, search_type):
        columns = self.get_required_columns()
        data_type = "varchar"
        for column_name in columns:
            cmd = ColumnAddCmd(search_type, column_name, data_type)
            cmd.execute()




    def get_required_columns(self):
        '''method to get the require columns for this'''
        return []



    def is_editable(cls):
        '''Determines whether this element is editable'''
        return True
    is_editable = classmethod(is_editable)

    def get_sort_prefix(self):
        return None

    def is_sortable(self):
        order_by = self.get_option("order_by")
        if order_by:
            return True
        else:
            return False


    def is_groupable(self):
        order_by = self.get_option("order_by")
        if order_by:
            return True
        else:
            return False

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
 
    def get_text_value(self):
        return self.get_value()

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



class RawTableElementWdg(BaseTableElementWdg):
    '''This shows the data as TACTIC stores it internally, unaltered by
    formatting'''

    def get_title(self):
        name = self.get_name()
        return name

    def is_sortable(self):
        return True

    def get_required_columns(self):
        '''method to get the require columns for this'''
        return [
        self.get_name()
        ]
    
    def get_display(self):
        sobject = self.get_current_sobject()
        name = self.get_name()
        value = self.get_value()

        if sobject:
            data_type = SearchType.get_column_type(sobject.get_search_type(), name)
        else:
            data_type = 'text'

        if data_type in ["timestamp","time"] or self.name == "timestamp":
            if value == 'now':
                value = ''
            elif value:
                date = parser.parse(value)
                # we want to match what's in the db which is server local timezone
                if not SPTDate.has_timezone(value):
                    value = SPTDate.convert_to_local(value)
                #value = SPTDate.add_gmt_timezone(date)
                value = str(value)
            else:
                value = ''

        return value

     



class SimpleTableElementWdg(BaseTableElementWdg):
    '''This is the default table element widget.  It simply takes the value
    of the sobject draws it as a string'''


    ARGS_KEYS = {
        'type': {
            'description': 'Determine the type it should be displayed as',
            'type': 'SelectWdg',
            'values': 'string|text|integer|float|boolean|timestamp',
            'category': 'Database'
        },
        'total_summary': {
            'description': 'Determine a calculation for the bottom row',
            'type': 'SelectWdg',
            'values': 'count|total|average',
            'category': 'Summary'
        },
        'column': {
            'description': 'Determine the database column to display',
            'type': 'TextWdg',
            'category': 'Display'
        },
        'single_line': {
            'description': 'Determines if the text is displayed as a single line',
            'type': 'SelectWdg',
            'values': 'false|true',
            'category': 'Display'
        }

    }


    def get_required_columns(self):
        '''method to get the require columns for this'''
        return [
        self.get_name()
        ]

    def create_required_columns(self, search_type):
        columns = self.get_required_columns()
        data_type = self.get_option("type")

        constraint = self.get_option("constraint")

        for column_name in columns:
            try:
                column_exist_error = None
                cmd = ColumnAddCmd(search_type, column_name, data_type)
                cmd.execute()
            except TacticException as e:
                if 'already existed in this table' in e.__str__():
                    column_exist_error = e
                else:
                    raise 
            finally:
                if constraint:
                    cmd = ColumnAddIndexCmd(search_type=search_type, column=column_name, constraint=constraint)
                    cmd.execute()
                if column_exist_error:
                    raise column_exist_error



    def is_editable(cls):
        '''Determines whether this element is editable'''
        return True
    is_editable = classmethod(is_editable)

    def is_groupable(self):
        return True


    def is_time_groupable(self):
        return False

    def get_simple_display(self):
        value = self.get_value()
        if self.name == "timestamp":
            date = parser.parse(value)
            value = date.strftime("%b %m - %H:%M")
        else:
            if not isinstance(value, basestring):
                value = str(value)

        if not value:
            value = ""
        
        return value




    def get_vars(self):
        # create variables
        element_name = self.get_name()
        self.vars = {
            'ELEMENT_NAME': element_name
        }

        # get info from search critiera
        # FIXME: this should be formalized
        #search_vars = Container.get("Message:search_vars")
        #if search_vars:
        #    for name, value in search_vars.items():
        #        self.vars[name] = value

        return self.vars


   
    def get_group_bottom_wdg(self, sobjects):

        summary = self.get_option("total_summary")
        if not summary:
            return None

        # parse the expression
        self.vars = self.get_vars()
 
        expression, title = self.get_expression(summary)
        try:
            result = Search.eval(expression, sobjects=sobjects, vars=self.vars)
        except Exception as e:
            print "WARNING: ", e.message
            result = 0
            title = ''

        div = DivWdg()
        div.add(str(result))
        div.add_style("text-align: right")

        return div, result



    def get_expression(self, summary):
        if summary == 'total':
            expression = '@SUM(.%s)' % self.get_name()
            title = "Total: "
        elif summary == 'average':
            expression = '@AVG(.%s)' % self.get_name()
            title = "Avg: "
        else:
            expression = '@COUNT()'
            title = "Count: "

        return expression, title



    def check_bottom_wdg(self):
        '''return a dictionary to indicate if the user has enabled this bottom wdg or 
            if there is data worth drawing'''

        info = {}
        # For the old table only, ignore the first 2 (edit and insert)!
        if self.get_layout_wdg().get_layout_version() == '1':
            sobjects = self.sobjects[2:]
        else:
            sobjects = self.sobjects

        if not sobjects:
            info['check'] = False
            return info

        summary = self.get_option("total_summary")
        if not summary:
            info['check'] = False
            return info

        # store the kind of summary, since some widget may not support all modes
        info['mode'] = summary
        

        
        # parse the expression
        self.vars = self.get_vars()

        expression, title = self.get_expression(summary)
        try:
            info['check'] = True
            result = Search.eval(expression, sobjects=sobjects, vars=self.vars)
        except Exception as e:
            print("WARNING: ", e.message)
            result = "Calculation Error"
            title = ''

        info['result'] = result
        info['title'] = title

        return info


    def get_bottom_wdg(self):
        # check if the user has enabled it 
        info = self.check_bottom_wdg()
        if info.get('check') == False:
            return None

        
        title = info.get('title')
        result = info.get('result')

        div = DivWdg()
        div.add(title)
        div.add(str(result))
        div.add_style("text-align: right")
        div.add_class( "spt_%s_expr_bottom" % (self.get_name()) )


        # DEPRECATED until we have a better solution
        # add a listener
        '''
        for sobject in sobjects:
            if sobject.is_insert():
                continue

            # DISABLE this for simple
            #if self.enable_eval_listener:
            #    self.add_js_expression(div, sobject, expression)
        '''

        return div



    def add_value_update(self, value_wdg, sobject, name):
        value_wdg.add_update( {
            'search_key': sobject.get_search_key(),
            'column': name,
            'interval': 4,
        } )
 

    def get_display(self):
        sobject = self.get_current_sobject()

        column =  self.kwargs.get('column')
        if column:
            name = column
        else:
            name = self.get_name()
        
        value = self.get_value(name=name)

        empty = self.get_option("empty")
        if empty and self.is_editable() and not value:
            from pyasm.web import SpanWdg
            div = DivWdg()
            div.add_style("text-align: center")
            div.add_style("width: 100%")
            div.add_style("white-space: nowrap" )
            if empty in [True, 'true']:
                div.add("--Select--")
            div.add_style("opacity: 0.5")
            return div




        if sobject:
            data_type = SearchType.get_column_type(sobject.get_search_type(), name)
        else:
            data_type = 'text'

        if type(value) in types.StringTypes:
            wiki = WikiUtil()
            value = wiki.convert(value) 
        if name == 'id' and value == -1:
            value = ''

        elif data_type in ["timestamp","time"] or name == "timestamp":
            if value == 'now':
                value = ''
            elif value:
                # This date is assumed to be GMT
                date = parser.parse(value)
                # convert to user timezone
                if not SObject.is_day_column(name):
                    date = self.get_timezone_value(date)
                try:
                    encoding = locale.getlocale()[1]		
                    value = date.strftime("%b %d, %Y - %H:%M").decode(encoding)
                except:
                    value = date.strftime("%b %d, %Y - %H:%M")

            else:
                value = ''
        elif isinstance(value, dict) and not value:
            value = ""
        else:
            if isinstance(value, Widget):
                return value
            elif not isinstance(value, basestring):
                try:
                    value + 1
                except TypeError:
                    value = str(value)
                #else:
                #    value_wdg.add_style("float: right")
                #    value_wdg.add_style("padding-right: 3px")


        min_height = self.get_option("min_height") or 25
        single_line = self.get_option("single_line") or False

        value_wdg = DivWdg()
        if single_line in ["true", True]:
            value_wdg.add_style("line-height: %spx" % min_height)
            value_wdg.add_style("white-space: nowrap")
            value_wdg.add_style("overflow-y: hidden")

        value_wdg.add_style("overflow-x: hidden")
        value_wdg.add_style("text-overflow: ellipsis")


        # some properties
        value_wdg.add_style("min-height: %spx" % min_height)

        if sobject and SearchType.column_exists(sobject.get_search_type(), name):

            self.add_value_update(value_wdg, sobject, name)

            # don't call str() to prevent utf-8 encode error
            value_wdg.add(value)



            link_expression = self.get_option("link_expression")
            if link_expression:
                value_wdg.add_class("tactic_new_tab")
                value_wdg.add_style("display: inline-block")
                value_wdg.add_attr("search_key", sobject.get_search_key())
                value_wdg.add_style("text-decoration: underline")
                #value_wdg.add_attr("spt_class_name", "tactic.ui.tools.SObjectDetailWdg")
                value_wdg.add_class("hand")

        else:
            value_wdg.add(value)


        # TEST: loading values dynamically using javascript
        """
        value_wdg.add_attr("spt_value", value)
        value_wdg.add_attr("spt_name", name)
        value_wdg.add_class("spt_update_cellX")
        value_wdg.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            bvr.src_el.update = function(data) {
                var el = document.id(this);
                var name = el.getAttribute("spt_name");
                var value = data[name];
                el.innerHTML = value + "!!!";

            }

            var name = bvr.src_el.getAttribute("spt_name");
            var value = bvr.src_el.getAttribute("spt_value");
            var data = {};
            data[name] = value;
            bvr.src_el.update( data );
            '''
        } )
        """


        return value_wdg


    def is_sortable(self):
        return True



class WidgetTableElementWdg(BaseTableElementWdg):

    def get_display(self):
        top = self.top
        for widget in self.widgets:
            top.add(widget)
        return top

