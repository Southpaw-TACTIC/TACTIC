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

from pyasm.security import Batch
from pyasm.command import Command
from pyasm.prod.biz import Asset
from pyams.prod.maya import *

from maya_checkin import *

class MayaCheckinTest(unittest.TestCase):

    def setUp(self):
        batch = Batch()

    def test_all(self):

        # create a scene that will be checked in
        asset_code = "prp101"
        sid = "12345"

         # create an asset
        mel('sphere -n sphere1')
        mel('circle -n circle1')
        mel('group -n |%s |circle1 |sphere1' % asset_code )

        # convert node into a maya asset
        node = MayaNode("|%s" % asset_code )
        asset_node = MayaAssetNode.add_sid( node, sid )

        # checkin the asset
        checkin = MayaAssetNodeCheckin(asset_node)
        Command.execute_cmd(checkin)

        # create a file from this node
        asset_node.export()






if __name__ == '__main__':
    unittest.main()



