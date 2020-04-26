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
from tactic_client_lib import TacticServerStub

import unittest

class ExpressionApiTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_all(self):

        self.server = TacticServerStub()
        project_code = "unittest"
        self.server.set_project(project_code)

        self.server.start("Expression Test")
        try:
            self._setup()


            self._test_expression()

        except:
            self.server.abort()
            raise
        else:
            self.server.abort()


    def _setup(self):

        city_data = {
            'code': 'los_angeles'
        }

        search_type = "unittest/person"
        self.persons = []
        for i in range(0,4):
            data = {
                'name_first': 'person%s' % i,
                'name_last': 'Test',
                'city_code': 'los_angeles',
                'age': '25'
            }
            person = self.server.insert(search_type, data)
            self.persons.append( person )


    def _test_expression(self):

        # get the people sobjects
        expr = "@SOBJECT(unittest/person)"
        result = self.server.eval(expr)
        self.assertEquals(4, len(result))
        self.assertEquals("los_angeles", result[0].get("city_code") )

        # get a single person
        expr = "@SOBJECT(unittest/person)"
        result = self.server.eval(expr, single=True)
        self.assertEquals("los_angeles", result.get('city_code'))

        # get the first_name
        expr = "@GET(unittest/person.name_first)"
        names = self.server.eval(expr)
        self.assertEquals(len(names), 4)
        #self.assertEquals("person0", names[0])
        #self.assertEquals("person1", names[1])
 
 
        # count the number of people
        expr = "@COUNT(unittest/person)"
        count = self.server.eval(expr)
        self.assertEquals(4, count)

        # get the age of a person
        expr = "@GET(unittest/person.age)"
        age = self.server.eval(expr, self.persons[0], single=True)
        self.assertEquals(25, age)

      
        return
       

if __name__ == "__main__":
    unittest.main()



