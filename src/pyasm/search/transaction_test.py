#!/usr/bin/python 
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

__all__ = ['TransactionTest']

import tacticenv

from pyasm.common import *
from pyasm.security import *
from pyasm.unittest import *

from transaction import *
from transaction_log import *
from search import *
from sql import *
from pyasm.biz import Project

import unittest,os


class TransactionTest(unittest.TestCase):


    def test_all(my):

        # intialiaze the framework as a batch process
        batch = Batch()
        from pyasm.biz import Project
        Project.set_project("unittest")

        test_env = UnittestEnvironment()
        test_env.create()

        try:
            my._test_transaction()
            my._test_undo()
            my._test_file_undo()
            my._test_debug_log()
        finally:
            test_env.delete()


    def _test_transaction(my):
        # initiate a global transaction

        database = "unittest"
        count_sql = 'select count(*) from "person"'

        transaction = Transaction.get(create=True)

        # adding these 2 lines 
        project = Project.get_by_code(database)
        db_resource= project.get_project_db_resource()

        db = DbContainer.get(db_resource)

        count0 = db.get_value(count_sql)
        person = Person.create("Mr", "Dumpling", "Dumpling Land", "Burnt")

        # check to see that one was added
        count1 = db.get_value(count_sql)
        my.assertEquals( count1, count0+1)

        # FIXME: cant' delete for some reason
        #person.delete()

        # commit the first time
        transaction.commit()

        # check to see that one was added
        count1 = db.get_value(count_sql)
        my.assertEquals( count1, count0+1)

        #transaction.rollback()
        #person.delete()
        last = TransactionLog.get_last()
        last.undo()

        # create another login
        transaction = Transaction.get(create=True)

        count0 = db.get_value(count_sql)
        person = Person.create("Mr", "Dumpling", "Dumpling Land", "Burnt")
        db = DbContainer.get(db_resource)
        count2 = db.get_value(count_sql)
        my.assertEquals( count2, count0+1)

        transaction.rollback()

        # check to see that one was removed/rolled back
        count3 = db.get_value(count_sql)
        my.assertEquals( count3, count0)


    def _test_undo(my):

        search = Search("sthpw/transaction_log")
        search.add_filter("login", Environment.get_user_name() )
        num_transactions = search.get_count()

        # delete all instances of PotatoHead
        search = Search("unittest/person")
        search.add_filter("name_last", "Potato Head")
        people = search.do_search()
        for person in people:
            person.delete()

        # initiate a global transaction
        transaction = Transaction.get(create=True)

        person = Person.create("Mr", "Potato Head", "PotatoLand", "Pretty much looks like a potato")
        person2 = Person.create("Mrs", "Potato Head", "PotatoLand", "Pretty much looks like a potato")

        person2.set_value("nationality", "PotatoCountry")
        person2.commit()

        transaction.commit()

        search = Search("unittest/person")
        search.add_filter("name_first", "Mr")
        search.add_filter("name_last", "Potato Head")
        person = search.get_sobject()
        my.assertEquals( False, person == None )

        # make sure we are no longer in transaction
        my.assertEquals( False, transaction.is_in_transaction() )

        # check the transaction log
        search = Search("sthpw/transaction_log")
        search.add_filter("login", Environment.get_user_name() )
        num_transactions2 = search.get_count()
        results = search.do_search()
        my.assertEquals( num_transactions2, num_transactions + 1 )

        # get the last transaction and undo it
        last = TransactionLog.get_last()
        last.undo()

        search = Search("unittest/person")
        search.add_filter("name_first", "Mr")
        search.add_filter("name_last", "Potato Head")
        person = search.get_sobject()

        my.assertEquals( True, person == None )

        search = Search("unittest/person")
        search.add_filter("name_first", "Mrs")
        search.add_filter("name_last", "Potato Head")
        person = search.get_sobject()

        my.assertEquals( True, person == None )


    def _test_file_undo(my):

        tmpdir = Environment.get_tmp_dir()

        dir = "%s/temp/unittest" % tmpdir
        src = "%s/test_file_src" % tmpdir
        src2 = "%s/test_file_src2" % tmpdir
        dst = "%s/test_file_dst" % dir
        dst2 = "%s/test_file_dst2" % dir

        # make sure everything is clean
        if os.path.exists(src):
            os.unlink(src)
        if os.path.exists(src2):
            os.unlink(src2)
        if os.path.exists(dst):
            os.unlink(dst)
        if os.path.exists(dst2):
            os.unlink(dst2)
        if os.path.exists(dir):
            os.rmdir(dir)


        # initiate a global transaction
        transaction = Transaction.get(create=True)

        # do some operations
        FileUndo.mkdir(dir)

        # create a file
        file = open(src,"w")
        file.write("whatever")
        file.close()

        # create a file
        file = open(src2,"w")
        file.write("whatever2")
        file.close()

        my.assertEquals(os.path.exists(src), True)
        my.assertEquals(os.path.exists(src2), True)

        FileUndo.move(src,dst)
        FileUndo.copy(dst,dst2)
        FileUndo.remove(src2)

        transaction.commit()

        my.assertEquals(True, os.path.exists(dir) )
        my.assertEquals(False, os.path.exists(src) )
        my.assertEquals(False, os.path.exists(src2) )
        my.assertEquals(True, os.path.exists(dst) )
        my.assertEquals(True, os.path.exists(dst2) )

        TransactionLog.get_last().undo()

        my.assertEquals(False, os.path.exists(dir) )
        my.assertEquals(True, os.path.exists(src) )
        my.assertEquals(True, os.path.exists(src2) )
        my.assertEquals(False, os.path.exists(dst) )
        my.assertEquals(False, os.path.exists(dst2) )

        os.unlink(src)
        os.unlink(src2)


    def _test_debug_log(my):
        '''tests that the debug log executes outside of a transaction'''

        # initiate a global transaction
        transaction = Transaction.get(create=True)

        person = Person.create("Mr", "Potato Head", "PotatoLand", "Pretty much looks like a potato")
        person_id = person.get_id()
        person_type = person.get_search_type()

        from pyasm.biz import DebugLog
        log = DebugLog.log("debug", "Unittest Debug In transaction")
        log_id = log.get_id()

        Person.clear_cache()
        transaction.rollback()

        person = Search.get_by_id(person_type, person_id)
        #log = DebugLog.get_by_id(log_id)

        # make sure the person is undone
        my.assertEquals(None, person)

        # make sure the log still exists
        my.assertNotEquals(None, log)





if __name__ == "__main__":
    unittest.main()

