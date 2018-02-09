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

import os,unittest

from pyasm.unittest import *

from pyasm.security import *
from pyasm.biz import *

from perforce_checkin import *

class CheckinTest(unittest.TestCase):


    def test_all(self):

        Batch()

        self._test_perforce()


    def _test_perforce(self):

        perforce = PerforceTransaction()
        perforce.start()

        # create a new file and check it in
        path = "/tmp/test.txt"
        file = open(path, "w")
        file.write("Hello world\n")
        file.write("Hello world\n")
        file.close()

        perforce.checkin(path)

        # create a new file and check it in
        path = "/tmp/test2.txt"
        file = open(path, "w")
        file.write("Hello world\n")
        file.write("Hello world\n")
        file.close()

        perforce.checkin(path)

        

        perforce.commit()







if __name__ == '__main__':
    unittest.main()









