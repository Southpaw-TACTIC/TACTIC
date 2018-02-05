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

from sequence import *
from shot import *

import unittest

class ShotTest(unittest.TestCase):

    def test_sequence(self):
        sequence = Sequence.get_by_code("001SHO")

        shot = sequence.get_shot_by_code("0001")

        description = shot.get_value("description")

        self.assertEquals("Sequence Wide Shot", description )




if __name__ == "__main__":
    unittest.main()

