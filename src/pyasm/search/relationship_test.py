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

import tacticenv

from pyasm.security import *

from sql import *
from search import *
from transaction import *

import unittest

class RelationshipTest(unittest.TestCase):


    def setUp(my):
        # start batch environment
        Batch()

        from pyasm.biz import Project
        Project.set_project("unittest")



    def test_all(my):
        my.transaction = Transaction.get(create=True)
        try:
            my._test_parent_child()
            my._test_related()
        finally:
            my.transaction.rollback()



    def _test_parent_child(my):
        search = Search("unittest/person")
        persons = search.get_sobjects()
        person = persons[0]


        # create a task manually
        task = SearchType.create("sthpw/task")
        task.set_sobject_value(person)
        task.commit()

        # test get parent
        parent = task.get_parent()
        my.assertEquals( parent.get_code(), person.get_code() )


        # create another task
        task = SearchType.create("sthpw/task")
        task.set_sobject_value(person)
        task.commit()


        # get the children
        children = person.get_all_children("sthpw/task")
        my.assertEquals( 2, len(children) )


        # set the parent
        task = SearchType.create("sthpw/task")
        task.set_parent(person)
        task.commit()

        # get the children
        children = person.get_all_children("sthpw/task")
        my.assertEquals( 3, len(children) )


        # parent search key
        parent_key = task.get_parent_search_key()
        my.assertEquals(person.get_search_key(), parent_key)



    def _test_related(my):
        search = Search("unittest/person")
        persons = search.get_sobjects()
        person = persons[1]

        # create another task
        for i in range(0, 4):
            task = SearchType.create("sthpw/task")
            task.set_sobject_value(person)
            task.commit()

        # create another note
        for i in range(0, 3):
            task = SearchType.create("sthpw/note")
            task.set_sobject_value(person)
            task.commit()

        tasks = person.get_related_sobjects("sthpw/task")
        my.assertEquals( 4, len(tasks) )
        notes = person.get_related_sobjects("sthpw/note")
        my.assertEquals( 3, len(notes) )
    
    







if __name__ == "__main__":
    unittest.main()

