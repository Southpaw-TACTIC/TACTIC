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

import unittest

import os

from pyasm.security import *

from pyasm.common import *

class SystemTest(unittest.TestCase):

    def test_all(my):
        if os.name == 'nt':
            my.base = 'C:/sthpw/temp'
        else:
            my.base = '/tmp/sthpw/temp'

        my._test_makedirs()

    def tearDown(my):
        # note this will remove base so recreate it
        if not os.path.exists(my.base):
            os.makedirs(my.base)


    def _test_makedirs(my):
        dir = '%s/this/is/a/new/dir' % my.base
        if os.path.exists(dir):
            os.removedirs(dir)

        System().makedirs(dir)
        my.assertEquals( True, os.path.exists(dir) )

        exists = System().exists(dir)
        my.assertEquals( True, exists )

        if os.path.exists(dir):
            os.removedirs(dir)
        my.assertEquals( False, os.path.exists(dir) )

        # test existance
        exists = System().exists(dir)
        my.assertEquals( False, exists )



if __name__ == '__main__':
    Batch()
    unittest.main()



