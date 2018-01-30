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

from maya_parser import *

import unittest

class MayaParserTest(unittest.TestCase):
    '''Unit test that tests all of the interactions of Tactic with Maya'''

    def test_all(self):

        file_path = "./test/whatever.ma"
        file_path = "./test/tree004_texture_v002_BAR.ma"
        file_path = "./test/furn004_rig_v001_BAR.ma"
        parser = MayaParser(file_path)


        #parser.set_read_only()
        texture_filter = MayaParserTextureFilter()
        parser.add_filter(texture_filter)
        ref_filter = MayaParserReferenceFilter()
        parser.add_filter(ref_filter)

        parser.parse()

        




if __name__ == "__main__":
    unittest.main()

