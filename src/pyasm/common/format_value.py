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


__all__ = ['FormatValue']

import re
import os
from dateutil import parser
import datetime
from timecode import TimeCode


import locale
locale.setlocale(locale.LC_ALL, '') 
try:
    locale.currency(1234.56, True)
except ValueError:
    # if auto setting of locale fails, then set the locale to en_US
    # Windows only understands alias language name like English
    if os.name == 'posix':
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') 
    elif os.name == 'nt':
        locale.setlocale(locale.LC_ALL, 'English') 



class FormatValue(object):

    def convert_to_float(my, num):
        try:
            num = float(num)
        except:
            num = 0
        return num


    def number_format(my, num, places=0):
        """Format a number according to locality and given places"""
        return locale.format("%.*f", (places, num), True)

    def currency_format(my, num, grouping=False, monetary=False):
        """Format a currency according to locality and given places"""
        try:
            num = float(num)
        except ValueError, e:
            num = 0
        return locale.currency(num, True, grouping, monetary)



    def get_format_value(my, value, format, format_option=None):
        '''format is required. format_option is optional where applicable like fps for timecode'''
        if value == '':
            return value

        if isinstance(value, datetime.datetime):
            value = str(value)
        elif not isinstance(value, basestring):
            value = str(value)

        if value.startswith("{") and value.endswith("}"):
            from pyasm.search import Search
            value = Search.eval(value)

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
            if not value:
                value = "-"
            else:
                value = my.currency_format(value, grouping=True)
                if value.startswith("-"):
                    value = "(%s)" % value.replace("-", "")

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
                value = parser.parse(value)
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
                value = value.strftime("%I:%M:%S %p")

        elif format == '31/12/99 13:37':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%d/%m/%y %H:%M")


        elif format == '99/12/31 13:37':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%y/%m/%d %H:%M")

        elif format == '1999/12/31 13:37':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%Y/%m/%d %H:%M")



        elif format == 'YYYY/MM/DD HH:MM AM':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                value = value.strftime("%Y/%m/%d %I:%M %p")

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
                from pyasm.biz import ProdSetting
                setting = ProdSetting.get_value_by_key('DATETIME')
                if not setting:
                    setting = "%Y-%m-%d %H:%M"
                value = value.strftime(setting)

        elif format == 'DATE':
            if not value:
                value = ''
            else:
                value = parser.parse(value)
                from pyasm.biz import ProdSetting
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


        # ------------------------------------------------
        # Timecode
        elif format in ['MM:SS.FF','MM:SS:FF', 'MM:SS', 'HH:MM:SS.FF', 'HH:MM:SS:FF','HH:MM:SS']:
            #fps = my.get_option('fps')
            fps = format_option
            if not fps:
                fps = 24
            else:
                fps = int(fps)
            timecode = TimeCode(frames=value, fps=fps)

            value = timecode.get_timecode(format)

        # ------------------------------------------------
        # Dictionary
        elif format == "DICT":

            dict_as_str = ""
            dict_list = []

            if not value:
                value = ''

            else:
                for key, value in sorted(value.iteritems()):
                    dict_list.append("%s : %s" % (key, value))

            dict_as_str = "<br />".join(dict_list)
            value = dict_as_str

        # ------------------------------------------------
        # File Size
        elif format in ['KB']:

            ext = " B"
            if not value:
                value = 0
                ext = "B"
            elif value > 1024**5/2:
                value = float(value)/1024**5
                ext = "PB"
            elif value > 1024**4/2:
                value = float(value)/1024**4
                ext = "TB"
            elif value > 1024**3/2:
                value = float(value)/1024**3
                ext = "GB"
            elif value > 1024**2/2:
                value = float(value)/1024**2
                ext = "MB"
            elif value > 1024/2:
                value = float(value)/1024
                ext = "KB"
            else:
                value = int(value)
                return "%s &nbsp;&nbsp;B" % value

            value = my.currency_format(value, grouping=True)
            # HACK: remove $ and last decimal
            value = value[1:-1]
            value = "%s %s" % (value, ext)
       
        return value


    """
    def handle_td(my, td):
        format = my.get_option('format')
        if format == 'Checkbox':
            td.add_attr("spt_input_type", "inline")
            td.add_style("text-align: center")
    """ 
