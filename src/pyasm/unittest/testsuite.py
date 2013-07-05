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

import tacticenv

import unittest, sys

from pyasm.common.common_test import *
from pyasm.common.system_test import *
from pyasm.common.config_test import *
from pyasm.biz.expression_test import *
from pyasm.search.sql_test import *
from pyasm.security.security_test import *
from pyasm.search.transaction_test import *
from pyasm.command.command_test import *
from pyasm.search.search_test import *
from pyasm.biz.biz_test import *
from pyasm.biz.naming_test import *
from pyasm.checkin.checkin_test import *


#from pyasm.web.html_wdg_test import *
#from pyasm.web.web_app_test import *
from pyasm.widget.widget_test import *
from pyasm.widget.widget_config_test import *
#from pyasm.prod.prod_test import *
#from pyasm.prod.biz.shot_test import *
#from pyasm.prod.load.loader_test import *

# import the client api test, which is separate
install_dir = tacticenv.get_install_dir()
sys.path.insert(0, "%s/src/client/test" % install_dir)
from client_api_test import *
#from application_api_test import *




def main(args):

    tests_to_perform = []
    if len(args) == 1:
        tests_to_perform.append(args[0])

    uber_suite = unittest.TestSuite()

    test_list = [
                    CommonTest,
                    SystemTest,
                    ConfigTest,
                    SqlTest,
                    SecurityTest,
                    TransactionTest,
                    CommandTest, # CommandTest consistently fails due to inability to detect trigger as a subclass of Trigger class
                    SearchTest,
                    BizTest,
                    NamingTest,
                    CheckinTest,
                    WidgetTest,
                    WidgetConfigTest,
                    #HtmlWdgTest,
                    #WebAppTest,
                    #WidgetTest,
                    #ProdTest,
                    #ShotTest,
                    #LoaderTest,
                    ExpressionTest,
                    ClientApiTest,
                    #ApplicationApiTest
                ]

    # check if test_to_perform exist
    test_classes = [ test.__name__ for test in test_list ]
    for test_to_perform in tests_to_perform:
        if test_to_perform not in test_classes:
            print
            print "ERROR: Test [%s] does not exist in Test Suite" % test_to_perform
            return


    for test in test_list:
        test_class = test.__name__
        if tests_to_perform and test_class not in tests_to_perform:
            continue

        suite = unittest.makeSuite( test )
        uber_suite.addTest(suite)

    runner = unittest.TextTestRunner()
    runner.run(uber_suite)



if __name__ == '__main__':
    Batch()
    executable = sys.argv[0]
    args = sys.argv[1:]
    main(args)

