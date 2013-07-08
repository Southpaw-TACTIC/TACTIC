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

__all__ = ["SyncFilterTest"]

import tacticenv
from pyasm.security import Batch
from pyasm.biz import Project

from pyasm.search import SearchType, Search

import unittest

from sync_filter import SyncFilter

class SyncFilterTest(unittest.TestCase):

    def setUp(my):
        Batch()
        Project.set_project("unittest")
        

    def test_all(my):

        my._test_security()


    def _test_security(my):

        transaction = '''<transaction>
          <sobject search_type="sthpw/task" parent_type='project/asset' search_code="TASK00001689" action="update">
            <column name="assigned" from="" to="beth"/>
          </sobject>
          <sobject search_type="sthpw/task" parent_type='project/asset' search_code="TASK00001690" action="update">
            <column name="assigned" from="" to="john"/>
          </sobject>
          <sobject search_type="sthpw/note" parent_type='project/asset' search_code="NOTE0001234" action="update">
            <column name="login" from="" to="john"/>
          </sobject>
        </transaction>
        '''
        log = SearchType.create("sthpw/transaction_log")
        log.set_value("transaction", transaction)
        log.set_value("namespace", "demo")

        # deny by project
        rules = '''
        <rules>
        <rule group='project' code='demo2' access='allow'/>
        <rule group='search_type' code='sthpw/task' access='allow'/>
        </rules>
        '''
        sync_filter = SyncFilter(rules=rules, transaction=log)
        sync_filter.execute()
        transaction = sync_filter.get_transaction_xml()
        nodes = transaction.get_nodes("transaction/sobject")
        my.assertEquals(len(nodes), 0)

        # allow by project
        rules = '''
        <rules>
        <rule group='project' code='demo' access='allow'/>
        <rule group='search_type' code='sthpw/task' access='allow'/>
        </rules>
        '''
        sync_filter = SyncFilter(rules=rules, transaction=log)
        sync_filter.execute()
        transaction = sync_filter.get_transaction_xml()
        nodes = transaction.get_nodes("transaction/sobject")
        my.assertEquals(len(nodes), 2)


        # deny 1 by search type
        rules = '''
        <rules>
        <rule group='project' code='demo' access='allow'/>
        <rule group='search_type' code='sthpw/note' access='allow'/>
        </rules>
        '''
        sync_filter = SyncFilter(rules=rules, transaction=log)
        sync_filter.execute()
        transaction = sync_filter.get_transaction_xml()
        nodes = transaction.get_nodes("transaction/sobject")
        my.assertEquals(len(nodes), 1)


        # allow all
        rules = '''
        <rules>
        <rule group='project' code='*' access='allow'/>
        <rule group='search_type' code='*' access='allow'/>
        </rules>
        '''
        sync_filter = SyncFilter(rules=rules, transaction=log)
        sync_filter.execute()
        transaction = sync_filter.get_transaction_xml()
        nodes = transaction.get_nodes("transaction/sobject")
        my.assertEquals(len(nodes), 3)




if __name__ == '__main__':
    unittest.main()



