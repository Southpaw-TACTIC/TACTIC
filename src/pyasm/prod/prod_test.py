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

from pyasm.search import *
from pyasm.prod.biz import *

import unittest

class ProdTest(unittest.TestCase):

    def setUp(self):
        db = DbContainer.get("prod")
        db.start()

    def tearDown(self):
        db = DbContainer.get("prod")
        db.rollback()
        #db.commit()


    def create_production(self):
        '''function to create a test production'''

        # create the sequence
        seq_code = "000TST"
        seq_desc = "Test Sequence"
        sequence = Sequence.create(seq_code,seq_desc)

        # create a shot
        shot_code = "0000"
        shot_desc = "Test Shot"
        shot = Shot.create(sequence, shot_code, shot_desc)

        # create some assets
        cow_code = "chr998"
        cow_name = "cow"
        cow_asset_type = "chr"
        cow_desc = "It's a cow!"
        cow = Asset.create( cow_code, cow_name, cow_asset_type, cow_desc )

        pig_code = "chr999"
        pig_name = "pig"
        pig_asset_type = "chr"
        pig_desc = "It's a pig!"
        pig = Asset.create( pig_code, pig_name, pig_asset_type, pig_desc )

        # add these assets to the shot
        shot.add_asset(cow,"cow_left")
        shot.add_asset(cow,"cow_right")
        shot.add_asset(pig,"piggy")

        instances = shot.get_all_instances()
        self.assertEquals(3, len(instances))




        


    def test_prod(self):

        self.create_production()


if __name__ == "__main__":
    unittest.main()

