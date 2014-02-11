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

__all__ = ['SObjectLog', 'RetireLog']

from pyasm.common import *
from search import *


class SObjectLog(SObject):
    
    SEARCH_TYPE = 'sthpw/sobject_log'

    def create(sobject, transaction):
        assert sobject

        log = SObjectLog.create_new()
        log.set_sobject_value(sobject)
        log.set_user()
        log.set_value("transaction_log_id", transaction.get_id() )
        log.commit(triggers="none")

    create = staticmethod(create)





class RetireLog(SObject):

    SEARCH_TYPE = "sthpw/retire_log"


    def get_all_by_sobject(sobject):
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()

        search = Search("sthpw/retire_log")
        search.add_filter("search_type", search_type)
        search.add_filter("search_id", search_id)

        retire_logs = search.get_sobjects()
        return retire_logs
    get_all_by_sobject = staticmethod(get_all_by_sobject)



    def get_by_interval(interval):
        search = Search("sthpw/retire_log")
        search.add_where("now()-timestamp <= '%s'::interval" % interval)
        search.add_order_by("timestamp desc")
        user = Environment.get_user_name()
        search.add_filter("login", user)
        retire_logs = search.get_sobjects()
        return retire_logs
    get_by_interval = staticmethod(get_by_interval)



    def create(search_type, search_id):

        log = RetireLog( RetireLog.SEARCH_TYPE )
        log.set_value("search_type", search_type)
        log.set_value("search_id", search_id)

        user = Environment.get_user_name()
        log.set_value("login", user)

        log.commit()
        return log
    create = staticmethod(create)














