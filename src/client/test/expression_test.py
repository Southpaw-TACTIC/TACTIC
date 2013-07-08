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

    def setUp(my):
        pass

    def test_all(my):

        my.server = TacticServerStub()
        project_code = "unittest"
        my.server.set_project(project_code)

        my.server.start("Expression Test")
        try:
            my._setup()


            my._test_expression()

        except:
            my.server.abort()
            raise
        else:
            my.server.abort()


    def _setup(my):

        city_data = {
            'code': 'los_angeles'
        }

        search_type = "unittest/person"
        my.persons = []
        for i in range(0,4):
            data = {
                'name_first': 'person%s' % i,
                'name_last': 'Test',
                'city_code': 'los_angeles',
                'age': '25'
            }
            person = my.server.insert(search_type, data)
            my.persons.append( person )


    def _test_expression(my):

        # get the people sobjects
        expr = "@SOBJECT(unittest/person)"
        result = my.server.eval(expr)
        my.assertEquals(4, len(result))
        my.assertEquals("los_angeles", result[0].get("city_code") )

        # get a single person
        expr = "@SOBJECT(unittest/person)"
        result = my.server.eval(expr, single=True)
        my.assertEquals("los_angeles", result.get('city_code'))

        # get the first_name
        expr = "@GET(unittest/person.name_first)"
        names = my.server.eval(expr)
        my.assertEquals(len(names), 4)
        #my.assertEquals("person0", names[0])
        #my.assertEquals("person1", names[1])
 
 
        # count the number of people
        expr = "@COUNT(unittest/person)"
        count = my.server.eval(expr)
        my.assertEquals(4, count)

        # get the age of a person
        expr = "@GET(unittest/person.age)"
        age = my.server.eval(expr, my.persons[0], single=True)
        my.assertEquals(25, age)

      
        return
       

if __name__ == "__main__":
    unittest.main()



