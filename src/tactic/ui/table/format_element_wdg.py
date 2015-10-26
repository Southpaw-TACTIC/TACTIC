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


__all__ = ['FormatElementWdg']

import re, datetime

from pyasm.common import TimeCode
from pyasm.search import SObject, Search, SearchKey, SearchType
from pyasm.web import DivWdg, WebContainer, SpanWdg, Widget
from pyasm.biz import Schema, Project, ProdSetting, PrefSetting
from pyasm.widget import HiddenWdg, IconWdg

from tactic.ui.common import SimpleTableElementWdg

from dateutil import parser

class FormatElementWdg(SimpleTableElementWdg):


    ARGS_KEYS = {
    'type': {
        'description': 'Determines the type it should be displayed as',
        #'type': 'SelectWdg',
        'type': 'tactic.ui.manager.FormatDefinitionEditWdg',
        'values': 'integer|float|percent|currency|date|time|scientific|boolean|text|timecode',
        'category': 'Display',
        'default': 'text',
        'order': 0
    },
    'total_summary': {
        'description': 'Determines a calculation for the bottom row',
        'type': 'SelectWdg',
        'values': 'count|total|average',
        'category': 'Summary'
    },
    'format': {
        'description': 'display format',
        'category': 'internal',
        'sub_keys': ['fps']
    },

    'constraint': {
        'description': 'Determines what kind of index is put onto the created column',
        'category': 'Database',
        'type': 'SelectWdg',
        'values': 'unique|indexed',
        'order': 2
    }

    }


    def handle_layout_behaviors(my, layout):
        layout.add_relay_behavior( {
        'type': 'mouseup',
        #'propagate_evt': True, # not sure if this works
        'bvr_match_class': 'spt_format_checkbox_%s' % my.get_name(),
        'cbjs_action': '''
        var layout = bvr.src_el.getParent(".spt_layout");
        var version = layout.getAttribute("spt_version");
        if (version == "2") {
            var value_wdg = bvr.src_el;
            var checkbox = value_wdg.getElement(".spt_input");
            // FIXME: Not sure why we have to replicate checkbox basic behavior ...
            if (checkbox.checked) {
                checkbox.checked = false;
            }
            else{
                checkbox.checked = true;
            }

            spt.table.set_layout(layout);
            spt.table.accept_edit(checkbox, checkbox.checked, false)

        }
        else {
            var cached_data = {};
            var value_wdg = bvr.src_el;
            var top_el = bvr.src_el.getParent(".spt_boolean_top");
            spt.dg_table.edit.widget = top_el;
            var key_code = spt.kbd.special_keys_map.ENTER;
            spt.dg_table.inline_edit_cell_cbk( value_wdg, cached_data );
        }
        '''
        } )


    def get_width(my):
        widget_type = my.get_option("type")
        if widget_type in ['integer']:
            return 30
        elif widget_type in ['float', 'date', 'timecode', 'currency']:
            return 80
        else:
            return 100



    def get_display(my):

        top = DivWdg()

        value = my.get_value()
        widget_type = my.get_option("type")
        
        if widget_type in ['integer', 'float', 'timecode', 'currency']:
            top.add_style("float: right")
            my.justify = "right"

        elif widget_type in ['date','time']:
            name = my.get_name()
            if value and not SObject.is_day_column(name):               
                value = my.get_timezone_value(value)
         

                value = str(value)

        else:
            top.add_style("float: left")
            my.justify = "left"
        top.add_style("padding-right: 3px")

        top.add_style("min-height: 15px")

        format = my.get_option('format')
        value = my.get_format_value( value, format )

        top.add(value)

        return top

    def get_text_value(my):

        value = my.get_value()
        widget_type = my.get_option("type")
        
        if widget_type in ['date','time']:
            name = my.get_name()
            if not SObject.is_day_column(name):
                value = my.get_timezone_value(value)
                value = str(value)
 
        format = my.get_option('format')
        
        if format == 'Checkbox':
            value = str(value)
        else:
            value = my.get_format_value( value, format )

       
        return value

    def get_bottom_wdg(my):
        # check if the user has enabled it
        info = my.check_bottom_wdg()

        if info.get('check') == False:
            return None

        
        title = info.get('title')
        result = info.get('result')
        format = my.get_option('format')
        result = my.get_format_value( result, format )

        div = DivWdg()
        div.add(title)
        div.add(str(result))
        div.add_style("text-align: right")
        div.add_class( "spt_%s_expr_bottom" % (my.get_name()) )
        return div



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
        """
        widget_type = my.get_option("type")
        
        if widget_type in ['date','time']:
            name = my.get_name()
            if not SObject.is_day_column(name):
                result = SPTDate.convert_to_local(result)
                result= str(result)
        """
        format = my.get_option('format')
        formatted_result = my.get_format_value( result, format )

        div = DivWdg()
        div.add(str(formatted_result))
        div.add_style("text-align: right")

        return div, result



    def convert_to_float(my, num):
        try:
            num = float(num)
        except:
            num = 0
        return num


    def number_format(my, num, places=0):
        """Format a number according to locality and given places"""
        import locale
        locale.setlocale(locale.LC_ALL, "")
        return locale.format("%.*f", (places, num), True)

    def currency_format(my, num, grouping=False, monetary=False):
        """Format a currency according to locality and given places"""
        import locale
        locale.setlocale(locale.LC_ALL, "")
        try:
            num = float(num)
        except ValueError, e:
            num = 0
        return locale.currency(num, True, grouping, monetary)

   
    def get_format_value(my, value, format):
        if format not in ['Checkbox'] and value == '':
            return ''
        # ------------------------------------------------
        # Integer
        if format == '-1234':
            if not value:
                # Case where value is '', 0, 0.0, -0.0 . 
                value = 0
            value = "%0.0f" % my.convert_to_float(value)

        elif format == '-1,234':
            if not value:
                value = 0
            # Group the value into three numbers seperated by a comma.
            value = my.number_format(value, places=0)

        # ------------------------------------------------
        # Float
        elif format == '-1234.12':
            if not value:
                value = 0
            value = "%0.2f" % my.convert_to_float(value)

        elif format == '-1,234.12':
            # break the value up by 3s
            if not value:
                value = 0
            value = my.number_format(value, places=2)

        # ------------------------------------------------
        # Percentage
        elif format == '-13%':
            if not value:
                value = 0
            value = my.convert_to_float(value) * 100
            value = "%0.0f" % my.convert_to_float(value) + "%"

        elif format == '-12.95%':
            if not value:
                value = 0
            value = my.convert_to_float(value) * 100
            value = "%0.2f" % my.convert_to_float(value) + "%"

        # ------------------------------------------------
        # Currency
        elif format == '-$1,234':
            # break the value up by 3s
            if not value:
                value = 0
            value = my.currency_format(value, grouping=True)
            value = value[0:-3]

        elif format == '-$1,234.00':
            if not value:
                value = 0
            value = my.currency_format(value, grouping=True)

        elif format == '-$1,234.--':
            # break the value up by 3s
            if not value:
                value = 0
            value = my.currency_format(value, grouping=True)
            value = value[0:-3] + ".--"

        elif format == '-$1,234.00 CAD':
            # break the value up by 3s
            if not value:
                value = 0
            value = my.currency_format(value, grouping=True, monetary=True)

        elif format == '($1,234.00)':
            # break the value up by 3s
            if not value or value == "0":
                value = " "
            else:
                value = my.currency_format(value, grouping=True)
                if value.startswith("-"):
                    value = "<span style='color: #F00'>(%s)</span>" % value.replace("-", "")


        # ------------------------------------------------
        # Date
        elif format == '31/12/99':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%d/%m/%y")

        elif format == 'December 31, 1999':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%B %d, %Y")

        elif format == '31/12/1999':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%d/%m/%Y")

        elif format == 'Dec 31, 99':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%b %d, %y")

        elif format == 'Dec 31, 1999':
            if not value:
                value = ''
            else:
                try:
                    value = parser.parse(value)
                except:
                    # try utc
                    value = int(value)
                    value = datetime.datetime.fromtimestamp(value)

                value = value.strftime("%b %d, %Y")

        elif format == '31 Dec, 1999':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%d %b, %Y")

        elif format == '31 December 1999':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%d %B %Y")

        elif format == 'Fri, Dec 31, 99':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%a, %b %d, %y")

        elif format == 'Fri 31/Dec 99':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%a %d/%b %y")

        elif format == 'Fri, December 31, 1999':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%a, %B %d, %Y")

        elif format == 'Friday, December 31, 1999':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%A, %B %d, %Y")

        elif format == '12-31':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%m-%d")

        elif format == '99-12-31':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%y-%m-%d")

        elif format == '1999-12-31':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%Y-%m-%d")

        elif format == '12-31-1999':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%m-%d-%Y")

        elif format == '12/99':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%m-%y")

        elif format == '31/Dec':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%d/%b")

        elif format == 'December':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%B")

        elif format == '52':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%U")

        # ------------------------------------------------
        # Time
        elif format == '13:37':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%H:%M")

        elif format == '13:37:46':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%H:%M:%S")

        elif format == '01:37 PM':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%I:%M %p")

        elif format == '01:37:46 PM':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                """
                # TO BE REMOVED: outdated as it is processed in get_display()
                from pyasm.common import SPTDate

                # this is a special column based timezone override
                timezone = my.get_option('timezone')
                if not timezone:
                    pass
                elif timezone == "local":
                    pass # already the default
                    #value = SPTDate.convert_to_local(value)
                else:
                    value = SPTDate.convert_to_timezone(value, timezone)
                """
                value = value.strftime("%I:%M:%S %p")

        elif format == '31/12/99 13:37':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%d/%m/%y %H:%M")

        elif format == '31/12/99 13:37:46':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%d/%m/%y %H:%M:%S")

        elif format == 'DATETIME':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                setting = ProdSetting.get_value_by_key('DATETIME')
                if not setting:
                    setting = "%Y-%m-%d %H:%M"
                
                value = value.strftime(setting)
                
                

        elif format == 'DATE':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                setting = ProdSetting.get_value_by_key('DATE')
                if not setting:
                    setting = "%Y-%m-%d"
                value = value.strftime(setting)
        # ------------------------------------------------
        # Scientific
        elif format == '-1.23E+03':
            if not value:
                value = ''
            else:
                try:
                    value = "%.2e" % my.convert_to_float(value)
                except:
                    value = "0.00"

        elif format == '-1.234E+03':
            if not value:
                value = ''
            else:
                try:
                    value = "%.2e" % my.convert_to_float(value)
                except:
                    value = "0.00"

        # ------------------------------------------------
        # Boolean
        # false = 0, true = 1
        elif format in ['True|False']:
            if value:
                value = 'True'
            else: 
                value = 'False'

        elif format in ['true|false']:
            if value:
                value = 'true'
            else: 
                value = 'false'

        elif format == 'Checkbox':

            div = DivWdg()
            div.add_class("spt_boolean_top")
            from pyasm.widget import CheckboxWdg
            checkbox = CheckboxWdg(my.get_name())
            if my.attributes.get('edit') == 'false':
                checkbox.set_option('disabled','disabled')

            checkbox.set_option("value", "true")
            if value:
                checkbox.set_checked()
            div.add(checkbox)

            div.add_class('spt_format_checkbox_%s' % my.get_name())

            version = my.parent_wdg.get_layout_version()
            if version == "2":
                pass
            else:
                checkbox.add_behavior( {
                'type': 'click_up',
                'propagate_evt': True,
                'cbjs_action': '''

                var cached_data = {};
                var value_wdg = bvr.src_el;
                var top_el = bvr.src_el.getParent(".spt_boolean_top");
                spt.dg_table.edit.widget = top_el;
                var key_code = spt.kbd.special_keys_map.ENTER;
                spt.dg_table.inline_edit_cell_cbk( value_wdg, cached_data );
                '''
                } )

            value = div


        # ------------------------------------------------
        # Timecode
        elif format in ['MM:SS.FF','MM:SS:FF', 'MM:SS', 'HH:MM:SS.FF', 'HH:MM:SS:FF', 'HH:MM:SS']:
            fps = my.get_option('fps')
            if not fps:
                fps = 24
            else:
                fps = int(fps)
            timecode = TimeCode(frames=value, fps=fps)

            value = timecode.get_timecode(format)


        # ------------------------------------------------
        # Text formats
        elif format in ['wiki']:
            pass

       
        return value



    def handle_th(my, th, index):
        format = my.get_option('format')
        if format == 'Checkbox':
            th.add_attr("spt_input_type", "inline")
            #th.add_style("text-align: center")


    def handle_td(my, td):
        super(FormatElementWdg, my).handle_td(td)
        version = my.parent_wdg.get_layout_version()
        if version == "2":
            return
        format = my.get_option('format')
        if format == 'Checkbox':
            td.add_attr("spt_input_type", "inline")
            td.add_style("text-align: center")
        
 




