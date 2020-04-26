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

import tacticenv
from pyasm.security import *
from pyasm.unittest import UnittestEnvironment
from pyasm.biz import Project
import unittest

class WidgetTest(unittest.TestCase):

    def setUp(self):
        # intitialize the framework as a batch process
        self.batch = Batch()

    def test(self):
        pass



if __name__ == "__main__":
    unittest.main()

