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

__all__ = ['PythonElementWdg']

import types, os

from pyasm.common import TacticException, Container, jsonloads, jsondumps

from pyasm.search import Search
from tactic.command import PythonCmd

from table_element_wdg import TypeTableElementWdg

class PythonElementWdg(TypeTableElementWdg):
    '''General purpose element widget for expressions'''

    ARGS_KEYS = {
    'script_path': {
        'description': 'Path of script',
        'type': 'TextWdg',
        'order': 1,
        'category': 'Options'
    },
  
    'display_format': {
        'description': 'Predefined format for display',
        'type': 'TextWdg',
        'order': 3,
        'category': 'Options'
    },
    'bottom':   {
        'description': 'Expression to calculate the bottom row of the table',
        'type': 'TextAreaWdg',
    },
    'group_bottom':   {
        'description': 'Expression to calculate the bottom of a group',
        'type': 'TextAreaWdg',
    },
    'order_by': {
        'description': 'Turn on Order by',
        'type': 'TextWdg',
        'order': 5,
        'category': 'Options'
    }
    }
  

 
    def get_required_columns(my):
        '''method to get the require columns for this'''
        return []


    def get_sort_prefix(my):
        return "Post"

    def is_sortable(my):
        # false is the word to prevent the auto-adoption (preprocess) of the expression to order-by
        order_by = my.get_option("order_by")
        if order_by =='false':
            return False
        else:
            return True

    def is_groupable(my):
        group_by = my.get_option("group_by")
        if group_by:
            return True
        else:
            return False


    def is_time_groupable(my):
        return False



    def preprocess(my):

        script_path = my.get_option("script_path")

        folder = os.path.dirname(script_path)
        title = os.path.basename(script_path)

        search = Search("config/custom_script")
        search.add_filter("folder", folder)
        search.add_filter("title", title)
        custom_script = search.get_sobject()
        if not custom_script:
           my.code = '''return "No script defined"''' 
        else:
           my.code = custom_script.get_value("script")


    def get_result(my, sobject):
        result = None
        sobject_dict = sobject.get_sobject_dict()
        filter_data = my.filter_data.get_data()
        try:
            cmd = PythonCmd(code=my.code, sobject=sobject_dict, filter_data=filter_data)
            result = cmd.execute()
        except Exception, e:
            return str(e)
        
        return result

    def get_display(my):
        top = my.top
        my.result = ''

        sobject = my.get_current_sobject()
        
        current_value = sobject.get_value(my.get_name(), no_exception=True)
        if current_value:
            top.add(current_value)
            return top

        result = my.get_result(sobject)

        if result == "":
            return top

        sobject.set_value(my.get_name(), result, temp=True)
        display_format = my.get_option("display_format")
        if display_format:
            expr = "@FORMAT(@GET(.%s), '%s')" % (my.get_name(), display_format)
            result = Search.eval(expr, sobject, single=True)

        my.result = result
        
        top.add(result)
        return top

    def get_text_value(my):

        sobject = my.get_current_sobject()
        sobject_dict = sobject.get_sobject_dict()

        try:
            cmd = PythonCmd(code=my.code, sobject=sobject_dict)
            result = cmd.execute()
        except Exception, e:
            return str(e)

        if result == "":
            return result

        sobject.set_value(my.get_name(), result, temp=True)
        display_format = my.get_option("display_format")
        if display_format:
            expr = "@FORMAT(@GET(.%s), '%s')" % (my.get_name(), display_format)
            result = Search.eval(expr, sobject, single=True)
        return result


    def handle_td(my, td):
        if isinstance(my.result, basestring):
            td.add_style("text-align", "left")
        else:
            td.add_style("text-align", "right")


