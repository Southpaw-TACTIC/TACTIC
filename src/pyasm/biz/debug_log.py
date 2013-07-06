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

__all__ = ['DebugLog']

from pyasm.common import Environment
from pyasm.search import SObject, SObjectFactory, Transaction

import sys,traceback

class DebugLog(SObject):
    '''Class that controls the logging of all debug logs during the Tactic
    runtime'''

    SEARCH_TYPE = "sthpw/debug_log"

    critical = 50
    error = 40
    warning = 30
    info = 20
    debug = 10


    def debug(cls, message, category="default"):
        return cls.log("debug", message, category)
    debug = classmethod(debug)



    def log(cls, level, message, category="default"):
        assert level in ("critical", "error", "warning", "info", "debug")

        # record the exception
        user_name = Environment.get_user_name()
        if not user_name:
            user_name = "UNKNOWN"

        # put the debug in a completely separate transaction from the main
        # transaction
        transaction = Transaction.get(force=True)
        transaction.set_record(False)

        debug_log = SObjectFactory.create("sthpw/debug_log")
        debug_log.set_value("login", user_name)
        debug_log.set_value("level", level)
        debug_log.set_value("category", category)
        debug_log.set_value("message", message )
        debug_log.commit()

        transaction.commit()
        transaction.remove_from_stack()

        return debug_log

    log = classmethod(log)





