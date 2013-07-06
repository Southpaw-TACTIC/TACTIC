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


from pyasm.command import DatabaseAction
from pyasm.search import SObjectFactory

__all__ = ['TaskCreateAction']

class TaskCreateAction(DatabaseAction):

    def execute(my):
        pass

    def postprocess(my):

        sobject = my.sobject

        if not sobject.is_insert():
            return


        processes = ["layout", "animation", "lighting"]

        # create a bunch of tasks
        for process in processes:
            task = SObjectFactory.create("sthpw/task")
            task.set_value("description", process)
            task.set_value("process", process)
            task.set_sobject_value(sobject)
            task.commit()



