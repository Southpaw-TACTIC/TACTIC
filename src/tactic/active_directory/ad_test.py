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

__all__ = ["ADTest"]

import tacticenv

import unittest

from pyasm.security import Batch
from pyasm.search import SearchType

from ad_authenticate import ADAuthenticate


class ADTest(unittest.TestCase):

    def test_all(self):
        authenticate = ADAuthenticate()

        # put in a valid user
        login_name = 'supervisor'
        password = 'tactic'
        exists = authenticate.verify(login_name, password)
        self.assertEquals(exists, True)

        login = SearchType.create("sthpw/login")
        login.set_value("login", login_name)
        authenticate.add_user_info(login, password)

        # check the user data
        display_name = authenticate.get_user_data("display_name")
        self.assertEquals("Smith, Joe", display_name)

        license_type = authenticate.get_user_data("license_type")
        #self.assertEquals("user", license_type)

        # check the login sobject
        license_type = login.get_value("license_type")
        #self.assertEquals("user", license_type)



if __name__ == '__main__':
    Batch(project_code='unittest')
    unittest.main()



