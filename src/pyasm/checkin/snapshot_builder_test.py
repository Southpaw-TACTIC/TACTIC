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
from snapshot_builder import *

class SnapshotBuilderTest(unittest.TestCase):

    def setUp(self):
        batch = Batch()

    def test_all(self):

        builder = SnapshotBuilder()
        builder._add_ref_node("prod/asset", "132", "12", "prp101_01" )
        builder._add_file_node("1234", "maya", "prp100")

        snapshot_xml = builder.to_string()
    
        expected = \
        """<?xml version='1.0' encoding='UTF-8'?>
<snapshot>
  <ref search_type='prod/asset' instance='prp101_01' version='12' search_id='132'/>
  <file type='maya' file_code='1234' name='prp100'/>
</snapshot>
"""

        self.assertEquals(expected, snapshot_xml)






if __name__ == '__main__':
    unittest.main()



