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

import unittest


from pyasm.security import *

from pyasm.common import *

class ConfigTest(unittest.TestCase):

    def setUp(my):
        my.config = Config()

    def test_get_value(my):
        # check integrity of config parsing

        server = my.config.get_value("database", "server")

        my.failUnless(server, "No definition for database/server in config file" )




if __name__ == '__main__':
    Batch()
    unittest.main()



