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

from pyasm.common import Container, jsonloads, jsondumps, Environment, Xml
from pyasm.security import Batch
from pyasm.search import Search, SearchType
from pyasm.command import Command
from pyasm.unittest import UnittestEnvironment

import unittest

import requests


__all__ = ['TestCmd', 'TestUpdateCmd']

SERVER_URL = "http://192.168.56.105"
PROJECT_CODE = "unittest"
LOGIN_TICKET = "25041f619db4b69a63af12859c71d6cc"


class RestAPITest(unittest.TestCase):

    def _get_rest_url(self):
        project_code = PROJECT_CODE
        url = SERVER_URL
        rest_url = url + "/default/" + project_code + "/REST/"
        return rest_url 

    def test_all(self):

        Batch()

        test_env = UnittestEnvironment()
        test_env.create()

        try:
            self._test_ping()
            self._test_args()
            self._test_execute_cmd()
            self._test_kwargs()

        finally:
            test_env.delete()


    def _test_ping(self):
        login_ticket = LOGIN_TICKET
        rest_url = self._get_rest_url()

        data = {
            'login_ticket': login_ticket,
            'method': 'ping',
        }

        r = requests.post(rest_url, data=data)
        ret_val = r.json()

        # FIXME: This should return data structure
        self.assertEqual(ret_val, "OK")


    def _test_args(self):
        '''Tests use args parameter

        login_ticket -  login_ticket
        method - API method
        args - list of arguments

        '''
        task = SearchType.create("sthpw/task")
        task.commit()

        search_key = task.get_search_key()


        # Make update to task description
        description = 'Test description'
        update_data = {
            'description': description
        }
        args = (search_key, update_data)
        args = jsondumps(args)

        login_ticket = LOGIN_TICKET
        rest_url = self._get_rest_url()

        data = {
            'login_ticket': login_ticket,
            'method': 'update',
            'args': args
        }

        r = requests.post(rest_url, data=data)
        ret_val = r.json()
        updated_description = ret_val.get("description")
        self.assertEqual(description, updated_description)


    def _test_execute_cmd(self):
        '''Tests use of class_name and args parameter
        for API method execute_cmd

        login_ticket -  login_ticket
        method - execute_cmd
        class_name - Cmd class name
        args - Cmd kwargs

        '''

        login_ticket = LOGIN_TICKET
        rest_url = self._get_rest_url()

        bar =  '123'
        cmd_kwargs = {
            'foo': {
                'bar': bar
            }
        }
        cmd_kwargs = jsondumps(cmd_kwargs)

        data = {
            'login_ticket': login_ticket,
            'method': 'execute_cmd',
            'class_name': 'tactic.protocol.TestCmd',
            'args': cmd_kwargs
        }

        r = requests.post(rest_url, data=data)
        ret_val = r.json()
        info = ret_val.get("info")
        bar2 = info.get('bar2')
        self.assertEqual(bar, bar2)


    def _test_kwargs(self):
        '''Tests use kwargs parameter

        login_ticket -  login_ticket
        method - API method
        kwargs - dict of arguments for method

        '''


        # Setup
        task = SearchType.create("sthpw/task")
        task.commit()

        search_key = task.get_search_key()

        # Make update
        description = 'Test description'
        update_data = {
            'description': description
        }

        login_ticket = LOGIN_TICKET

        rest_url = self._get_rest_url()
        data = {
            'login_ticket': login_ticket,
            'method': 'update',
            'kwargs': jsondumps({
                'search_key': search_key,
                'data': update_data
             })
        }

        r = requests.post(rest_url, data=data)
        ret_val = r.json()

        updated_description = ret_val.get("description")
        self.assertEqual(updated_description, description)



class TestCmd(Command):


    def execute(self):
        foo = self.kwargs.get('foo')
        bar = foo.get('bar')
        return {
            'bar2': bar    
        }


class TestUpdateCmd(Command):


    def __init__(self, **kwargs):
        super(TestUpdateCmd, self).__init__(**kwargs)
        self.update = True


    def execute(self):
        print(self.kwargs)







if __name__ == "__main__":
    unittest.main()


