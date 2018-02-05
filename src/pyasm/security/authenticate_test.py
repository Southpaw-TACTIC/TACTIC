#!/usr/bin/env python
###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

import tacticenv

from pyasm.common import Common, Environment
from pyasm.security import Security, Batch, Authenticate
from pyasm.search import Search

import unittest


class AutocreateAuthenticate(Authenticate):

    def add_user_info(self, user, password):
        user.set_value("email", "test@test.com")

    def verify(self, login_name, password):
        # allow everything
        return True




class AuthenticateTest(unittest.TestCase):

    def test_all(self):
        Batch(project_code='unittest')
        self.security = Environment.get_security()

        self._test_succeed()
        self._test_fail()

        self._test_autocreate()
        self._test_cache()


    def _test_succeed(self):
        # should succeed
        self.security.login_user("admin", "tactic")

    def _test_fail(self):
        # should fail
        try:
            self.security.login_user("foofoo", "tactic")
        except Exception, e:
            if str(e).find("Login/Password") == -1:
                self.fail()


    def _test_autocreate(self):
        from pyasm.common import Config

        Config.set_value("security", "mode", "autocreate", no_exception=True)
        Config.set_value("security", "authenticate_class", "pyasm.security.authenticate_test.AutocreateAuthenticate", no_exception=True)

        mode = Config.get_value("security", "mode", use_cache=False)
        self.assertEquals(mode, "autocreate")



        # verify that the user exists in the database
        search = Search("sthpw/login")
        search.add_filter("login", "foofoo")
        login = search.get_sobject()
        self.assertEquals(None, login)


        from pyasm.search import Transaction
        transaction = Transaction.get(create=True)
        transaction.start()

        self.security.login_user("foofoo", "wow")

        # verify that the user exists in the database
        search = Search("sthpw/login")
        search.add_filter("login", "foofoo")
        login = search.get_sobject()
        self.assertNotEquals(None, login)

        email = login.get_value("email")
        self.assertEquals("test@test.com", email)

        transaction.rollback()

        # after rollback, this user should not exist
        search = Search("sthpw/login")
        search.add_filter("login", "foofoo")
        login = search.get_sobject()
        self.assertEquals(None, login)



    def _test_cache(self):
        from pyasm.common import Config

        Config.set_value("security", "mode", "cache", no_exception=True)
        #Config.set_value("security", "authenticate_class", "pyasm.security.authenticate_test.AutocreateAuthenticate", no_exception=True)
        Config.set_value("security", "authenticate_class", "pyasm.security.mms_authenticate.MMSAuthenticate", no_exception=True)
        mode = Config.get_value("security", "authenticate_class", use_cache=False)

        mode = Config.get_value("security", "mode", use_cache=False)
        self.assertEquals(mode, "cache")


        # verify that the user exists in the database
        search = Search("sthpw/login")
        search.add_filter("login", "foofoo")
        login = search.get_sobject()
        self.assertEquals(None, login)


        from pyasm.search import Transaction
        transaction = Transaction.get(create=True)
        transaction.start()

        self.security.login_user("foofoo", "wow")

        # verify that the user exists in the database
        search = Search("sthpw/login")
        search.add_filter("login", "foofoo")
        login = search.get_sobject()
        self.assertNotEquals(None, login)



if __name__ == "__main__":
    unittest.main()



