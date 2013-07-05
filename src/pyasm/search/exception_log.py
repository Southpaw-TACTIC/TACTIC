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

__all__ = ['ExceptionLog']

from pyasm.common import *
from search import *
from sql import DbContainer

import sys,traceback

class ExceptionLog(SObject):
    '''Class that controls the logging of all of the exceptions that occur
    during the Tactic runtime'''

    def log(exception):
        tb = sys.exc_info()[2]
        stacktrace = traceback.format_tb(tb)
        stacktrace_str = "".join(stacktrace)

        # replace crazy windows paths with normal paths
        stacktrace_str = stacktrace_str.replace("\\", "/")


        print "-"*50
        print stacktrace_str
        print str(exception)
        print "-"*50

        # make sure all of the databases are rolled back
        DbContainer.rollback_all()

        # record the exception
        user_name = Environment.get_user_name()
        if not user_name:
            user_name = "UNKNOWN"


        exception_log = SObjectFactory.create("sthpw/exception_log")
        exception_log.set_value("login", user_name)
        exception_log.set_value("class", exception.__class__.__name__)
        exception_log.set_value("message", str(exception) )

        exception_log.set_value("stack_trace", stacktrace_str)

        exception_log.commit()

        del tb, stacktrace

        return exception_log

    log = staticmethod(log)



    def get_stack_trace(exception):
        tb = sys.exc_info()[2]
        stacktrace = traceback.format_tb(tb)
        stacktrace_str = "".join(stacktrace)

        # replace crazy windows paths with normal paths
        stacktrace_str = stacktrace_str.replace("\\", "/")
        return stacktrace_str
    get_stack_trace = staticmethod(get_stack_trace)



