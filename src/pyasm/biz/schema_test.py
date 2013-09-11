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

__all__ = ["SchemaTest"]

import tacticenv
import os
import unittest

from pyasm.security import Batch

from pyasm.unittest import UnittestEnvironment, Sample3dEnvironment

from pyasm.search import SearchType, Search, Transaction
from pyasm.biz import Project
from schema import Schema

class SchemaTest(unittest.TestCase):

    def test_all(my):
        Batch()
        from pyasm.web.web_init import WebInit
        WebInit().execute()

        test_env = UnittestEnvironment()
        test_env.create()
        my.transaction = Transaction.get(create=True)
        try:
            my._test_multiple_schema()
        finally:
            my.transaction.rollback()
            Project.set_project('unittest')

            test_env.delete()


    def _test_multiple_schema(my):

        # add a second schema
        new_schema = SearchType.create("sthpw/schema")
        new_schema.set_value("project_code", "unittest")
        new_schema.set_value("code", "second_schema")
        new_schema.set_value("schema", '''
<schema>
    <search_type name="test/node1"/>
    <search_type name="test/node2"/>
    <search_type name="test/node3"/>
    <search_type name="test/node4"/>
    <connect from="test/node1" to="test/node2"/>
    <connect from="test/node2" to="test/node3"/>
    <connect from="test/node3" to="test/node4"/>
</schema>''')
        new_schema.commit()

        schema = Schema.get(reset_cache=True)
        print schema.get_value("schema")




if __name__ == '__main__':
    unittest.main()



