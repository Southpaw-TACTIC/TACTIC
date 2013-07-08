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
import tactic

from pyasm.security import *
from comp_checkin import *
from pyasm.application.maya import *

import unittest

class CompTest(unittest.TestCase):

    def setUp(my):
        # intialiaze the framework as a batch process
        my.batch = Batch()

    def test_all(my):
        my._test_fusion_parse()


    def _test_fusion_parse(my):

        file_path = "./test/fusion_sample.comp"

        parser = MayaParser(file_path)
        parser.set_line_delimiter(",")

        fusion_filter = FusionFileFilter()
        parser.add_filter(fusion_filter)
        parser.parse()

        file_outs = fusion_filter.get_file_outs()
        file_ins = fusion_filter.get_file_ins()

        print file_ins




if __name__ == "__main__":
    unittest.main()

