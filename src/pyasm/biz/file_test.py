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

import unittest

from pyasm.security import *

from file import FileRange


class FileTest(unittest.TestCase):


    def setUp(my):

        # start batch environment
        Batch()


    def tearDown(my):
        pass


    def test_all(my):
        my._test_sequence()


    def _test_sequence(my):

        data = '''
        test001/IM-0001-0013.png
        '''
        data = [x.strip() for x in data.strip().split("\n") if x]
        print data
        FileRange.check(data)

        data = '''
        test001/IM-0001-0013.png
        test001/IM-0001-0012.png
        test001/IM-0001-0010.png
        test001/IM-0001-0009.png
        test001/IM-0001-0007.png
        test001/IM-0001-0004.png
        test001/IM-0001-0019.png
        test001/IM-0001-0005.png
        test001/IM-0001-0011.png
        test001/IM-0001-0008.png
        test001/IM-0001-0020.png
        test001/IM-0001-0021.png
        test001/IM-0001-0006.png
        test001/IM-0001-0014.png
        test001/IM-0001-0002.png
        test001/IM-0001-0018.png
        test001/IM-0001-0001.png
        test001/IM-0001-0017.png
        test001/IM-0001-0003.png
        test001/IM-0001-0015.png
        test001/IM-0001-0016.png
        '''
        data = [x.strip() for x in data.strip().split("\n") if x]
        print data
        FileRange.check(data)

        print

        data = '''
        Frame01.jpg
        Frame02.jpg
        Frame03.jpg
        Frame004.jpg
        Frame05.jpg
        Frame07.jpg
        '''
        data = [x.strip() for x in data.strip().split("\n") if x]
        FileRange.check(data)

        print

        data = '''
        Frame03.jpg
        Frame04.jpg
        Frame05.jpg
        Frame06.jpg
        Frame07.jpg
        Frame08.jpg
        '''
        data = [x.strip() for x in data.strip().split("\n") if x]
        FileRange.check(data)





if __name__ == "__main__":
    unittest.main()

