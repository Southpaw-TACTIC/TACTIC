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

    def __init__(self, **kwargs):

        self.validation_regex = ''
        self.validation_script = ''
        self.validation_script_path = ''
        self.validation_js = ''
        self.validation_scheme = ''
        self.validation_warning = ''
        self.direct_cbjs = ''

        widget = kwargs.get('widget')
        if widget and hasattr(widget, "get_option"):
            self.validation_regex = widget.get_option("validation_regex")
            self.validation_script = widget.get_option("validation_script")
            self.validation_script_path = widget.get_option("validation_script_path")
            self.validation_js = widget.get_option("validation_js")
            self.validation_scheme = widget.get_option('validation_scheme')
            self.validation_warning = widget.get_option("validation_warning")

        if kwargs.get('regex'):
            self.validation_regex = kwargs.get('regex')

        if kwargs.get('script'):
            self.validation_script = kwargs.get('script')
        elif kwargs.get('script_path'):
            self.validation_script_path = kwargs.get('script_path')

        if kwargs.get('js'):
            self.validation_js = kwargs.get('js')
        elif kwargs.get('scheme'):
            self.validation_scheme = kwargs.get('scheme')

        if kwargs.get('warning'):
            self.validation_warning = kwargs.get('warning')

        if kwargs.get('direct_cbjs'):
            self.direct_cbjs = kwargs.get('direct_cbjs')

       


    def get_validation_bvr(self):

        cbjs_validation = ''

        if self.direct_cbjs:
            cbjs_validation = self.direct_cbjs

        elif self.validation_script:

            # get the script code from the custom_script table of the project ...
            prj_code = Project.get_project_code()
            s_key = "config/custom_script?project=%s&code=%s" % (prj_code, self.validation_script)
            custom_script_sobj = Search.get_by_search_key( s_key )
            if not custom_script_sobj:
                raise TacticException( 'Did NOT find a code="%s" custom_script entry for validation behavior' %
                                        (self.validation_script) )
            cbjs_validation = custom_script_sobj.get_value('script')
        
        elif self.validation_script_path:
            folder = os.path.dirname(self.validation_script_path)
            title = os.path.basename(self.validation_script_path)
            expr = "@GET(config/custom_script['folder','%s']['title','%s'].script)" %(folder, title)
            cbjs_validation = Search.eval(expr, single=True)
            

        elif self.validation_regex:
            # NOTE: the return MUST be true or false ... a return of null means an error
            # on defining or running the validation function wrapper around this ...
            #
            cbjs_validation = '''return( value.match( /%s/ ) != null );''' % self.validation_regex

        elif self.validation_js:
            cbjs_validation = self.validation_js

        elif self.validation_scheme:
            js = self.SCHEME.get(self.validation_scheme)
            cbjs_validation = js
            
        if not cbjs_validation:
            return None

        if not self.validation_warning:
            self.validation_warning = 'Entry not valid'

        return {'type': 'validation', 'cbjs_validation': cbjs_validation,
                'validation_warning': self.validation_warning}


    def get_input_onchange_bvr(self):

        return { 'type': 'change', 'cbjs_action': 'spt.validation.onchange_cbk( evt, bvr );' }


