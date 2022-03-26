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

__all__ = ["Subscription"]

from pyasm.common import Environment
from pyasm.search import Search, SObject, SearchType

class Subscription(SObject):
    '''
    This class is associated with the sthpw/subscription table.
    It contains methods that are relevant to operations that affect
    or read from this table.
    '''

    SEARCH_TYPE = "sthpw/subscription"
    def get_by_search_type(login, search_type):
        subs_expr = "@SOBJECT(sthpw/subscription['login','%s'])" %(login)

        sobjects = Search.eval(subs_expr)

        return sobjects
    get_by_search_type = staticmethod(get_by_search_type)



    def get_by_message_code(message_code):
        expr = "@SOBJECT(sthpw/subscription['login','%s']['message_code','%s'])" %(login, message_code)
        sobject = Search.eval(expr, single=True)
        return sobject
    get_by_message_code = staticmethod(get_by_message_code)



    def create(cls, message_code):

        login = Environment.get_user_name()

        # check to see if this subscription already exists
        search = Search("sthpw/subscription")
        search.add_filter("login", login)
        search.add_filter("message_code", message_code)
        subscription = search.get_sobject()
        if not subscription:
            subscription = SearchType.create("sthpw/subscription")
            subscription.set_value("login", login)
            subscription.set_value("message_code", message_code)
            subscription.commit()

        return subscription

    create = classmethod(create)



    def unsubscribe(cls, message_code):
 
        login = Environment.get_user_name()

        search = Search("sthpw/subscription")
        search.add_filter("login", login)
        search.add_filter.set_value("message_code", message_code)
        subscription = search.get_sobject()

        subscription.delete()

    unsubscribe = classmethod(unsubscribe)
  




