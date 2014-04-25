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
import unittest

from pyasm.security import *
from widget import *

from client.tactic_client_lib import TacticServerStub
from web_state import *

from pyasm.unittest import UnittestEnvironment
from pyasm.common import Environment
from pyasm.biz import Project

class WidgetTest(unittest.TestCase):

    def test_all(my):
        # start batch environment
        Batch(login_code='admin')

        test_env = UnittestEnvironment()
        test_env.create()
        Project.set_project('admin')

       
        try:
            my.test_csv_export()
        finally:
            test_env.delete()

    def test_url(my):

        base = "http://www.yahoo.com"
        url = Url( base )
        url.set_option("widget","EditWdg")
        url.set_option("args","person")
        
        url_str = url.get_url()

        my.assertEquals("%s?widget=EditWdg&args=person" % base, url_str)


    def test_state(my):

        # set the state
        state = WebState.get()
        state.add_state("episode_code", "TF01A")
        state.add_state("scene", "TF01A-003")

        base = "http://www.yahoo.com"
        url = Url(base)
        state.add_state_to_url(url)

        url_str = url.to_string()

        my.assertEquals("%s?episode_code=TF01A&scene=TF01A-003" % base, url_str)

    def test_csv_export(my):
        from tactic.ui.panel import TableLayoutWdg
        view = 'table'
        search_type ='sthpw/task'
        search_view = 'auto_search:table'
        simple_search_view = 'simple_search'
        search_class =''
        server = TacticServerStub(protocol='xmlrpc')
        server.set_project('admin')
        rtn = server.get_widget('tactic.ui.panel.TableLayoutWdg', {'search_type':search_type, 'view':view,\
                'show_search_limit':'false', 'search_limit':-1, 'search_view':search_view,\
                'search_class':search_class, 'simple_search_view':simple_search_view, 'init_load_num':-1})
        

        


if __name__ == '__main__':
    unittest.main()



