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

from pyasm.widget import BaseTableElementWdg as FormerBaseTableElementWdg
from pyasm.web import WikiUtil, DivWdg, Widget
from pyasm.common import SPTDate
from pyasm.common import Date, Common
from pyasm.search import Search, SearchType

from pyasm.command import Command, ColumnDropCmd, ColumnAlterCmd, ColumnAddCmd, ColumnAddIndexCmd
from base_refresh_wdg import BaseRefreshWdg

from dateutil import parser

class BaseTableElementWdg(BaseRefreshWdg, FormerBaseTableElementWdg):
    '''remaps the old BaseTableElementWdg to use BaseRefreshWdg'''

    def __init__(my, **kwargs):
        BaseRefreshWdg.__init__(my, **kwargs)
        FormerBaseTableElementWdg.__init__(my, **kwargs)


    def get_args_keys(cls):
        '''external settings which populate the widget'''
        return cls.ARGS_KEYS
    get_args_keys = classmethod(get_args_keys)




    def handle_th(my, th, wdg_idx=None):

        order_by = my.get_option("order_by")

        if order_by:
            # backward-compatible with true or false, don't set this
            # it will retrieve the element name instead thru js 
            if order_by not in ['true', 'false']:
                th.set_attr("spt_order_by", order_by)



    def _add_css_style(my, element, prefix):
        # skip the edit/ insert row
        sobject = my.get_current_sobject()
        if not sobject or sobject.get_id() == -1:
            return

        value = my.get_value()
        name = my.get_name()

        if not value:
            value = 0
        
        vars = {
            "ELEMENT":  name,
            "VALUE":    value
        }

        for key, expr in my.kwargs.items():
            if not key.startswith(prefix):
                continue

            if expr:
                prefix, property = key.split("_", 1)
                value = Search.eval(expr, sobject, vars=vars)
                if value:
                    element.add_style("%s: %s" % (property, value) )
 
    def handle_td(my, td):
        my._add_css_style(td, 'css_')
       

    def handle_tr(my, tr):
        my._add_css_style(tr, 'rowcss_')


    def get_title(my):
        if my.title:
            title = my.title
            title = title.replace(r'\n','<br/>')
        else:
            title = my.name

            if not title:
                title = ""

            else:
                title = Common.get_display_title(title)
        from pyasm.web import DivWdg
        div = DivWdg()
        div.add_attr("title", title)
        div.add(title)
        return div

        # FIXME: not sure about autofit here?  This should be a mode
        """
        div = DivWdg()
        div.add_attr("title", title)
        inner = DivWdg()
        inner.add_style("width: 100%")
        
        autofit = my.view_attributes.get('autofit')
        if autofit != 'false':
            div.add_style("width: 1px")
            inner.add_style("white-space: nowrap")
        inner.add(title)
        div.add(inner)
        return div
        """



    def create_required_columns(my, search_type):
        columns = my.get_required_columns()
        data_type = "varchar"
        for column_name in columns:
            cmd = ColumnAddCmd(search_type, column_name, data_type)
            cmd.execute()




    def get_required_columns(my):
        '''method to get the require columns for this'''
        return []



    def is_editable(cls):
        '''Determines whether this element is editable'''
        return True
    is_editable = classmethod(is_editable)


    def is_sortable(my):
        order_by = my.get_option("order_by")
        if order_by:
            return True
        else:
            return False


    def is_groupable(my):
        order_by = my.get_option("order_by")
        if order_by:
            return True
        else:
            return False

   
    def get_text_value(my):
        return my.get_value()

    def alter_order_by(my, search, direction=''):
        '''handle order by??'''
        order_by = my.get_option("order_by")

        if order_by:
            search.add_order_by(order_by, direction)
        else:
            search.add_order_by(my.get_name(), direction)

        # some order by's require a specific where clause in order to filter
        # down a join sufficiently.
        order_by_where = my.get_option("order_by_where")
        if order_by_where:
            search.add_where(order_by_where)



class RawTableElementWdg(BaseTableElementWdg):
    '''This shows the data as TACTIC stores it internally, unaltered by
    formatting'''

    def get_title(my):
        name = my.get_name()
        return name

    def get_display(my):
        sobject = my.get_current_sobject()
        name = my.get_name()
        value = my.get_value()

        if sobject:
            data_type = SearchType.get_column_type(sobject.get_search_type(), name)
        else:
            data_type = 'text'

        if data_type == "timestamp" or my.name == "timestamp":
	    if value == 'now':
                value = ''
            elif value:
                date = parser.parse(value)
                value = SPTDate.add_gmt_timezone(date)
                value = str(value)
            else:
                value = ''

        return value

     



class SimpleTableElementWdg(BaseTableElementWdg):
    '''This is the default table element widget.  It simply takes the value
    of the sobject draws it as a string'''


    ARGS_KEYS = {
    'type': {
        'description': 'Determines the type it should be displayed as',
        'type': 'SelectWdg',
        'values': 'string|text|integer|float|boolean|timestamp',
        'category': 'Database'
    },
    'total_summary': {
        'description': 'Determines a calculation for the bottom row',
        'type': 'SelectWdg',
        'values': 'count|total|average',
        'category': 'Summary'
    }
    }


    def get_required_columns(my):
        '''method to get the require columns for this'''
        return [
        my.get_name()
        ]

    def create_required_columns(my, search_type):
        columns = my.get_required_columns()
        data_type = my.get_option("type")

        constraint = my.get_option("constraint")

        for column_name in columns:
            cmd = ColumnAddCmd(search_type, column_name, data_type)
            cmd.execute()

            if constraint:
                cmd = ColumnAddIndexCmd(search_type=search_type, column=column_name, constraint=constraint)
                cmd.execute()



    def is_editable(cls):
        '''Determines whether this element is editable'''
        return True
    is_editable = classmethod(is_editable)

    def is_groupable(my):
        return True


    def is_time_groupable(my):
        return False

    def get_simple_display(my):
        value = my.get_value()
        if my.name == "timestamp":
            date = parser.parse(value)
            value = date.strftime("%b %m - %H:%M")
        else:
            if not isinstance(value, basestring):
                value = str(value)

        if not value:
            value = ""
        
        return value




    def get_vars(my):
        # create variables
        element_name = my.get_name()
        my.vars = {
            'ELEMENT_NAME': element_name
        }

        # get info from search critiera
        # FIXME: this should be formalized
        #search_vars = Container.get("Message:search_vars")
        #if search_vars:
        #    for name, value in search_vars.items():
        #        my.vars[name] = value

        return my.vars



    def get_group_bottom_wdg(my, sobjects):

        summary = my.get_option("total_summary")
        if not summary:
            return None

        # parse the expression
        my.vars = my.get_vars()
 
        expression, title = my.get_expression(summary)
        try:
            result = Search.eval(expression, sobjects=sobjects, vars=my.vars)
        except Exception, e:
            print "WARNING: ", e.message
            result = "Calculation Error"
            title = ''

        div = DivWdg()
        div.add(str(result))
        div.add_style("text-align: right")

        return div



    def get_expression(my, summary):
        if summary == 'total':
            expression = '@SUM(.%s)' % my.get_name()
            title = "Total: "
        elif summary == 'average':
            expression = '@AVG(.%s)' % my.get_name()
            title = "Avg: "
        else:
            expression = '@COUNT()'
            title = "Count: "

        return expression, title



    def check_bottom_wdg(my):
        '''return a dictionary to indicate if the user has enabled this bottom wdg or 
            if there is data worth drawing'''

        info = {}
        # For the old table only, ignore the first 2 (edit and insert)!
        if my.get_layout_wdg().get_layout_version() == '1':
            sobjects = my.sobjects[2:]
        else:
            sobjects = my.sobjects

        if not sobjects:
            info['check'] = False
            return info

        summary = my.get_option("total_summary")
        if not summary:
            info['check'] = False
            return info

        # store the kind of summary, since some widget may not support all modes
        info['mode'] = summary
        

        
        # parse the expression
        my.vars = my.get_vars()

        expression, title = my.get_expression(summary)
        try:
            info['check'] = True
            result = Search.eval(expression, sobjects=sobjects, vars=my.vars)
        except Exception, e:
            print "WARNING: ", e.message
            result = "Calculation Error"
            title = ''

        info['result'] = result
        info['title'] = title

        return info


    def get_bottom_wdg(my):
        # check if the user has enabled it 
        info = my.check_bottom_wdg()
        if info.get('check') == False:
            return None

        
        title = info.get('title')
        result = info.get('result')

        div = DivWdg()
        div.add(title)
        div.add(str(result))
        div.add_style("text-align: right")
        div.add_class( "spt_%s_expr_bottom" % (my.get_name()) )


        # DEPRECATED until we have a better solution
        # add a listener
        '''
        for sobject in sobjects:
            if sobject.is_insert():
                continue

            # DISABLE this for simple
            #if my.enable_eval_listener:
            #    my.add_js_expression(div, sobject, expression)
        '''

        return div




    def get_display(my):
        sobject = my.get_current_sobject()
        name = my.get_name()
        value = my.get_value()

        if sobject:
            data_type = SearchType.get_column_type(sobject.get_search_type(), name)
        else:
            data_type = 'text'

        if type(value) in types.StringTypes:
            wiki = WikiUtil()
            value = wiki.convert(value) 
        if name == 'id' and value == -1:
            value = ''

        elif data_type == "timestamp" or my.name == "timestamp":
	    if value == 'now':
                value = ''
            elif value:
                # This date is assumed to be GMT
                date = parser.parse(value)
                # convert to local
                date = SPTDate.convert_to_local(date)

		value = date.strftime("%b %d, %Y - %H:%M")
            else:
                value = ''
        else:
            if isinstance(value, Widget):
                return value
            if not isinstance(value, basestring):
                value_wdg = DivWdg()
                value_wdg.add_style("float: right")
                value_wdg.add_style("padding-right: 3px")
                value_wdg.add( str(value) )
                return value_wdg

        return value

    def is_sortable(my):
        return True



class WidgetTableElementWdg(BaseTableElementWdg):

    def get_display(my):
        top = my.top
        for widget in my.widgets:
            top.add(widget)
        return top

