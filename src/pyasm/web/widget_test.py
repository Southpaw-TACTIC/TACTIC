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
from pyasm.search import Search

class WidgetTest(unittest.TestCase):

    def test_all(my):
        # start batch environment
        Batch(login_code='admin')

        test_env = UnittestEnvironment()
        test_env.create()
        Project.set_project('admin')

       
        try:
            my._test_csv_export()
        finally:
            test_env.delete()

    def _test_url(my):

        base = "http://www.yahoo.com"
        url = Url( base )
        url.set_option("widget","EditWdg")
        url.set_option("args","person")
        
        url_str = url.get_url()

        my.assertEquals("%s?widget=EditWdg&args=person" % base, url_str)


    def _test_state(my):

        # set the state
        state = WebState.get()
        state.add_state("episode_code", "TF01A")
        state.add_state("scene", "TF01A-003")

        base = "http://www.yahoo.com"
        url = Url(base)
        state.add_state_to_url(url)

        url_str = url.to_string()

        my.assertEquals("%s?episode_code=TF01A&scene=TF01A-003" % base, url_str)

    def _test_csv_export(my):
        from tactic.ui.widget import CsvExportWdg
        view = 'table'
        search_type ='sthpw/task'
        search_view = 'auto_search:table'
        #search_view = ''
        simple_search_view = 'simple_search'
        search_class =''
        mode = 'export_matched'
        element_name=  'project_tasks'
        filter =  [{"prefix":"main_body","main_body_enabled":"on","main_body_column":"project_code","main_body_relation":"is","main_body_value":"{$PROJECT}"}, {"prefix":"main_body","main_body_enabled":"on","main_body_column":"search_type","main_body_relation":"is not","main_body_value":"sthpw/project"}]
        
        from pyasm.common import jsondumps, jsonloads
        values  = {'json': jsondumps(filter)}
        element_names = ['code','id','description']
        server = TacticServerStub(protocol='xmlrpc')
        current_project = 'vfx'
        server.set_project(current_project)

        rtn = server.get_widget('tactic.ui.widget.CsvExportWdg', args={'search_type':search_type, 'view':view,\
            'filter': filter, 'element_name': element_name, 'show_search_limit':'false', 'search_limit':-1, 'search_view':search_view, \
            'element_names': element_names, 'mode':mode, 'search_class':search_class, 'simple_search_view':simple_search_view,\
            'init_load_num':-1, 'test':True}, values=values )
        expected_columns = ['code','id','description']
        expected_sql = '''SELECT "sthpw"."public"."task".* FROM "sthpw"."public"."task" WHERE ( "task"."project_code" = \'%s\' AND ( "task"."search_type" != \'sthpw/project\' OR "task"."search_type" is NULL ) ) AND ("task"."s_status" != \'retired\' or "task"."s_status" is NULL) AND ("task"."s_status" != \'retired\' or "task"."s_status" is NULL) AND ("task"."s_status" != \'retired\' or "task"."s_status" is NULL) ORDER BY "task"."search_type", "task"."search_code"'''%current_project

        expr = "@COUNT(sthpw/task['project_code','%s']['search_type','!=','sthpw/project])"%current_project
        expected_count = Search.eval(expr, single=True)
        
        rtn = jsonloads(rtn)
        my.assertEquals(expected_columns, rtn.get('columns'))
        my.assertEquals(expected_sql, rtn.get('sql'))
        my.assertEquals(expected_count, rtn.get('count'))


        mode = 'export_displayed'
        selected_search_keys = ['sthpw/task?id=4385','sthpw/task?id=4386','sthpw/task?id=4387']
        rtn = server.get_widget('tactic.ui.widget.CsvExportWdg', args={'search_type':search_type, 'view':view,\
            'filter': filter, 'element_name': element_name, 'show_search_limit':'false', 'search_limit':-1, 'search_view':search_view, \
            'element_names': element_names, 'mode':mode, 'search_class':search_class, 'simple_search_view':simple_search_view,\
            'init_load_num':-1, 'test':True, 'selected_search_keys': selected_search_keys}, values=values )
        
        expected_count = 3
        rtn = jsonloads(rtn)
        my.assertEquals(expected_columns, rtn.get('columns'))
        my.assertEquals(expected_count, rtn.get('count'))
        
        


if __name__ == '__main__':
    unittest.main()



