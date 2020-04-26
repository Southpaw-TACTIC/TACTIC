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


__all__ = ['WorkHour']

from pyasm.search import *
from pyasm.biz import Project
from pyasm.common import Environment

class WorkHour(SObject):
    '''Work hour for task or various items'''
    SEARCH_TYPE = "sthpw/work_hour"

    def get_defaults(self):
        '''specifies the defaults for this sobject'''
        project_code = Project.get_project_code()
        me = Environment.get_user_name()
        defaults = {
            "project_code": project_code,
            "login": me
        }

        return defaults


 
