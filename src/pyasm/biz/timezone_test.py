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

__all__ = ["TimeZoneTest"]

import tacticenv
import os
import unittest

from pyasm.common import SPTDate
from pyasm.security import Batch
from pyasm.search import Search, SearchType
from pyasm.biz import Project


class TimeZoneTest(unittest.TestCase):

    def setUp(my):
        # start batch environment
        Batch()


    def test_all(my):

        my._test_task()



    def _test_task(my):

        project = Project.get()

        # create a new task
        task = SearchType.create("sthpw/task")
        task.set_parent(project)
        task.set_value("code", "XXX001")
        task.set_value("process", "unittest")
        task.set_value("description", "unittest")

        # set a time with no timezone.  A timestamp with no timezone should
        # assume GMT.
        test_time = '2011-11-11 00:00:00'
        task.set_value("timestamp", test_time)

        # asset that the time has not changed
        timestamp = task.get_value("timestamp")
        my.assertEquals(timestamp, test_time)
        task.commit()


        # get the task back from the databse
        search = Search("sthpw/task")
        search.add_filter("code", "XXX001")
        task = search.get_sobject()

        # make sure the time has not changed.  This value should is assumed
        # to be in GMT
        timestamp = task.get_value("timestamp")
        my.assertEquals(timestamp, test_time)

        task.delete()




if __name__ == '__main__':
    unittest.main()



