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


import os,unittest

from pyasm.unittest import *

from pyasm.security import *
from pyasm.search import *
from .snapshot_builder import *

class SnapshotBuilderTest(unittest.TestCase):

    def setUp(self):
        batch = Batch()

    def test_all(self):
        """
        Tests SnapshotBuilder by checking that the snapshot_xml returns nodes added to the snapshot.
        """
        
        test_env = Sample3dEnvironment()
        test_env.create()

        
        transaction = Transaction.get(create=True)

        try:
            asset = SearchType.create("prod/asset")
            asset.set_value("code", "132")
            asset.commit()

            builder = SnapshotBuilder()
            builder.add_ref(asset, context="publish", version="12", instance_name="prp101_01" )

            builder._add_file_node("1234", "prp100", {'type': 'maya'})
            snapshot_xml = builder.to_string()
        
            expected = """<snapshot>\n  <ref version="12" search_type="prod/asset?project=sample3d" instance="prp101_01" tag="main" context="publish" search_code="132" search_id="2"/>\n  <file file_code="1234" name="prp100" type="maya"/>\n</snapshot>\n"""

            self.assertEquals(expected, snapshot_xml)
        finally:
            transaction.rollback()
            test_env.delete()





if __name__ == '__main__':
    unittest.main()



