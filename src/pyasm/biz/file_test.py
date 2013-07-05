#!/usr/bin/env python
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

__init__ = ["FileTest"]

import tacticenv

from pyasm.security import *

from file import *

import unittest, os


class FileTest(unittest.TestCase):


    def setUp(my):

        # start batch environment
        Batch()


    def tearDown(my):
        pass


    def test_all(my):
        my._test_file_code()


    def _test_file_code(my):

        file_name = "/tmp/cow.ma"
        file_code = "1238BAR"
        full_path = "/tmp/cow_0001238BAR.ma"

        full_file_name = File.add_file_code(file_name, file_code)
        my.assertEquals(full_path, full_file_name)

        extract_id = File.extract_file_code(full_path)
        my.assertEquals(file_code, extract_id)



    def _test_icon_creator(my):

        dir = os.path.dirname(file.__file__)
        file_path = "%s/sthpw_maya.jpg" % dir
        creator = IconCreator(file_path)

        creator.create_icons()

        web_path = creator.get_web_path()
        icon_path = creator.get_icon_path()
        
        my.assertEquals( True, os.path.exists(web_path) )
        my.assertEquals( True, os.path.exists(icon_path) )

        os.unlink(web_path)
        os.unlink(icon_path)





if __name__ == "__main__":
    unittest.main()

