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

from asset import *
from shot import *

import unittest

class BizTest(unittest.TestCase):
    '''Unit test that tests all of the interactions of Tactic with Maya'''

    def test_all(my):

        Batch()
        my._test_parent()


    def _test_parent(my):

        SearchType.set_global_template("prod", "bar")

        parent_search_type = "prod/shot"
        child_search_type = "prod/instance"
        ref_search_type = "prod/asset"

        # Very generic code
        parent_code = "00001"
        search = Search(parent_search_type)
        search.add_filter("code", parent_code)
        parent = search.get_sobject()

        children = parent.get_all_children(child_search_type)
        for child in children:
            reference = child.get_reference(ref_search_type)
            print reference.get_code()



        # This is more readable, but shot can be replace by shot easily
        SearchType.set_global_template("prod", "flash")
        shot_search_type = "flash/shot"
        instance_search_type = "flash/instance"
        asset_search_type = "flash/asset"


        shot_code = "TF01A-001"
        search = Search(shot_search_type)
        search.add_filter("code", shot_code)
        shot = search.get_sobject()

        instances = shot.get_all_children(instance_search_type)
        for instance in instances:
            asset = instance.get_parent(asset_search_type)
            print asset.get_code()



        # create test






if __name__ == "__main__":
    unittest.main()

