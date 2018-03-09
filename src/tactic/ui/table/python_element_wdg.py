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
    },

    'group_by': {
        'description': 'Turn on Group by',
        'type': 'SelectWdg',
        'values': 'true|',
        'labels': 'true|false',
        'order': 6,
        'category': 'Options'
    }
    }
  

 
    def get_required_columns(self):
        '''method to get the require columns for this'''
        return []


    def get_sort_prefix(self):
        return "Post"

    def is_sortable(self):
        # false is the word to prevent the auto-adoption (preprocess) of the expression to order-by
        order_by = self.get_option("order_by")
        if order_by =='false':
            return False
        else:
            return True

    def is_groupable(self):
        group_by = self.get_option("group_by")
        if group_by:
            return True
        else:
            return False


    def is_time_groupable(self):
        return False



    def preprocess(self):

        script_path = self.get_option("script_path")

        folder = os.path.dirname(script_path)
        title = os.path.basename(script_path)

        search = Search("config/custom_script")
        search.add_filter("folder", folder)
        search.add_filter("title", title)
        custom_script = search.get_sobject()
        if not custom_script:
           self.code = '''return "No script defined"''' 
        else:
           self.code = custom_script.get_value("script")


    def get_result(self, sobject):
        result = None
        sobject_dict = sobject.get_sobject_dict()
        filter_data = self.filter_data.get_data()
        try:
            cmd = PythonCmd(code=self.code, sobject=sobject_dict, filter_data=filter_data)
            result = cmd.execute()
        except Exception as e:
            return str(e)
        
        return result

    def get_display(self):
        top = self.top
        self.result = ''

        sobject = self.get_current_sobject()
        
        current_value = sobject.get_value(self.get_name(), no_exception=True)
        if current_value:
            top.add(current_value)
            return top

        result = self.get_result(sobject)

        if result == "":
            return top

        sobject.set_value(self.get_name(), result, temp=True)
        display_format = self.get_option("display_format")
        if display_format:
            expr = "@FORMAT(@GET(.%s), '%s')" % (self.get_name(), display_format)
            result = Search.eval(expr, sobject, single=True)

        self.result = result
        
        top.add(result)
        return top

    def get_text_value(self):

        sobject = self.get_current_sobject()
        sobject_dict = sobject.get_sobject_dict()

        try:
            cmd = PythonCmd(code=self.code, sobject=sobject_dict)
            result = cmd.execute()
        except Exception as e:
            return str(e)

        if result == "":
            return result

        sobject.set_value(self.get_name(), result, temp=True)
        display_format = self.get_option("display_format")
        if display_format:
            expr = "@FORMAT(@GET(.%s), '%s')" % (self.get_name(), display_format)
            result = Search.eval(expr, sobject, single=True)
        return result


    def handle_td(self, td):
        if isinstance(self.result, basestring):
            td.add_style("text-align", "left")
        else:
            td.add_style("text-align", "right")


