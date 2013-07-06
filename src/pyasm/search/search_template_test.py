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

import tacticenv
from pyasm.security import *
from pyasm.command import *

from sql import *
from search import *

import unittest


class TestCmd(Command):

    def __init__(my, sobject):
        my.sobject = sobject


    def execute(my):
        my.sobject.set_value("description", "whatever2")
        my.sobject.commit()

        my.description = "changed description to 'whatever'"




class SearchTest(unittest.TestCase):


    def setUp(my):
        Batch()

    def test_all(my):
        my._test_search_type()


    def _test_search_type(my):
        '''tests search type as an object'''

        # set the template and instantiate
        SearchType.set_global_template("prod", "prod2")
        search_type = SearchType.get("prod/template")
    
        # now switch the template
        SObjectFactory.set_template("prod", "prod")
        search_type2 = SearchType.get("prod/template")

        print search_type.get_base_key()
        print search_type.get_full_key()

        my.assertEquals("prod/template", search_type.get_base_key())
        my.assertEquals("prod/template?prod=prod2",search_type.get_full_key())

        search = Search(search_type)
        sobjects = search.do_search()

        sobject = sobjects[0]

        cmd = TestCmd(sobject)
        Command.execute_cmd(cmd)
        



if __name__ == "__main__":
    unittest.main()

