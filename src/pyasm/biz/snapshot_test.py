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


    def test_all(self):

        self.description = "Checkin unit test"
        self.errors = []

        Batch()
        Project.set_project("unittest")

        
        self.transaction = Transaction.get(create=True)
        try:
            self._test_create()
        finally:
            self.transaction.rollback()
 


    def _test_create(self):
        search = Search("unittest/person")
        persons = search.get_sobjects()
        person = persons[0]

        snapshot_type = "file"
        snapshot = Snapshot.create(person, context="publish", snapshot_type=snapshot_type)

        version = snapshot.get_value("version")
        self.assertEquals( 1, version )

        search_type = snapshot.get_value("search_type")
        self.assertEquals( search_type, person.get_search_type() )
        search_code = snapshot.get_value("search_code")
        self.assertEquals( search_code, person.get_value("code") )

        # also check search_id
        if SearchType.column_exists("sthpw/snapshot", "search_id"):
            search_code = snapshot.get_value("search_id")
            self.assertEquals( search_code, person.get_value("id") )


        test_person = snapshot.get_sobject()
        self.assertEquals(test_person.get_code(), person.get_code())

if __name__ == '__main__':
    unittest.main()



