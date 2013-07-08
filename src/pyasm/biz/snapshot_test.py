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

__all__ = ["SnapshotTest"]

import tacticenv
import os
import unittest

from pyasm.common import *
from pyasm.security import *
from pyasm.search import SearchType, Search, SearchKey, Transaction
from project import Project
from snapshot import Snapshot


class SnapshotTest(unittest.TestCase):


    def test_all(my):

        my.description = "Checkin unit test"
        my.errors = []

        Batch()
        Project.set_project("unittest")

        
        my.transaction = Transaction.get(create=True)
        try:
            my._test_create()
        finally:
            my.transaction.rollback()
 


    def _test_create(my):
        search = Search("unittest/person")
        persons = search.get_sobjects()
        person = persons[0]

        snapshot_type = "file"
        snapshot = Snapshot.create(person, context="publish", snapshot_type=snapshot_type)

        version = snapshot.get_value("version")
        my.assertEquals( 1, version )

        search_type = snapshot.get_value("search_type")
        my.assertEquals( search_type, person.get_search_type() )
        search_code = snapshot.get_value("search_code")
        my.assertEquals( search_code, person.get_value("code") )

        # also check search_id
        if SearchType.column_exists("sthpw/snapshot", "search_id"):
            search_code = snapshot.get_value("search_id")
            my.assertEquals( search_code, person.get_value("id") )


        test_person = snapshot.get_sobject()
        my.assertEquals(test_person.get_code(), person.get_code())

if __name__ == '__main__':
    unittest.main()



