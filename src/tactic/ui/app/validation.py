###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["ValidationUtil"]

import os
from pyasm.biz import Project
from pyasm.common import TacticException
from pyasm.search import Search



class ValidationUtil:
    SCHEME = {'INTEGER': 'return value ? spt.input.is_integer(value): true',
          'POS_INTEGER': 'return value ? spt.input.is_integer(value) && parseInt(value, 10) > 0 : true',
          'NUMERIC': 'return value ? spt.input.is_numeric(value): true' }

    def __init__(my, **kwargs):

        my.validation_regex = ''
        my.validation_script = ''
        my.validation_script_path = ''
        my.validation_js = ''
        my.validation_scheme = ''
        my.validation_warning = ''
        my.direct_cbjs = ''

        widget = kwargs.get('widget')
        if widget and hasattr(widget, "get_option"):
            my.validation_regex = widget.get_option("validation_regex")
            my.validation_script = widget.get_option("validation_script")
            my.validation_script_path = widget.get_option("validation_script_path")
            my.validation_js = widget.get_option("validation_js")
            my.validation_scheme = widget.get_option('validation_scheme')
            my.validation_warning = widget.get_option("validation_warning")

        if kwargs.get('regex'):
            my.validation_regex = kwargs.get('regex')

        if kwargs.get('script'):
            my.validation_script = kwargs.get('script')
        elif kwargs.get('script_path'):
            my.validation_script_path = kwargs.get('script_path')

        if kwargs.get('js'):
            my.validation_js = kwargs.get('js')
        elif kwargs.get('scheme'):
            my.validation_scheme = kwargs.get('scheme')

        if kwargs.get('warning'):
            my.validation_warning = kwargs.get('warning')

        if kwargs.get('direct_cbjs'):
            my.direct_cbjs = kwargs.get('direct_cbjs')

       


    def get_validation_bvr(my):

        cbjs_validation = ''

        if my.direct_cbjs:
            cbjs_validation = my.direct_cbjs

        elif my.validation_script:

            # get the script code from the custom_script table of the project ...
            prj_code = Project.get_project_code()
            s_key = "config/custom_script?project=%s&code=%s" % (prj_code, my.validation_script)
            custom_script_sobj = Search.get_by_search_key( s_key )
            if not custom_script_sobj:
                raise TacticException( 'Did NOT find a code="%s" custom_script entry for validation behavior' %
                                        (my.validation_script) )
            cbjs_validation = custom_script_sobj.get_value('script')
        
        elif my.validation_script_path:
            folder = os.path.dirname(my.validation_script_path)
            title = os.path.basename(my.validation_script_path)
            expr = "@GET(config/custom_script['folder','%s']['title','%s'].script)" %(folder, title)
            cbjs_validation = Search.eval(expr, single=True)
            

        elif my.validation_regex:
            # NOTE: the return MUST be true or false ... a return of null means an error
            # on defining or running the validation function wrapper around this ...
            #
            cbjs_validation = '''return( value.match( /%s/ ) != null );''' % my.validation_regex

        elif my.validation_js:
            cbjs_validation = my.validation_js

        elif my.validation_scheme:
            js = my.SCHEME.get(my.validation_scheme)
            cbjs_validation = js
            
        if not cbjs_validation:
            return None

        if not my.validation_warning:
            my.validation_warning = 'Entry not valid'

        return {'type': 'validation', 'cbjs_validation': cbjs_validation,
                'validation_warning': my.validation_warning}


    def get_input_onchange_bvr(my):

        return { 'type': 'change', 'cbjs_action': 'spt.validation.onchange_cbk( evt, bvr );' }


