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

__all__ = ["Notification", "GroupNotification"]


from pyasm.search import Search, SObject, SearchType
from pyasm.security import LoginGroup, Login, LoginInGroup

class Notification(SObject):

    SEARCH_TYPE = "sthpw/notification"


    def get_foreign_key(my):
        return "notification_id"


    def get_defaults(my):
        '''specifies the defaults for this sobject'''
        defaults = {
            "type": "email"
        }
        return defaults
    """
    def get_description(my):
        desc = [my.get_code()]
        if my.get_value('search_type'):
            desc.append('for %s' % my.get_value('search_type'))
        if my.get_value('context'):
            desc.append('in %s' % my.get_value('context'))    
        
        return " ".join(desc)
    """

    def get_description(my):
        return my.get_value("description")
       

    """
    def get(code, search_type, context):
        search = Search(Notification.SEARCH_TYPE)
        search.add_filter("code", code)
        if search_type:
            search.add_filter("search_type", search_type)
        if context:
            search.add_filter("context", context)
        return search.get_sobjects()
    get = staticmethod(get)
    """


class GroupNotification(SObject):

    SEARCH_TYPE = "sthpw/group_notification"
    def get_groups_by_code(note_code):
        group_note = SearchType.get(GroupNotification.SEARCH_TYPE)
        
        search = Search(LoginGroup.SEARCH_TYPE)
        search.add_where('''"login_group" in (select "login_group" from "%s" where "notification_code" = '%s')''' %(group_note.get_table(), note_code))
            
        return search.get_sobjects()
    get_groups_by_code = staticmethod(get_groups_by_code)
   
    def get_logins_by_id(note_id):
        login_in_group = SearchType.get(LoginInGroup.SEARCH_TYPE)
        group_note = SearchType.get(GroupNotification.SEARCH_TYPE)
        search = Search(Login.SEARCH_TYPE)
        query_str = ''
        
        if isinstance(note_id, list):
            query_str = "in (%s)" %",".join([str(id) for id in note_id])
        else:
            query_str = "= %d" %note_id
        search.add_where('''"login" in (select "login" from "%s" where "login_group" in (select "login_group" from "%s" where "notification_id" %s)) ''' % (login_in_group.get_table(), group_note.get_table(), query_str))
            
            
        return search.get_sobjects()
    get_logins_by_id = staticmethod(get_logins_by_id)




