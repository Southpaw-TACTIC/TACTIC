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


__all__ = ["ConfigTest"]

import tacticenv
import unittest


from pyasm.security import *

from pyasm.common import *

class ConfigTest(unittest.TestCase):

    def setUp(self):
        self.config = Config()

    def test_get_value(self):
        # check integrity of config parsing

        server = self.config.get_value("database", "server")

        self.failUnless(server, "No definition for database/server in config file" )




if __name__ == '__main__':
    Batch()
    unittest.main()



