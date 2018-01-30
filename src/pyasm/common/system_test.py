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


__all__ = ["SystemTest"]

import tacticenv
import unittest

import os

from pyasm.security import *

from pyasm.common import *

class SystemTest(unittest.TestCase):

    def test_all(self):
        if os.name == 'nt':
            self.base = 'C:/sthpw/temp'
        else:
            self.base = '/tmp/sthpw/temp'

        self._test_makedirs()

    def tearDown(self):
        # note this will remove base so recreate it
        if not os.path.exists(self.base):
            os.makedirs(self.base)


    def _test_makedirs(self):
        dir = '%s/this/is/a/new/dir' % self.base
        if os.path.exists(dir):
            os.removedirs(dir)

        System().makedirs(dir)
        self.assertEquals( True, os.path.exists(dir) )

        exists = System().exists(dir)
        self.assertEquals( True, exists )

        if os.path.exists(dir):
            os.removedirs(dir)
        self.assertEquals( False, os.path.exists(dir) )

        # test existance
        exists = System().exists(dir)
        self.assertEquals( False, exists )



if __name__ == '__main__':
    Batch()
    unittest.main()



