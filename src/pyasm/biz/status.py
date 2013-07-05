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

__all__ = ["StatusLog"]

from pyasm.search import SObjectFactory, SObject, Search

from pipeline import Pipeline
from pyasm.common import Environment, Date
from project import Project

class StatusLog(SObject):

    SEARCH_TYPE = "sthpw/status_log"

    def create(sobject, value, prev_value=None):
        if prev_value == value:
            return

        # if this is successful, the store it in the status_log
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()

        status_log = SObjectFactory.create("sthpw/status_log")
        status_log.set_value("login", Environment.get_user_name() )
        status_log.set_value("search_type", search_type)
        status_log.set_value("search_id", search_id)
        if prev_value:
            status_log.set_value("from_status", prev_value)

        status_log.set_value("to_status", value)

        project_code = Project.get_project_name()
        status_log.set_value("project_code", project_code)

        status_log.commit()

        return status_log

    create = staticmethod(create)


