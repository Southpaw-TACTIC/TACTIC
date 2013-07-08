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

    def add_user_info(my, user, password):
        user.set_value("email", "test@test.com")

    def verify(my, login_name, password):
        # allow everything
        return True




class AuthenticateTest(unittest.TestCase):

    def test_all(my):
        Batch(project_code='unittest')
        my.security = Environment.get_security()

        my._test_succeed()
        my._test_fail()

        my._test_autocreate()
        my._test_cache()


    def _test_succeed(my):
        # should succeed
        my.security.login_user("admin", "tactic")

    def _test_fail(my):
        # should fail
        try:
            my.security.login_user("foofoo", "tactic")
        except Exception, e:
            if str(e).find("Login/Password") == -1:
                my.fail()


    def _test_autocreate(my):
        from pyasm.common import Config

        Config.set_value("security", "mode", "autocreate", no_exception=True)
        Config.set_value("security", "authenticate_class", "pyasm.security.authenticate_test.AutocreateAuthenticate", no_exception=True)

        mode = Config.get_value("security", "mode", use_cache=False)
        my.assertEquals(mode, "autocreate")



        # verify that the user exists in the database
        search = Search("sthpw/login")
        search.add_filter("login", "foofoo")
        login = search.get_sobject()
        my.assertEquals(None, login)


        from pyasm.search import Transaction
        transaction = Transaction.get(create=True)
        transaction.start()

        my.security.login_user("foofoo", "wow")

        # verify that the user exists in the database
        search = Search("sthpw/login")
        search.add_filter("login", "foofoo")
        login = search.get_sobject()
        my.assertNotEquals(None, login)

        email = login.get_value("email")
        my.assertEquals("test@test.com", email)

        transaction.rollback()

        # after rollback, this user should not exist
        search = Search("sthpw/login")
        search.add_filter("login", "foofoo")
        login = search.get_sobject()
        my.assertEquals(None, login)



    def _test_cache(my):
        from pyasm.common import Config

        Config.set_value("security", "mode", "cache", no_exception=True)
        #Config.set_value("security", "authenticate_class", "pyasm.security.authenticate_test.AutocreateAuthenticate", no_exception=True)
        Config.set_value("security", "authenticate_class", "pyasm.security.mms_authenticate.MMSAuthenticate", no_exception=True)
        mode = Config.get_value("security", "authenticate_class", use_cache=False)

        mode = Config.get_value("security", "mode", use_cache=False)
        my.assertEquals(mode, "cache")


        # verify that the user exists in the database
        search = Search("sthpw/login")
        search.add_filter("login", "foofoo")
        login = search.get_sobject()
        my.assertEquals(None, login)


        from pyasm.search import Transaction
        transaction = Transaction.get(create=True)
        transaction.start()

        my.security.login_user("foofoo", "wow")

        # verify that the user exists in the database
        search = Search("sthpw/login")
        search.add_filter("login", "foofoo")
        login = search.get_sobject()
        my.assertNotEquals(None, login)



if __name__ == "__main__":
    unittest.main()



