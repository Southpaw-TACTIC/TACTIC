###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ["RetireCmd", "ReactivateCmd", "DeleteCmd"]

from pyasm.search import *
from pyasm.common import *
from command import *


class RetireCmd(Command):

    def __init__(self, **kwargs):
        super(RetireCmd, self).__init__(**kwargs)
        self.search_type = self.kwargs.get('search_type')
        self.search_id =  self.kwargs.get('search_id')

    def set_search_type(self, search_type):
        self.search_type = search_type

    def set_search_id(self, search_id):
        self.search_id = search_id

    def get_title(self):
        return "Retire"

    def execute(self):
        
        sobject = Search.get_by_id(self.search_type, self.search_id)
        sobject.retire()

        search_type_desc = SearchType.get(self.search_type).get_title()
        self.add_description("Retired [%s] of type [%s] " % (sobject.get_code(), \
                
            search_type_desc))

    def check(self):
        
        if not self.search_type or not self.search_id:
            # try the web
            from pyasm.web import WebContainer
            web = WebContainer.get_web()
            self.search_type = web.get_form_value('search_type')
            self.search_id = web.get_form_value('search_id')
            if not self.search_type or not self.search_id:
                raise CommandException("search type or search id is empty")
        return True

    def check_security(self):
        '''give the command a callback that allows it to check security'''
        return True


class ReactivateCmd(RetireCmd):
    '''Reactivate an sobject '''
    def get_title(self):
        return "Reactivate"

    def execute(self):
        
        sobject = Search.get_by_id(self.search_type, self.search_id)
        sobject.reactivate()
        self.add_description("Reactivated '%s' '%s'" % (self.search_type, self.search_id))





class DeleteCmd(Command):
    '''Base class for all command'''

    def __init__(self):
        super(DeleteCmd,self).__init__()
        self.search_type = ""
        self.search_id = ""
        
    def set_search_type(self, search_type):
        self.search_type = search_type

    def set_search_id(self, search_id):
        self.search_id = search_id

    def check(self):
        return True
    
    def execute(self):
        if not self.search_type or not self.search_id:
            # try the web
            from pyasm.web import WebContainer
            web = WebContainer.get_web()
            self.search_type = web.get_form_value('search_type')
            self.search_id = web.get_form_value('search_id')
            if not self.search_type or not self.search_id:
                raise CommandException("search type or search id is empty")
        sobject = Search.get_by_id(self.search_type, self.search_id)
        sobject.delete()

        search_type_desc = SearchType.get(self.search_type).get_title()
        self.add_description("Deleted [%s] of type [%s] " % (sobject.get_code(), \
            search_type_desc))

    def get_title(self):
        return "Delete"

    def check_security(self):
        '''give the command a callback that allows it to check security'''
        return True



