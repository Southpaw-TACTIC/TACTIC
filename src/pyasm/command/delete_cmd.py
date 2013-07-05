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

    def __init__(my, **kwargs):
        super(RetireCmd, my).__init__(**kwargs)
        my.search_type = my.kwargs.get('search_type')
        my.search_id =  my.kwargs.get('search_id')

    def set_search_type(my, search_type):
        my.search_type = search_type

    def set_search_id(my, search_id):
        my.search_id = search_id

    def get_title(my):
        return "Retire"

    def execute(my):
        
        sobject = Search.get_by_id(my.search_type, my.search_id)
        sobject.retire()

        search_type_desc = SearchType.get(my.search_type).get_title()
        my.add_description("Retired [%s] of type [%s] " % (sobject.get_code(), \
                
            search_type_desc))

    def check(my):
        
        if not my.search_type or not my.search_id:
            # try the web
            from pyasm.web import WebContainer
            web = WebContainer.get_web()
            my.search_type = web.get_form_value('search_type')
            my.search_id = web.get_form_value('search_id')
            if not my.search_type or not my.search_id:
                raise CommandException("search type or search id is empty")
        return True

    def check_security(my):
        '''give the command a callback that allows it to check security'''
        return True


class ReactivateCmd(RetireCmd):
    '''Reactivate an sobject '''
    def get_title(my):
        return "Reactivate"

    def execute(my):
        
        sobject = Search.get_by_id(my.search_type, my.search_id)
        sobject.reactivate()
        my.add_description("Reactivated '%s' '%s'" % (my.search_type, my.search_id))





class DeleteCmd(Command):
    '''Base class for all command'''

    def __init__(my):
        super(DeleteCmd,my).__init__()
        my.search_type = ""
        my.search_id = ""
        
    def set_search_type(my, search_type):
        my.search_type = search_type

    def set_search_id(my, search_id):
        my.search_id = search_id

    def check(my):
        return True
    
    def execute(my):
        if not my.search_type or not my.search_id:
            # try the web
            from pyasm.web import WebContainer
            web = WebContainer.get_web()
            my.search_type = web.get_form_value('search_type')
            my.search_id = web.get_form_value('search_id')
            if not my.search_type or not my.search_id:
                raise CommandException("search type or search id is empty")
        sobject = Search.get_by_id(my.search_type, my.search_id)
        sobject.delete()

        search_type_desc = SearchType.get(my.search_type).get_title()
        my.add_description("Deleted [%s] of type [%s] " % (sobject.get_code(), \
            search_type_desc))

    def get_title(my):
        return "Delete"

    def check_security(my):
        '''give the command a callback that allows it to check security'''
        return True



