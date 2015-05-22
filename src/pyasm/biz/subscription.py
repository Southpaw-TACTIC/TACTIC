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

    SEARCH_TYPE = "sthpw/subscription"
    def get_subscriptions_by_stype(login, search_type):
        subs_expr = "@SOBJECT(sthpw/subscription['login','%s'])" %(login)

        sobjects = Search.eval(subs_expr)

        return sobjects
    get_subscriptions_by_stype = staticmethod(get_subscriptions_by_stype)



