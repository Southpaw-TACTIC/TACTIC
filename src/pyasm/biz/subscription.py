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



