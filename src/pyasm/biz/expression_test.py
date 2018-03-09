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

__all__ = ["ExpressionTest"]

import tacticenv

import unittest
import random
import types
import math
import re

from pyasm.common import Environment, Date, Common
from pyasm.security import Batch
from pyasm.search import Transaction, SearchType, Search, SearchKey, SObject, SearchException
from pyasm.unittest import Person
from task import Task
from project import Project

from pyasm.unittest import UnittestEnvironment, Sample3dEnvironment

from expression import *

import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ExpressionTest(unittest.TestCase):

    def test_all(self):

        Batch()

        test_env = UnittestEnvironment()
        test_env.create()
        sample3d_env = Sample3dEnvironment()
        sample3d_env.create()

        Project.set_project("unittest")


        self.parser = ExpressionParser()

        self.transaction = Transaction.get(create=True)
        try:
            user = self.parser.eval("@SOBJECT(sthpw/login['login','ben'])")
            if not user:
                from tactic_client_lib import TacticServerStub
                server = TacticServerStub.get()
                server.insert_update('sthpw/login?code=ben', {'login':'ben', 'code':'ben','first_name':'Ben'})
              
            self.city = SearchType.create("unittest/city")
            self.city.set_value("code", "los_angeles")
            self.city.set_value("name", "LA")
            self.city.set_value("country_code", "USA")
            self.city.commit()

            self.city2 = SearchType.create("unittest/city")
            self.city2.set_value("code", "new_york")
            self.city2.set_value("country_code", "USA")
            self.city2.commit()

            self.country = SearchType.create("unittest/country")
            self.country.set_value("code", "USA")
            self.country.commit()

            Task.create(self.country, "p1", "Task 1", context='p1')
            Task.create(self.country, "p2", "Task 2", context='p2')

            desc = u'Task 3 \xe2\x80\x9cHELLO"'.encode('utf-8')
            self.country_task = Task.create(self.country, "p3", "Task 3", context='p3')
            self.country_task.set_value('priority', '4')
            self.country_task.set_value('description', desc)

            self.country_task.commit()

            # city task
            self.city_task = Task.create(self.city, "los_angeles", "City Task 1", context='City')  
            self.city_task.set_value('priority', '5')
            self.city_task.commit()

            self.city_task2 = Task.create(self.city, "los_angeles2", "City Task 2", context='City')   
            # done for test_args
            self.city_task.set_value('status','LA')
            self.city_task.set_value('assigned','admin')
            self.city_task.commit()
            
            self.persons = []
            for i in range(0, 8):

                age = random.randint(20, 70)

                person = Person.create( "person%s" % i, "Joe",
                        "Smith%s" % i, "Fake Unittest Person")

                if i != 4:
                    # keep one of them empty
                    person.set_value("age", age)


                person.set_value("city_code", "los_angeles")
                person.set_value("birth_date", "2000-12-25")
                person.set_now()
                if i > 4 :
                    person.set_value('metadata','unittest')

                person.commit()
                
                self.persons.append(person)

            self._test_instance()
            self._test_utf8()
            self._test_palette()
            self._test_related_sobject()
            self._test_input_search()

            self._test_return_types()
            self._test_file()
            self._test_string()
            self._test_literal()
            self._test_loop()

            self._test_var()
            self._test_new_parser()
            self._test_simple()
            self._test_single()
            self._test_args()

            self._test_composite()
            self._test_dates()
            self._test_filter()
            self._test_paragraph()
            self._test_op()
            self._test_syntax_error()
            self._test_regex()
            self._test_conditional()
            self._test_update()
            self._test_custom_layout()
            self._test_color()
            self._test_connection()
            self._test_cache()
            self._test_cross_proj_count()

        finally:
            self.transaction.rollback()

            test_env.delete()
            sample3d_env.delete()

    def _test_cross_proj_count(self):

        Project.set_project("sample3d")
        expression = "@COUNT(prod/shot?project=sample3d)"
        result = self.parser.eval(expression)
        count = 30
        self.assertEquals(count, result)
        expression = "@COUNT(prod/sequence?project=sample3d.prod/shot)"
        result = self.parser.eval(expression)
        count = 30
        self.assertEquals(count, result)

        expression = "@COUNT(prod/sequence?project=sample3d.prod/shot?project=sample3d)"
        result = self.parser.eval(expression)
        count = 30
        self.assertEquals(count, result)

        expression = "@COUNT(prod/sequence?project=sample3d)"
        result = self.parser.eval(expression)
        count = 1
        self.assertEquals(count, result)
        
        Project.set_project("unittest")

    def _test_utf8(self):
        desc = u'Task 3 \xe2\x80\x9cHELLO"'.encode('utf-8')
        expr3 = "@GET(.description)"
        actual_desc = self.parser.eval(expr3, sobjects=self.country_task, single=True)
        
        self.assertEquals(True, isinstance(actual_desc, unicode))
        # the returned unicode needs to be encoded as str
        actual_desc = actual_desc.encode('utf-8')
        self.assertEquals(desc, actual_desc)


        
        
    def _test_simple(self):

        # do some precalculateion
        sum = 0
        person1_age = 0
        for idx, person in enumerate(self.persons):
            value = person.get_value('age')
            if idx == 1:
                person1_age = value
            if value:
                sum += value
        avg = float(sum) / len(self.persons)
        count = len(self.persons)

        person = self.persons[0]
        age = person.get_value("age")
        name_first = person.get_value("name_first")

        # test shorthand
        expression = "@GET(.age)"
        result = self.parser.eval(expression, person, single=True)
        self.assertEquals(age, result)

        # test shorthand with quotes
        expression = "@GET('.age')"
        result = self.parser.eval(expression, person)
        self.assertEquals([age], result)


        expression = "@GET(.name_first)"
        result = self.parser.eval(expression, person)
        self.assertEquals([name_first], result)

        # TODO: this should return a list
        expression = "@GET(.name_first)"
        result = self.parser.eval(expression, self.persons)
        #self.assertEquals(name_first, result)
        self.assertEquals("person0", result[0])
        self.assertEquals("person1", result[1])


        # test boolean column
        expression = "@GET(sthpw/snapshot['is_latest','true'].code)"
        result = self.parser.eval(expression, single=True)

        expression = "@GET(sthpw/snapshot['code','%s'].is_latest)==True" %result
        
        result = self.parser.eval(expression)
        self.assertEquals(True, result)

    

        # evaluate the total age ... NOTE: {} means stringify, @SOBJECT is assumed
        expression = "{@COUNT(unittest/person)} people"
        result = self.parser.eval(expression, self.city)
        self.assertEquals("%s people" % count, result)

        # use the redundant @SOBJECT 
        expression = "{@COUNT(@SOBJECT(unittest/person))} people"
        result = self.parser.eval(expression, self.city)
        self.assertEquals("%s people" % count, result)
        
        # use the redundant @SOBJECT 
        expression = "{@COUNT(@SOBJECT(unittest/person['name_first','person1']['age','>','1']))} person"
        result = self.parser.eval(expression, self.city)
        self.assertEquals("1 person" , result)

        # use the @UNIQUE which requires @SOBJECT
        expression = "@COUNT(@UNIQUE(@SOBJECT(unittest/person)))"
        result = self.parser.eval(expression, self.city)
        self.assertEquals( count, result)



        # test sum
        expression = "{@SUM(unittest/person.age)} years"
        result = self.parser.eval(expression, self.city)
        self.assertEquals("%s years" % sum, result)


        # test sum with 1 item only
        expression = "{@SUM(unittest/person['name_first','person1'].age)} years"
        result = self.parser.eval(expression, self.city)
        self.assertEquals("%s years" % person1_age, result)

        # test sum with 1 item only using @GET
        expression = "{@SUM(@GET(unittest/person['name_first','person1'].age) + @GET(unittest/person['name_first','person1'].id))} years"
        result = self.parser.eval(expression, self.city)
        self.assertEquals("%s years" % (person1_age + self.persons[1].get_id()), result)

        # test average, with some formating
        format = "%2d"
        expression = "{@AVG(unittest/person.age),%s} years" % format
        result = self.parser.eval(expression, self.city)
        expected = "%s years" % format % avg
        self.assertEquals(expected, result)


        # test using TACTIC formatting
        format = "-$1,234.00"
        expression = "{1234,format='%s'}" % format
        result = self.parser.eval(expression)
        expected = "$1,234.00"
        self.assertEquals(expected, result)



        # test explicit function
        expression = "@FORMAT(1234, '-$1,234.00')"
        result = self.parser.eval(expression)
        expected = ["$1,234.00"]
        self.assertEquals(expected, result)

        expression = "@FORMAT(0.355, '-12.95%')"
        result = self.parser.eval(expression, single=True)
        expected = "35.50%"
        self.assertEquals(expected, result)

        expression = "@FORMAT(@GET(.birth_date), '31/12/1999')"
        result = self.parser.eval(expression, self.persons[0])
        expected = ["25/12/2000"]
        self.assertEquals(expected, result)

        # default 24fps
        expression = "@FORMAT('5000', 'MM:SS:FF')"
        result = self.parser.eval(expression, single=True)
        expected = "03:28:08"
        self.assertEquals(expected, result)

        expression = "@FORMAT('5000', 'MM:SS:FF', '25')"
        result = self.parser.eval(expression, single=True)
        expected = "03:20:00"
        self.assertEquals(expected, result)


        # TODO!!!
        # test with complex formatting
        #format = "%2d"
        #expression = "years old: ({@AVG(unittest/person.age),%s}) !!" % format
        #result = self.parser.eval(expression, sobject=self.city)
        #expected = "years old: (%s) !!" % format % avg
        #self.assertEquals(expected, result)

        """
        Project.set_project('sample3d')        
        self.submission = SearchType.create("prod/submission")
        self.submission.set_value('artist','admin')
        self.submission.commit()

        self.bin = SearchType.create("prod/bin")
        self.bin.set_value('code', 'Test Bin')
        self.bin.commit()

        self.submission_in_bin = SearchType.create("prod/submission_in_bin")
        self.submission_in_bin.set_value('bin_id', self.bin.get_id())
        self.submission_in_bin.set_value('submission_id', self.submission.get_id())
        self.submission_in_bin.commit()

        expression = '{@GET(prod/submission_in_bin.prod/bin.code)}'
        #expression = '{@GET(prod/submission.artist)}'
        result = self.parser.eval(expression, sobjects= self.submission)
        expected = 'Test Bin'
        self.assertEquals(expected, result)
        """


        Project.set_project('unittest')        

        # The parrser operates on sobjects at a certain level.  The sobject
        # argument is the base level of these expression.  All elements in the
        # expression are relative to this sobject (or list of sobjects)

        # The expression will look at the serach type in the first argument
        # of the expression an

        # operate on a list of objects.  Now because the expression is at
        # a base level
        expression = "{@COUNT(unittest/person)} people"
        result = self.parser.eval(expression, self.persons)
        self.assertEquals("%s people" % count, result)


        # test average, with some formating
        format = "%4f"
        expression = "{@AVG(unittest/person.age),%s} years" % format
        result = self.parser.eval(expression, self.persons)
        expected = "%s years" % format % avg
        self.assertEquals(expected, result)


        # @AVG of 1 sobject should be the same as @GET
        expression = "@AVG(unittest/person['name_first','person2'].age)"
        result = self.parser.eval(expression)
        expected = self.parser.eval("@GET(unittest/person['name_first','person2'].age)", single=True)
        self.assertEquals(expected, result)

        expression = "@AVG(unittest/person['name_first','EQ','pers'].age)"
        result = self.parser.eval(expression)
        expected = avg
        self.assertEquals(expected, result)

        # there are only 2 tasks , 1 with priority 5
        expression = "@AVG(unittest/city.sthpw/task.priority)"
        result = self.parser.eval(expression, self.persons[0])
        expected = 2.5
        self.assertEquals(expected, result)


        # Avg of city and country task priority
        expression = "@AVG(.priority)"
        result = self.parser.eval(expression, [self.city_task, self.country_task])
        expected = 4.5
        self.assertEquals(expected, result)

        # FIXME: these do not work
        # try a compound
        #expression = "@SUM( @GET(unittest/person.age) )"
        #result = self.parser.eval(expression, self.persons)
        #self.assertEquals(sum, result)

        # try a compound
        #expression = "@AVG( @GET(unittest/person.age) )"
        #result = self.parser.eval(expression, self.persons)
        #self.assertEquals(avg, result)





    def _test_args(self):
        expression = "@SEARCH(unittest/person.sthpw/task)"
        search = self.parser.eval(expression)
        self.assertEquals(isinstance(search, Search), True)

        expected = '''SELECT "sthpw"."public"."task".* FROM "sthpw"."public"."task" WHERE "task"."search_type" = 'unittest/person?project=unittest' AND "task"."search_code" in ('''

        self.assertEquals(search.get_statement().startswith(expected), True)
        expression = "@SEARCH(unittest/person.unittest/person)"
        search = self.parser.eval(expression)
        self.assertEquals(isinstance(search, Search), True)
        expected = 'SELECT "unittest"."public"."person".* FROM "unittest"."public"."person"'
        self.assertEquals(search.get_statement(), expected)

        expression = "@SEARCH(sthpw/login['login', @GET(sthpw/login['login','ben'].login)])"
        result = self.parser.eval(expression, single=True)

        self.assertEquals(True, isinstance(result,Search))
        sobject = result.get_sobject()
        self.assertEquals('ben', sobject.get_value('login'))

        expression = "@SEARCH(login.sthpw/task['assigned', @GET(sthpw/login['login','admin'].login)])"
        result = self.parser.eval(expression, single=True)
        self.assertEquals(True, isinstance(result,Search))
        sobject = result.get_sobject()
        self.assertEquals('admin', sobject.get_value('assigned'))

        expression = "@SEARCH(login.sthpw/task['assigned', @GET(sthpw/login['login','admin'].login)].sthpw/login)"
        result = self.parser.eval(expression, single=True)
        self.assertEquals(True, isinstance(result,Search))
        sobject = result.get_sobject()
        self.assertEquals('admin', sobject.get_value('login'))

        #find a task assigned to me
        expression = "@SEARCH(login.sthpw/task['project_code','unittest'])"
        result = self.parser.eval(expression, single=True)
        self.assertEquals(True, isinstance(result,Search))
        sobjects = result.get_sobjects()
        project_codes = SObject.get_values(sobjects,'project_code')

        for project_code in project_codes:
            self.assertEquals('unittest', project_code)

        expression = "@SOBJECT(sthpw/login['login', @GET(sthpw/login['login','ben'].login)])"
        result = self.parser.eval(expression, single=True)
        self.assertEquals('ben', result.get_value('login'))

        expression = "@SOBJECT(unittest/person['name_first', @GET(unittest/person['metadata', $PROJECT].name_first)])"
        result = self.parser.eval(expression)
        self.assertEquals(3, len(result))

        # test get_plain_related_types() method used by FastTableLayoutWdg and TableLayoutWdg
        expression ="@SOBJECT(unittest/person['client_name', @GET(sthpw/login['login',$LOGIN].client_name)])"
        related = self.parser.get_plain_related_types(expression)
        self.assertEquals(['unittest/person'], related)

        expression ="@SOBJECT(unittest/country.unittest/city.unittest/person['client_name', @GET(sthpw/login['login',$LOGIN].client_name)])"
        related = self.parser.get_plain_related_types(expression)
        self.assertEquals(['unittest/country','unittest/city','unittest/person'], related)

        expression ="@UNIQUE(@SOBJECT(unittest/country.unittest/city.unittest/person['client_name', @GET(sthpw/login['login',$LOGIN].client_name)]))"
        related = self.parser.get_plain_related_types(expression)
        self.assertEquals(['unittest/country','unittest/city','unittest/person'], related)

        expression ="@UNIQUE(@SOBJECT(unittest/city.unittest/person))"
        related = self.parser.get_plain_related_types(expression)
        self.assertEquals(['unittest/city','unittest/person'], related)

        expression ="@SOBJECT(unittest/city.unittest/person['name','ben'])"
        related = self.parser.get_plain_related_types(expression)
        self.assertEquals(['unittest/city','unittest/person'], related)

        expression ="@SOBJECT(unittest/city.unittest/person['name is NULL'])"

        try:
            related = self.parser.eval(expression)
        except SearchException, e:
            self.assertEquals(str(e).startswith('Single argument filter is no longer supported.'), True)
            

        expression ='''@SOBJECT(unittest/city.unittest/person["name ='ben'"])'''
        try:
            related = self.parser.eval(expression)
        except SearchException, e:
            self.assertEquals(str(e).startswith('Single argument filter is no longer supported.'), True)
    

        # test for missing ] bracket Syntax Error
        try:
            expression = "@SOBJECT(sthpw/login['login', @GET(sthpw/login['login','ben'.login)])"
        except SyntaxError, e:
            self.assertEquals(True, 'Incorrect syntax: square brackets for the filter' in e.__str__())

        # test for outermost missing ] bracket Syntax Error
        try:
            expression = "@SOBJECT(sthpw/login['login', @GET(sthpw/login['login','ben'].login))"
        except SyntaxError, e:
            self.assertEquals(True, 'Incorrect syntax found' in e.__str__())


        expression = "@GET(sthpw/task['process', @GET(.process)].process)"
        result = self.parser.eval(expression, sobjects=self.city_task)
        self.assertEquals(['los_angeles'], result)
        expression = "@GET(sthpw/task['process', @GET(.process)].context)"
        result = self.parser.eval(expression, sobjects=self.city_task)
        self.assertEquals(['City'], result)

        # try comparing white spaces
        expression = "@GET(.description) == 'City Task 1'"
        result = self.parser.eval(expression, sobjects=self.city_task)
        self.assertEquals(True, result)

       

        # try using @GET in the column name 
        self.city_task.set_value('description','process')
        expression = "@GET(sthpw/task[@GET(.description), @GET(.process)].process)"
        result = self.parser.eval(expression, sobjects=self.city_task)
        self.assertEquals(['los_angeles'], result)

        self.city_task.set_value('description','priority')
        expression = "@GET(sthpw/task[@GET(.description), '5'].priority)"
        result = self.parser.eval(expression, sobjects=self.city_task2)

        # 3.7 returns 0 for None integer
        self.assertEquals([0], result)

        self.city_task.set_value('description','priority')
        expression = "@GET(sthpw/task[@GET(.description), '5'].priority)"
        result = self.parser.eval(expression, sobjects=self.city_task)
        self.assertEquals([5], result)



        # los_angeles is the code for task process
        expression = "@SOBJECT(sthpw/task['process', @GET(.code)])"
        result = self.parser.eval(expression, sobjects=self.city)
        self.assertEquals(self.city_task.get_id(), result[0].get_id())

        # los_angeles is the code for task process
        expression = "@SOBJECT(sthpw/task['process', @GET(.code)]['description','City Task 1'])"
        result = self.parser.eval(expression, sobjects=self.city)
        self.assertEquals(self.city_task.get_id(), result[0].get_id())

        # los_angeles is the code for task process, description is CIty Task 1, so return nothing
        expression = "@SOBJECT(sthpw/task['process', @GET(.code)]['description','City Task 0'])"
        result = self.parser.eval(expression, sobjects=[self.city])
        self.assertEquals([], result)

        # los_angeles is the code for task process, should return  [] with a . in the description
        expression = "@SOBJECT(sthpw/task['process', @GET(.code)]['description','City Task.1'])"
        result = self.parser.eval(expression, sobjects=[self.city])
        self.assertEquals([], result)

        # los_angeles is the code for task process, and LA is the task status
        expression = "@SOBJECT(unittest/city['code', @GET(.process)]['name', @GET(.status)])"
        result = self.parser.eval(expression, sobjects=self.city_task)
        self.assertEquals('los_angeles', result[0].get_value('code'))


    def _test_composite(self):
        expression = "@JOIN(@GET(unittest/person['name_first', 'EQ','person'].name_first), '#')"
        result = self.parser.eval(expression)
        self.assertEquals('person0#person1#person2#person3#person4#person5#person6#person7', result)


        expression = "@JOIN(@INTERSECT(@GET(unittest/person['name_first', 'EQ','person'].name_first), @GET(unittest/person['age', 'is not','NULL'].name_first)) , '..')"
        result = self.parser.eval(expression)
        persons = result.split('..')
        self.assertEquals(True, 'person4' not in result)
        person_list = ['person1','person2','person3','person5','person6','person7','person0']
        self.assertEquals(set(person_list).difference(persons), set([]))


        expression = "@JOIN(@INTERSECT(@GET(unittest/person['name_first', 'EQ','person'].name_first), @GET(unittest/person['age', 'is not','NULL'].name_first), @GET(unittest/person['name_first','person3'].name_first)) , '..')"
        result = self.parser.eval(expression)
        # intersect to only 1 result back
        self.assertEquals(result, 'person3')


        # try having multiple {}
        expression = "{@COUNT(@SOBJECT(unittest/person['age', 'is','NULL']))} out of {@COUNT(@SOBJECT(unittest/person['name_first', 'EQ','person']))} peeps"
        result = self.parser.eval(expression)
        self.assertEquals(result, '1 out of 8 peeps')


    def _test_related_sobject(self):
        expression = "@GET(sthpw/task.process)"
        # list = True
        result = self.parser.eval(expression, [self.country])
        result = sorted(result)
        self.assertEquals(result, ['p1','p2','p3'])
        
        # task for city2 is None
        expression = "@GET(sthpw/task.id)"
        result = self.parser.eval(expression, [self.city2])
        self.assertEquals(result, [])

        # task for city2 is None
        expression = "@SOBJECT(sthpw/task)"
        result = self.parser.eval(expression, [self.city2])
        self.assertEquals(result, [])

        # task for city2 is None even in dictionary return
        expression = "@SOBJECT(sthpw/task)"
        result = self.parser.eval(expression, [self.city2], dictionary=True)
        self.assertEquals(result, {self.city2.get_search_key(): []})

        expression = "@COUNT(sthpw/task)"
        result = self.parser.eval(expression, [self.country])
        self.assertEquals(result, 3)

        expression = "@GET(sthpw/task.id)"
        # this is done for next test
        result = self.parser.eval(expression, [self.country])

        # just use the first id to test number mode works. Limited to integer though
        expression = "@COUNT(sthpw/task['id', %s])" %result[0]
        result = self.parser.eval(expression, [self.country])
        self.assertEquals(result, 1)

        # just a bogus count to test the syntax
        self.country.set_value('process', 'p1')
        expression = "@COUNT(sthpw/task['process', @GET(.process)]['id','999'])"
        result = self.parser.eval(expression, [self.country])
        self.assertEquals(result, 0)

        # just setting a process value to the task temporarily for this variable substituition test
        self.country.set_value('process', 'p1')
        expression = "@COUNT(sthpw/task['process', @GET(.process)])"
        result = self.parser.eval(expression, [self.country])
        self.assertEquals(result, 1)

        # los_angeles and los_angeles2 task for self.city
        expression = "@COUNT(sthpw/task['process', 'EQ', @GET(.code)]['context','City'])"
        result = self.parser.eval(expression, [self.city])
        self.assertEquals(result, 2)

        # just a bogus count to test the syntax
        expression = "@COUNT(sthpw/task['code', @GET(unittest/city['code','los_angeles'].code) ])"
        result = self.parser.eval(expression, [self.country])
        self.assertEquals(result, 0)
        
        # do a real city task count without input sobject , which is 1
        expression = "@COUNT(sthpw/task['process', @GET(unittest/city['code','los_angeles'].code) ])"
        result = self.parser.eval(expression)
        self.assertEquals(result, 1)

        # do a real city task count with input sobject , which is 2
        expression = "@COUNT(sthpw/task['process', 'EQ', @GET(.code) ])"
        result = self.parser.eval(expression, [self.city])
        self.assertEquals(result, 2)

        # do a real city task count with input sobject , which is 2
        expression = "@COUNT(sthpw/task['process', 'EQ', @GET(.code) ])"
        result = self.parser.eval(expression, [self.city])
        self.assertEquals(result, 2)

        # do a real city task count with input sobject , which is 2
        expression = "@COUNT(sthpw/task['process', 'EQ', @GET(.code) ]) >= 1"
        result = self.parser.eval(expression, [self.city])
        self.assertEquals(result, True)

        # do a person count with input sobject , which is 8
        expression = "@COUNT(unittest/person['city_code', @GET(.code)])"
        result = self.parser.eval(expression, [self.city])
        self.assertEquals(result, 8)

        # do a person count with full search type input sobject , which is also 8
        expression = "@COUNT(unittest/person?project=unittest['city_code', @GET(.code)])"
        result = self.parser.eval(expression, [self.city])
        self.assertEquals(result, 8)

        # do a real city task count with input sobject , which is 2, indirectly thru couuntry
        expression = "@COUNT(unittest/city.sthpw/task['process', 'EQ', @GET(unittest/city['code','los_angeles'].code) ])"
        result = self.parser.eval(expression, [self.country])
        self.assertEquals(result, 2)

        # do a real city task count with input sobject , which is 1, indirectly thru couuntry, @GET returns a list here without
        # filtering down to los_angeles. 
        expression = "@COUNT(unittest/city.sthpw/task['process', @GET(unittest/city.code) ])"
        result = self.parser.eval(expression, [self.country])
        self.assertEquals(result, 1)

        city_task_id = self.city_task.get_id()
        expression = "@GET(unittest/city['code','los_angeles'].sthpw/task['context','City']['priority','5'].id)"
        result = self.parser.eval(expression, [self.country], single=True)
        self.assertEquals(result, city_task_id)
    

        # test simple case statement
        expression = '''@CASE( @GET(sthpw/task.status) == 'Assignment', 'red')'''
        result = self.parser.eval(expression, self.country)
        self.assertEquals("red", result)

        expression = '''@UPDATE( @SOBJECT(sthpw/task), 'status', 'In Progress' )'''
        self.parser.eval(expression, self.country)
        expression = '''@GET(sthpw/task.status)'''
        result = self.parser.eval(expression, self.country)
        self.assertEquals(result[0], "In Progress")

        expression = '''@CASE(
          @( @GET(sthpw/task.status) == 'Assignment' ), 'red',
          @( @GET(sthpw/task.status) == 'In Progress' ), 'blue',
          @( @GET(sthpw/task.status) == 'Review' ), 'blue'
        )'''
        result = self.parser.eval(expression, self.country)
        #print 'result: ', result

        


        self.country.set_value("version", -1)

       

        expression = "@GET(.version) == -1"
        result = self.parser.eval(expression, self.country)
        self.assertEquals(True, result)

        expression = "@GET(.version) == '1'"
        result = self.parser.eval(expression, self.country)
        self.assertEquals(False, result)

      
        expression = "-1 == @GET(.version)"
        result = self.parser.eval(expression, self.country)
        self.assertEquals(True, result)

        # in can only be used in string comparision, list test is not supported yet
        expression = "US in @GET(.code)"
        result = self.parser.eval(expression, self.country)
        self.assertEquals(True, result)

        country_id = self.country.get_id()
        expression = "@GET(.version) - @GET(.id)"
        result = self.parser.eval(expression, self.country)
        self.assertEquals(-1 - country_id, result)

        
        # FIXME: this does not parse right ...
        #expression = "'-1' == -1"
        #result = self.parser.eval(expression, self.country)
        #self.assertEquals(False, result)


        self.country.set_value("version", -1)
        expression = '''@CASE( 
          @GET(.version) == -1, 'LATEST',
          @GET(.version) == 0, 'CURRENT',
          @GET(.version) > 0, 'v'+@STRING(@GET(.version))
        )'''
        result = self.parser.eval(expression, self.country)
        self.assertEquals('LATEST', result)

        self.country.set_value("version", 0)
        result = self.parser.eval(expression, self.country)
        self.assertEquals('CURRENT', result)

        """
        expression = '''{@CASE( 
          @GET(.version) == -1, 'LATEST'),
          @GET(.version) == 0, 'CURRENT',
          @GET(.version) > 0, 'v'+@STRING(@GET(.version))
        )}'''
        result = self.parser.eval(expression, self.country)
        self.assertEquals('LATEST', result)
        """
       
        self.country.set_value("version", -1)
        expression = '''{@CASE( 
          @GET(.version) == -1, 'LATEST',
          @GET(.version) == 0, 'CURRENT',
          @GET(.version) > 0, 'v'+@STRING(@GET(.version))
        )}'''
        result = self.parser.eval(expression, self.country)
        self.assertEquals('LATEST', result)

        self.country.set_value('name','ny')
        color_expression =  '''{@CASE(
                                    @GET(.name) == 'extended', '#469eeb', 
                                    @GET(.name) == 'expired', '#de4545', 
                                    @GET(.name) == 'pending', '#f2f540', 
                                    @GET(.name) == 'ny', '#3fb', 
                                    @GET(.name) == 'bumped', '#33F33F')}'''
        
        result = self.parser.eval(color_expression, self.country)
        self.assertEquals('#3fb', result)

        # FIXME: this does not work yet.  @STRING does not evaluate
        # expressions as an argument.
        #self.country.set_value("version", 3)
        #result = self.parser.eval(expression, self.country)
        #self.assertEquals('v003', result)



        # test for parent sobject
        tasks = self.parser.eval("@SOBJECT(sthpw/task)", [self.country])
        expression = "@GET(parent.code)"
        for task in tasks:
            code = self.parser.eval(expression, task, single=True)
            self.assertEquals("USA", code)


        expression = "@GET(parent.code)"
        code = self.parser.eval(expression, self.city, single=True)
        self.assertEquals("USA", code)




        # test some sample 3d submission relation
        '''
        Project.set_project('sample3d')
        self.submission = SearchType.create("prod/submission")
        # add a parent for this submission maybe
        self.submission.set_value('artist','admin')
        self.submission.commit()

        self.bin = SearchType.create("prod/bin")
        self.bin.set_value('code', 'Test Bin')
        self.bin.commit()

        self.submission_in_bin = SearchType.create("prod/submission_in_bin")
        self.submission_in_bin.set_value('bin_id', self.bin.get_id())
        self.submission_in_bin.set_value('submission_id', self.submission.get_id())
        self.submission_in_bin.commit()

        expression = '{$PROJECT}/Submit/{@GET(prod/submission_in_bin.prod/bin.code)}'
        
        result = self.parser.eval(expression, sobjects = [self.submission])
        expected = 'sample3d/Submit/Test Bin'
        self.assertEquals(expected, result)


        Project.set_project('unittest')
        '''



    def _test_input_search(self):

        # should find all of them
        search = Search("unittest/person")
        expr = "@SOBJECT(unittest/person)"
        result = Search.eval(expr, search=search)
        self.assertEquals(8, len(result))


        search = Search("unittest/person")
        search.add_limit(5)
        expr = "@SOBJECT(unittest/person)"
        result = Search.eval(expr, search=search)
        self.assertEquals(5, len(result))



        search = Search("unittest/person")
        expr = "@SOBJECT(unittest/person['age','<','30'])"
        result = Search.eval(expr, search=search)

        search = Search("unittest/person")
        search.add_filter("age", 30, op="<")
        result2 = search.get_sobjects()

        self.assertEquals(len(result), len(result2))


        # This is not supported yet
        search = Search("unittest/person")
        expr = "@SOBJECT(unittest/city)"
        try:
            results = Search.eval(expr, search=search)
        except:
            pass
        #self.assertEquals("unitest/city", results[0].get_base_search_type())






    def _test_single(self):
        
        expression = "@GET(unittest/person['name_first','person2'].age)"
        result = self.parser.eval(expression)
        expected = self.parser.eval("@GET(unittest/person['name_first','person2'].age)", single=True)
        age = expected 

        self.assertEquals(expected, result[0])


        sk = self.parser.eval("@GET(unittest/person['name_first','person2'].__search_key__)", single=True)
        person = SearchKey.get_by_search_key(sk)
        person.set_value('age', 0)
        person.commit()
        ExpressionParser.clear_cache()
        expression = "@GET(unittest/person['name_first','person2'].age)"
        expression2 = "@GET(unittest/person['name_first','person2'].__search_key__)"
        result2 = self.parser.eval(expression2)
        result = self.parser.eval(expression)
        expected = self.parser.eval("@GET(unittest/person['name_first','person2'].age)", single=True)
        self.assertEquals(expected, result[0])
        self.assertEquals(expected, 0)

        # set it back 
        person.set_value('age', age)
        person.commit()

        expected = self.parser.eval("@GET(unittest/person['name_first','person200'].age)", single=True)
        self.assertEquals(expected, None)

        sobj = self.parser.eval("@SOBJECT(unittest/person['name_first','person200'])", single=True)
        self.assertEquals(None, sobj)

        sobj = self.parser.eval("@SOBJECT(unittest/person['name_first','person2'])", single=True)
        from pyasm.search import SObject
        self.assertEquals(True, isinstance(sobj, SObject))

       






    def _test_string(self):
        expression = """@STRING(cow|horse|dog)"""
        result = self.parser.eval(expression)
        expected = "cow|horse|dog"
        self.assertEquals(expected, result)


        expression = """@STRING( '(cow|horse|dog)' )"""
        result = self.parser.eval(expression)
        expected = "(cow|horse|dog)"
        self.assertEquals(expected, result)

        expression = """@STRING( (cow|horse|dog) )"""
        result = self.parser.eval(expression)
        expected = "(cow|horse|dog)"
        self.assertEquals(expected, result)


        expression = """'(cow|horse|dog)'"""
        result = self.parser.eval(expression)
        expected = "(cow|horse|dog)"
        self.assertEquals(expected, result)

        '''
        expression = """5"""
        result = self.parser.eval(expression)
        expected = "5"
        self.assertEquals(expected, result)
        '''



    def _test_op(self):


        sum = 0
        for person in self.persons:
            value = person.get_value('age')
            if value:
                sum += value
        avg = float(sum) / len(self.persons)
        count = len(self.persons)

        # some rows have expression on the row
        person = self.persons[0]
        age = person.get_value("age")

        # simple expression
        expression = "@GET(unittest/person.age)"
        result = self.parser.eval(expression, person)
        self.assertEquals([age], result)


        # add white space expression
        expression = " @GET( unittest/person.age )"
        result = self.parser.eval(expression, person)
        self.assertEquals([age], result)

        
        
        expression = "@GET(.age)"
        result = Search.eval(expression, person)
        
        # this kind of evaluation auto convert a list like @GET(.age) into a single item
        expression = "@GET(.age) == %s"%result[0]
        result = Search.eval(expression, person)
        self.assertEquals(True, result)

        expression = "@GET(.picture)"
        result = Search.eval(expression, person)
        expression = "@GET(.picture) == ''"
        result = Search.eval(expression, person)
        self.assertEquals(True, result)

        expression = "@GET(.name_first) != ''"
        result = Search.eval(expression, person)
        self.assertEquals(True, result)

        
        # simple expressions

        # add
        expression = "@GET(unittest/person.age) + @GET(unittest/person.age)"
        result = self.parser.eval(expression, person)
        self.assertEquals(2*age, result)

        # subtract
        expression = "@GET(unittest/person.age) - @GET(unittest/person.age)"
        result = self.parser.eval(expression, person)
        self.assertEquals(0, result)


        # multiply
        expression = "@GET(unittest/person.age) * 12"
        result = self.parser.eval(expression, person)
        self.assertEquals(age*12, result)


        # divide
        expression = "@GET(unittest/person.age) / 12"
        result = self.parser.eval(expression, person)
        self.assertEquals(float(age)/12, result)

        # divide by zero
        expression = "0 / 0"
        result = self.parser.eval(expression)
        expected = None
        self.assertEquals(expected, result)

        expression = "10 / @GET(unittest/person.age)"
        result = self.parser.eval(expression, self.persons[4])
        self.assertEquals(None, result)

        # divide by zero
        expression = "(10/0) + 1"
        result = self.parser.eval(expression)
        expected = None
        self.assertEquals(expected, result)



        # simple math
        expression = "12 * 12"
        result = self.parser.eval(expression, person)
        self.assertEquals(144, result)

        # simple math
        expression = "18 / 3 + 1"
        result = self.parser.eval(expression, person)
        self.assertEquals(7, result)


        # variations with spaces
        expression = " 12*  @GET(unittest/person.age)* 12"
        result = self.parser.eval(expression, person)
        self.assertEquals(age*12*12, result)


        # variations with spaces
        expression = "  @GET(unittest/person.age) * 12"
        result = self.parser.eval(expression, person)
        self.assertEquals(age*12, result)

        # variations with spaces
        expression = "@GET(  unittest/person.age)* 12  "
        result = self.parser.eval(expression, person)
        self.assertEquals(age*12, result)


        # Test comparisons
        #

        # count the total number of people
        expression = "@COUNT(unittest/person) == 8"
        result = self.parser.eval(expression)
        self.assertEquals(True, result)

        # count the number of people with person2
        expression = "@COUNT(unittest/person['name_first','person2']) == 1"
        result = self.parser.eval(expression)
        self.assertEquals(True, result)

        # test average
        expression = "@AVG(unittest/person.age) > 0"
        result = self.parser.eval(expression)
        self.assertEquals(True, result)

        # count the number of people
        expression = "@GET(.age) == %s" % age
        result = self.parser.eval(expression, person)
        self.assertEquals(True, result)


        # count the number of people
        expression = "(@GET(.age) == %s and @GET(.age) == 0" % age
        result = self.parser.eval(expression, person)
        self.assertEquals(False, result)




        # test more complex comparisons
        expression = "@GET(unittest/person.name_first) == 'person1' or @GET(unittest/person.name_first) == 'person4'"
        result = self.parser.eval(expression, [self.persons[1],self.persons[4],self.persons[6]])
        self.assertEquals([True,True,False], result)

        expression = """@GET(unittest/person.name_first) in '["person1","person4"]'"""
        result = self.parser.eval(expression, [self.persons[1],self.persons[4],self.persons[6]])
        self.assertEquals([True,True,False], result)

        result = self.parser.eval("@GET(.name_first)==person6", sobjects=[self.persons[6]])
        self.assertEquals(True, result)


        # test max and min
        result = self.parser.eval("@GET(unittest/person.age)")
        #print "result: ", result
        
        result = self.parser.eval("@MAX(unittest/person.age)")
        #print "result: ", result

        result = self.parser.eval("@MIN(unittest/person.age)")
        #print "result: ", result

        result = self.parser.eval("abc")
        result = self.parser.eval("@GET(login.last_name)")
        
        # test the concept of containing using "in"
        expression = "'pers' in @GET(unittest/person.name_first)"
        result = self.parser.eval(expression, [self.persons[1]])
        self.assertEquals(True, result)






    def _test_syntax_error(self):
        person = self.persons[0]
        age = person.get_value("age")

        # syntax errors
        try:
            expression = "@GET(  unittest/person.age)* 12 12 "
            result = self.parser.eval(expression, person)
        except SyntaxError, e:
            #print str(e)
            pass
        else:
            self.fail("Expression [%s] did not produce a syntax error" % expression)



    def _test_filter(self):
        city = self.city
        person = self.persons[2]
        age = person.get_value("age")

        person2 = self.persons[3]
        age2 = person2.get_value("age")


        # try a simple filter
        expr = "@GET(unittest/person['name_first','person2'].age)"
        result = self.parser.eval(expr, city)
        self.assertEquals(age, result[0])


        # try a simple filter with bad characters (should not error out
        expr = "@GET(unittest/person['name_first','@!,$#%]['].age)"
        result = self.parser.eval(expr, city)

        # try other quotes
        expr = "@GET(unittest/person['name_first',\"person2\"].age)"
        result = self.parser.eval(expr, city)
        self.assertEquals([age], result)



        # try a compound filter with or
        expr = "@GET(unittest/person['name_first','person2']['name_first','person3']['or'].age)"
        result = self.parser.eval(expr, city)
        result = result[0]
        self.assertTrue((result == age or result == age2))



        # much more complex with two filters and doubling back
        expr = "@GET(unittest/person['name_first','person2'].unittest/city['code','los_angeles'].code)"
        result = self.parser.eval(expr, city, single=True)
        self.assertEquals("los_angeles", result)

        # much more complex formatted with two filters and doubling back
        #expr = '''@GET(
        #    unittest/person['name_first','person2'].unittest/city['code','los_angeles'].code
        #          )'''
        #result = self.parser.eval(expr, city)
        #self.assertEquals("los_angeles", result)


        # test a filter with period in it.  No result should come back
        expr = "@SOBJECT(unittest/person['name_first','per.son2'])"
        result = self.parser.eval(expr, city)
        self.assertEquals([], result)

        # test a filter with period in it.  No result should come back
        expr = "@COUNT(unittest/person['name_first','per.son2'])"
        result = self.parser.eval(expr, city)
        self.assertEquals(0, result)

        # test a filter with period in it.  No result should come back
        expr = "@SUM(unittest/person['name_first','per.son2'].unittest/city)"
        result = self.parser.eval(expr, city)
        self.assertEquals(0, result)



        # test a filter with period in it.  No result should come back
        expr = "@GET(unittest/person['name_first','per.son2'].age)"
        result = self.parser.eval(expr, city)
        self.assertEquals([], result)




        # test order by
        expr = "@GET(unittest/person['@ORDER_BY','age'].age)"
        result = self.parser.eval(expr)
        last = 0
        for i, value in enumerate(result):
            # FIXME: shouldn't need this
            if value == 0:
                continue
            self.assertEquals(True, last <= value)
            last = value

        # test order by
        expr = "@GET(unittest/person['@LIMIT','2'].age)"
        result = self.parser.eval(expr)
        self.assertEquals(True, len(result)== 2)


        # test order by
        expr = "@GET(unittest/person['@LIMIT',3].age)"
        result = self.parser.eval(expr)
        self.assertEquals(True, len(result)== 3)

        expr = "@GET(unittest/person['@OFFSET',3].age)"
        result = self.parser.eval(expr)
        #self.assertEquals(True, len(result)== 3)



        expr = "@GET(unittest/person['timestamp','is before', '$TOMORROW'].id)"
        result = self.parser.eval(expr)
        self.assertEquals(True, len(result)== 8)

        expr = "@GET(unittest/person['timestamp','is after', '$YESTERDAY'].id)"
        result = self.parser.eval(expr)
        self.assertEquals(True, len(result)== 8)






    def _test_regex(self):
        person = self.persons[2]
        person2 = self.persons[3]
        city = self.city
        age = person.get_value("age")

        # get last three letters
        expr = "{@GET(unittest/person.name_first),|(\w{3})$|}"
        result = self.parser.eval(expr, person)
        self.assertEquals("on2", result)


        # get first three letters
        expr = "{@GET(unittest/person.name_first),|^(\w{3})|}"
        result = self.parser.eval(expr, person)
        self.assertEquals("per", result)

        # get first three letters
        expr = "{@GET(unittest/person.name_first),|^p(\w{3})|}"
        result = self.parser.eval(expr, person)
        self.assertEquals("ers", result)

        vars = {
            'VALUE': 'foo foo',
            'SOBJECT_CODE': u'\u30EBSOME CHINESE CHAR'
            }

        #print "foo" , Search.eval("$VALUE == 'foo foo'", vars=vars)
        #print "fo2", Search.eval("'foo fo2' == $VALUE", vars=vars) 

        # ensure non-ascii characters work with eval and vars
        sobj_code = Search.eval("$SOBJECT_CODE", vars=vars) 
        self.assertEquals(sobj_code.endswith('SOME CHINESE CHAR'), True)

        

        # test regex comparisons
        vars = {'VALUE': 'foo Test'}
        expr = "$VALUE =~ '^foo'"
        result = Search.eval(expr, vars=vars)
        self.assertEquals(True, result)

        expr = "$VALUE !~ '^foo'"
        result = Search.eval(expr, vars=vars)
        self.assertEquals(False, result)

        expr = "@GET(unittest/person.name_first) == 'person2'"
        result = Search.eval(expr, person, vars=vars)
        self.assertEquals(True, result)


        expr = "@GET(unittest/person.name_first) == $VALUE"
        result = Search.eval(expr, person, vars=vars)
        self.assertEquals(False, result)

        expr = "@GET(unittest/person.name_first) =~ '^person'"
        result = Search.eval(expr, person, vars=vars)
        self.assertEquals([True], result)

        expr = "@GET(unittest/person.name_first) =~ '^person'"
        result = Search.eval(expr, [person], vars=vars)
        self.assertEquals([True], result)


        # try ends with
        expr = "@GET(unittest/person.name_first) =~ 'son2$'"
        result = Search.eval(expr, person, vars=vars)
        self.assertEquals([True], result)


        # try not matches and ends with
        expr = "@GET(unittest/person.name_first) !~ 'son2$'"
        result = Search.eval(expr, person, vars=vars)
        self.assertEquals([False], result)





        vars = {'VALUE': '^person'}
        expr = "@GET(unittest/person.name_first) =~ $VALUE"
        result = Search.eval(expr, [person,person2], vars=vars)
        self.assertEquals([True,True], result)

	# FIXME: comment out \n test for now
        """
        vars = {'VALUE': 'person\n bs'}
        expr = "@CASE($VALUE =~ '^per', 'Green')"
        result = Search.eval(expr,[person,person2], vars=vars)
        self.assertEquals('Green', result)
        """

        vars = {'VALUE': 'foo'}
        expr = "'cow' + $VALUE + 'cow'"
        result = Search.eval(expr, vars=vars)
        self.assertEquals("cowfoocow", result)

        expr = "'cowfoocow' = 'cow' + $VALUE + 'cow'"
        result = Search.eval(expr, vars=vars)
        self.assertEquals(True, result)

        # FIXME: not supported yet
        #expr = "'cowfoocow' =~ 'cow' + $VALUE + 'xx'"
        #result = Search.eval(expr, vars=vars)
        #self.assertEquals(False, result)





    def _test_var(self):

        login = Environment.get_login()
        login_name = login.get_value("login")
        first_name = login.get_value("first_name")

        person = self.persons[0]


        # replace $LOGIN variable
        result = self.parser.eval("$LOGIN" )
        self.assertEquals("admin", result)

        # replace {$LOGIN} with 
        result = self.parser.eval("{$LOGIN}" )
        self.assertEquals("admin", result)

        # replace $LOGIN variable
        result = self.parser.eval("'User:' + $LOGIN" )
        self.assertEquals("User:admin", result)

        # a more complex example
        # FIXME: does $LOGIN really need quotes?
        result = self.parser.eval("LOGIN: {$LOGIN} {@GET(sthpw/login['login',$LOGIN].first_name)}", vars={} )
        self.assertEquals("LOGIN: %s %s" % (login_name, first_name), result)

        # test the current project
        result = self.parser.eval("$PROJECT")
        self.assertEquals("unittest", result)


        # shorthand
        login = self.parser.eval("@GET(login.login)", single=True)
        self.assertEquals("admin", login)

        # FIXME: does not work with Unicode
        #login = self.parser.eval("{login.first_name + ':' + hello}")
        #self.assertEquals("%s:hello" % first_name, login)

        # get the login
        login = self.parser.eval("{ login.login }")
        self.assertEquals("admin", login)

        # get the login
        login = self.parser.eval("(login.login == 'admin')")
        self.assertEquals(True, login)

        # get the login
        #login = self.parser.eval("(login.login + x*3)")
        #self.assertEquals(True, login)


        # get the first 3 characters of the login
        login = self.parser.eval("{login.login,|(\w{3})|}")
        self.assertEquals("adm", login)

        #naming = self.parser.eval("v{version,%0.3d}")
        #print naming

        # test env
        login = Environment.get_login()
        env = {
            'sobject': person,
            'foofoo': login
        }
        results = self.parser.eval("@GET(sobject.age)", env_sobjects=env)
        self.assertEquals(person.get_value("age"), results[0])

        results = self.parser.eval("@GET(foofoo.login)", env_sobjects=env)
        self.assertEquals(login.get_value("login"), results[0])



        # test now
        result = self.parser.eval("@GET(date.now)", single=True)
        now = datetime.now()
        self.assertEquals(now.year, result.year)
        self.assertEquals(now.month, result.month)
        self.assertEquals(now.day, result.day)
        self.assertEquals(now.hour, result.hour)
        self.assertEquals(now.minute, result.minute)
        self.assertEquals(now.second, result.second)

        # test today
        result = self.parser.eval("@GET(date.today)", single=True)
       
        now = datetime.today()
        self.assertEquals(now.year, result.year)
        self.assertEquals(now.month, result.month)
        self.assertEquals(now.day, result.day)
        self.assertEquals(now.hour, result.hour)
        self.assertEquals(now.minute, result.minute)
        # FIXME: this test is problematic since if the server is busy, it
        # may be one or two seconds off
        try:
            self.assertEquals(now.second, result.second)
        except AssertionError:
            # let's give it a 2 second tolerance if it happens
            self.assertEquals(now.second - result.second < 2, True)


        result = self.parser.eval("@GET(date.now)", person, single=True)

        result = self.parser.eval("@STRING($NOW) > '2010-01-01'")
        self.assertEquals(True, result)

        result = self.parser.eval("$TODAY > '2010-01-01'")
        self.assertEquals(True, result)
      
        result = self.parser.eval("@CASE(@FORMAT({$TODAY}, 'DATE')  > '2010-01-01', 'green')")
        self.assertEquals('green', result)

        today = datetime.today()
        import time
        result = self.parser.eval("$NEXT_DAY")
        d  = today + relativedelta(days=1)
        
        expected_str = '%s-%s-%s 00:00:00' %(d.year,d.month,d.day)
        date = Date(db_date= expected_str)
        self.assertEquals(date.get_db_time(), result)

        result = self.parser.eval("$PREV_DAY")
        d  = today + relativedelta(days=-1)
        expected_str = '%s-%s-%s 00:00:00' %(d.year,d.month,d.day)
        date = Date(db_date= expected_str)
        self.assertEquals(date.get_db_time(), result)

        

        # FIXME: this doesnt work yet
        #result = self.parser.eval("'www $TODAY' > 'www'")
        #self.assertEquals(True, result)


        # FIXME: this returns a string ... should be a datetime object
        result = self.parser.eval("$NEXT_MONDAY")
       
        expected = today + relativedelta(weekday=calendar.MONDAY)
        expected = datetime(expected.year, expected.month, expected.day)
        self.assertEquals(str(expected), result)

        result = self.parser.eval("$PREV_MONDAY")
        today = datetime.today()
        expected = today + relativedelta(weeks=-1,weekday=calendar.MONDAY)
        expected = datetime(expected.year, expected.month, expected.day)
        self.assertEquals(str(expected), result)


	'''
        result = self.parser.eval("$PREV_MONTH")
        expected = today + relativedelta(months=-1)
        print "prev month ", result, str(expected)
        self.assertEquals(str(expected), result)
	'''
        # FIXME: this doesn't work yet!!  Need to stop using dates as
        # strings!!!
        #result = self.parser.eval("@GET(date.today) > '2010-01-01'")
        #self.assertEquals(expected, result)

        #result = self.parser.eval("$NEXT_MONDAY - @RELTIME(weekday=MO)")


        result = self.parser.eval("@COUNT(sthpw/snapshot['timestamp','<',$PREV_MONDAY])")
        self.assertEquals(True, result > 0)




        
    def _test_paragraph(self):
        # test some full text paragraph
        person = self.persons[0]
        name_first = person.get_value("name_first")
        age = person.get_value("age")




        # try a short sentence
        expr = '''My name is {@GET(.name_first)}!'''
        result = self.parser.eval(expr, person)
        expected = '''My name is %s!''' % name_first
        self.assertEquals(expected, result)


        # try a long expression with many replacements
        expr = '''This is a test of a long string.
        My name is "{@GET(.name_first)}" and I am {@GET(.age)}.
        I live in {@GET(unittest/city.code)} and I am here to stay
        '''
        result = self.parser.eval(expr, person)
        expected = '''This is a test of a long string.
        My name is "%s" and I am %s.
        I live in los_angeles and I am here to stay
        ''' % (name_first, age)
        self.assertEquals(expected, result)



        # try a sentence with no expressions, forcing string mode
        expr = '''My name is nobody'''
        result = self.parser.eval(expr, person, mode='string')
        expected = '''My name is nobody'''
        self.assertEquals(expected, result)

        # try a sentence with no expressions, forcing expression
        expr = '''12 * 12'''
        result = self.parser.eval(expr, person, mode='expression')
        self.assertEquals(144, result)


        # try a sentence forcing string mode
        expr = '''12 * 12'''
        result = self.parser.eval(expr, person, mode='string')
        self.assertEquals(expr, result)



        # try with empty brackets
        expr = '''My name is {}nobody'''
        result = self.parser.eval(expr, person)
        expected = '''My name is nobody'''
        self.assertEquals(expected, result)




    def _test_dates(self):
        person = self.persons[2]
        city = self.city
        age = person.get_value("age")

        parser = ExpressionParser()

        timestamp = person.get_value("timestamp")
        from dateutil import parser as date_parser
        timestamp = date_parser.parse(timestamp)

        # test formatting dates
        expression = "{@GET(unittest/person.timestamp), %Y}"
        result = parser.eval(expression, person)
        year = timestamp.strftime("%Y")
        self.assertEquals(year, result)
        
        expression = "{$PROJECT, |^(\w{4})|  }/{@GET(unittest/person.timestamp),%Y}"
        result = parser.eval(expression, person, mode='string')
        year = timestamp.strftime("%Y")
        self.assertEquals('unit/%s'%year, result)

        # first 3 and last 2
        expression = "{$PROJECT, |^(\w{3}).*(\w{2})$|  }/{@GET(unittest/person.timestamp),%Y}"
        result = parser.eval(expression, person, mode='string')
        year = timestamp.strftime("%Y")
        self.assertEquals('unist/%s'%year, result)

        # first 4 and last 2 with a trailing space
        expression = "{$PROJECT, |^(\w{4}).*(.{2})$|} /{@GET(unittest/person.timestamp),%Y}"
        result = parser.eval(expression, person, mode='string')
        year = timestamp.strftime("%Y")
        self.assertEquals('unitst /%s'%year, result)

        # test using | in the expression
        expression = "{$PROJECT, |(u|a|b|c)+|  }/{@GET(unittest/person.timestamp),%Y}"
        result = parser.eval(expression, person, mode='string')
        year = timestamp.strftime("%Y")
        self.assertEquals('u/%s'%year, result)

        # test using | in the expression with multiple groups
        expression = "{$PROJECT, |(u|a|b|c)+(a|n|b|c)+.*(t|3|b|c)+|  }/{@GET(unittest/person.timestamp),%Y}"
        result = parser.eval(expression, person, mode='string')
        year = timestamp.strftime("%Y")
        self.assertEquals('unt/%s'%year, result)

        # test formatting dates with @GET

        expression = "{@GET(.timestamp), %b-%m}/{@GET(unittest/person.name_first)}"

        result = parser.eval(expression, person, mode='string')
        label = timestamp.strftime("%b-%m")
        self.assertEquals('%s/person2'%label, result)
        #print "date: ", result




        from dateutil import parser as date_parser
        #today = parser.parse('yesterday')
        #print "today: ", today
        #hour_ago = date_parser.parse('1 hour, 3 minutes 12 seconds')

        expression = "@GET(unittest/person.timestamp) - @GET(unittest/person.timestamp)}"
        result = parser.eval(expression, person)
        #print "result: ", result, type(result)
        #print "timestamp: ", timestamp

    
     
    def _test_return_types(self):

        person = self.persons[0]
        name_first = person.get_value("name_first")
        age = person.get_value("age")

        person2 = self.persons[1]
        name_first2 = person2.get_value("name_first")
        age2 = person2.get_value("age")

        # NEW: single sobject with @GET should return an array now
        expr = "@GET(.name_first)"
        result = self.parser.eval(expr, person)
        self.assertEquals([name_first], result)

        # many sobjects with @GET should an array
        expr = "@GET(.name_first)"
        result = self.parser.eval(expr, self.persons[0:2])
        self.assertEquals([name_first,name_first2], result)

        # empty with @GET should return empty array
        expr = "@GET(.name_first)"
        result = self.parser.eval(expr, [])
        self.assertEquals([], result)

        # None with @GET should return empty array
        expr = "@GET(.name_first)"
        result = self.parser.eval(expr, None)
        self.assertEquals([], result)

        # Full search with @GET should return list
        expr = "@GET(unittest/person.name_first)"
        result = self.parser.eval(expr, None)
        self.assertEquals(types.ListType, type(result))

        # Full search with single result @GET should return list
        expr = "@GET(unittest/person['name_first','person0'].name_first)"
        result = self.parser.eval(expr, None)
        self.assertEquals(types.ListType, type(result))





        # SUM

        # single sobject with @SUM should return a value
        expr = "@SUM(.age)"
        result = self.parser.eval(expr, person)
        self.assertEquals(age, result)

        # many sobjects with @SUM should return a value
        expr = "@SUM(.age)"
        result = self.parser.eval(expr, self.persons[0:2])
        self.assertEquals(age+age2, result)

        # None with @SUM should return 0
        expr = "@SUM(.age)"
        result = self.parser.eval(expr, None)
        self.assertEquals(0, result)

        # Empty array with @SUM should return 0
        expr = "@SUM(.age)"
        result = self.parser.eval(expr, [])
        self.assertEquals(0, result)

        # Full search with @SUM should result in a value
        expr = "@SUM(unittest/person.age)"
        result = self.parser.eval(expr)
        self.assertEquals(types.IntType, type(result))

        # Single search with @SUM should result in a value
        expr = "@SUM(unittest/person['name_first','person0'].age)"
        result = self.parser.eval(expr)
        self.assertEquals(types.IntType, type(result))

        # Empty search with @SUM should result in 0
        expr = "@SUM(unittest/person['name_first','XXXX'].age)"
        result = self.parser.eval(expr)
        self.assertEquals(0, result)



        # SOBJECT

        # FIXME: syntax error?
        # Empty should return original sobject (for completion)
        #expr = "@SOBJECT()"
        #result = self.parser.eval(expr, person)
        #print result
        #self.assertEquals(0, result)


        # Full search should return a list
        expr = "@SOBJECT(unittest/person)"
        result = self.parser.eval(expr)
        self.assertEquals(types.ListType, type(result))

        # Empty search should return an empty list
        expr = "@SOBJECT(unittest/person['name_first','!!XXXX'])"
        result = self.parser.eval(expr)
        self.assertEquals([], result)

        expr = "@SOBJECT(unittest/person['name_first','in','person0|person2'])"
        result = self.parser.eval(expr)
        self.assertEquals(2, len(result))

        ''' 
        expr = "@SOBJECT(unittest/person['name_first','not in','person0|person2'])"
        result = self.parser.eval(expr)
        self.assertEquals(6, len(result))

        '''




    # Next Gen Expression parser

    def _test_new_parser(self):
        # test some full text paragraph
        person = self.persons[0]
        name_first = person.get_value("name_first")
        age = person.get_value("age")

        person1 = self.persons[1]
        age1 = person1.get_value("age")

        from expression import ExpressionParser

        try:
            expression = "@GET (unittest/person.age)"
            parser = ExpressionParser()
            parser.eval(expression)
        except SyntaxError, e:
            #print str(e)
            pass
        else:
            self.fail("Expression [%s] did not produce a syntax error" % expression)

        try:
            expression = "@ GET(unittest/person.age)"
            parser = ExpressionParser()
            parser.eval(expression)
        except SyntaxError, e:
            #print str(e)
            pass
        else:
            self.fail("Expression [%s] did not produce a syntax error" % expression)

        expression = "@SEARCH(unittest/person)"
        parser = ExpressionParser()
        result = parser.eval(expression, person, single=True)
        self.assertEquals(result.get_sobject().get_id(), person.get_id())

        # a correct statement
        expression = "@SOBJECT(unittest/person)"
        parser = ExpressionParser()
        result = parser.eval(expression, person, single=True)
        name_first = result.get_value("name_first")
        self.assertEquals("person0", name_first)


        # a few more syntax tests
        #
        # extra space at the beginning
        expression = "@SOBJECT( unittest/person)"
        parser = ExpressionParser()
        result = parser.eval(expression, person)
        name_first = result[0].get_value("name_first")
        self.assertEquals("person0", name_first)

        # extra space at the space at the end
        expression = "@SOBJECT(unittest/person  )"
        parser = ExpressionParser()
        result = parser.eval(expression, person)
        name_first = result[0].get_value("name_first")
        self.assertEquals("person0", name_first)


        # too many arguments
        try:
            expression = "@GET( unittest/person, .age  )"
            parser = ExpressionParser()
            result = parser.eval(expression, person)
        except SyntaxError, e:
            #print str(e)
            pass
        else:
            self.fail("Expression [%s] did not produce a syntax error" % expression)


        # bad space somewhere
        try:
            expression = "@SOBJECT( unitte st/person  )"
            parser = ExpressionParser()
            result = parser.eval(expression, person)
            name_first = result.get_value("name_first")
        # TODO: not sure about this
        except Exception:
            pass


        # string manipulations

        expression = "{@SOBJECT(unittest/city)} city"
        parser = ExpressionParser()
        result = parser.eval(expression, person)
        # it takes the .name attribute if available
        self.assertEquals("LA city", result)



        # larger string
        expression = "Hello, self name is {@GET(.name_first)}.  I live in {@GET(unittest/city.code)}.  I am going to be {@GET(.age)} this year."
        parser = ExpressionParser()
        result = parser.eval(expression, person)
        expected = 'Hello, self name is person0.  I live in los_angeles.  I am going to be %s this year.' % age
        self.assertEquals(expected, result)


        # test average
        expression = "@AVG(unittest/person.age)"
        avg = parser.eval(expression, self.city)

        format = "%2d"
        result = parser.eval(expression, self.city)
        expression = "It's been { @AVG(unittest/person.age), %s } years" % format
        result = parser.eval(expression, self.city)
        expected = "It's been %s years" % format % avg
        self.assertEquals(expected, result)


        # test regex
        result = parser.eval(expression, self.city)
        expression = "{@GET(unittest/person.name_first),|(\w{3})|} years"
        result = parser.eval(expression, self.city)
        self.assertEqual("per years", result)






        # get the parent
        expression = "@SOBJECT(unittest/city)"
        parser = ExpressionParser()
        result = parser.eval(expression, person)
        city_code = result[0].get_value("code")
        self.assertEquals("los_angeles", city_code)

        # get the age
        expression = "@GET(unittest/person.age)"
        parser = ExpressionParser()
        result = parser.eval(expression, person)
        self.assertEquals(age, result[0])

        # simple format
        expression = "@GET(.age)"
        parser = ExpressionParser()
        result = parser.eval(expression, person)
        self.assertEquals([age], result)


        # get sobjects with no starting sobject
        expression = "@COUNT(unittest/person)"
        parser = ExpressionParser()
        result = parser.eval(expression)
        self.assertEquals(len(self.persons) , result)



        # aggregate functions
        expression = "@SUM(.age)"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals(age + age1, result)

        # aggregate functions
        expression = "@COUNT(.age)"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals(2, result)

        # aggregate functions
        expression = "@AVG(.age)"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals(float(age + age1)/2, result)




        # multiple search_types
        expression = "@SOBJECT(unittest/city.unittest/country)"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals("USA", result[0].get_value("code"))
        # fast mode skips duplicated data
        self.assertEquals(1, len(result))
        #self.assertEquals("USA", result[1].get_value("code"))



        # FIXME: need to work on these!!!
        # reg
        expression = "@GET( .age)"
        parser = ExpressionParser()
        result = parser.eval(expression, person, dictionary=False)
        
        self.assertEquals([age], result)
        expression = "@SOBJECT(unittest/city)"
        parser = ExpressionParser()
        result = parser.eval(expression, person, dictionary=False)
        self.assertEquals('los_angeles', result[0].get('code'))
        
        
        expression = "@SOBJECT(unittest/city)"
        parser = ExpressionParser()
        result = parser.eval(expression, person, dictionary=True)
        result = result.get(person.get_search_key())
        self.assertEquals('los_angeles', result[0].get('code'))

        expression = "@SOBJECT(unittest/city.unittest/country)"
        parser = ExpressionParser()
        result = parser.eval(expression, person, dictionary=True)
        result = result.get(person.get_search_key())
        self.assertEquals('USA', result[0].get('code'))
        
        expression = "@GET( .age)"
        parser = ExpressionParser()
        result = parser.eval(expression, person, dictionary=True)
        result = result.get(person.get_search_key())
        self.assertEquals([age], result)

        another_person = Person.create('dave', 'v','italy','another person')
        
        # age is not set, but should result to zero
        expression = "@GET(.age) + @GET(.age)"
        parser = ExpressionParser()
        result = parser.eval(expression, another_person, dictionary=False)
        self.assertEquals(0, result)
        self.assertEquals(True, isinstance(result, int))

        expression = "@GET(.age) * @GET(.age)"
        parser = ExpressionParser()
        result = parser.eval(expression, another_person, dictionary=False)
        self.assertEquals(0, result)
        self.assertEquals(True, isinstance(result, int))

        # remove it so other calculations would only deal with 8 persons
        another_person.delete()


        # some addition
        expression = "@GET(.age) + @GET(.age)"
        parser = ExpressionParser()
        result = parser.eval(expression, person)
        self.assertEquals(age + age, result)

        # some addition with 2 sobjects
        expression = "@GET(.age) + @GET(.age)"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals([age + age, age1 + age1], result)


        # some more complex math with 2 sobjects
        expression = "@GET(.age) + (@GET(.age) * @GET(.age))"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals([age+(age*age), age1+(age1*age1)], result)

        # some more order of operations
        expression = "(@GET(.age) + @GET(.age)) * @GET(.age)"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals([(age+age)*age, (age1+age1)*age1], result)


        # put in some addition
        expression = "23.4 + @GET(.age)"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals([23.4 + age, 23.4 + age1], result)


        # put in some addition with no spacing
        expression = "23.4+@GET(.age)"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals([23.4 + age, 23.4 + age1], result)

        # put in some addition with no spacing
        expression = "@GET(.age) + 2.2"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals([2.2 + age, 2.2 + age1], result)

        # order of operations
        expression = "3.0 + @GET(.age) * 2.0"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals([3.0 + age * 2.0, 3.0 + age1 * 2.0], result)


        # try a bad element
        try:
            expression = "@GET(.age) + ls"
            parser = ExpressionParser()
            result = parser.eval(expression, [person, person1])
        except SyntaxError, e:
            #print str(e)
            pass
        #else:
        #    self.fail("Expression [%s] did not produce a syntax error" % expression)

        # try more garbage
        try:
            expression = "@GET(.age) ls"
            parser = ExpressionParser()
            result = parser.eval(expression, [person, person1])
        except SyntaxError, e:
            #print str(e)
            pass
        else:
            self.fail("Expression [%s] did not produce a syntax error" % expression)
        
        # test @GETALL vs @GET
        expression = "@GET(sthpw/task.unittest/country.code)"
        parser = ExpressionParser()
        result = parser.eval(expression, self.country)
        self.assertEquals(['USA'], result)

        expression = "@GETALL(sthpw/task.unittest/country.code)"
        parser = ExpressionParser()
        result = parser.eval(expression, self.country)
        # there should be 3 tasks pointing to 3 USA
        self.assertEquals(['USA','USA','USA'], result)

        # test comparisons
        expression = "@GET(.age) * 2.0 > 0.0"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals([True, True], result)


        # test comparisons
        expression = "@GET(.age) * 2.0 >= 0.0"
        parser = ExpressionParser()
        result = parser.eval(expression, [person, person1])
        self.assertEquals([True, True], result)


        # order of operations
        expression = "@FLOOR(2.2)"
        parser = ExpressionParser()
        result = parser.eval(expression, person)
        self.assertEquals(2.0, result)



        # suboperations
        expression = "@FLOOR(3.0 + @GET(.age) * 2.0 + 1.0)"
        parser = ExpressionParser()

        result = parser.eval(expression, person)
        self.assertEquals(3.0 + age * 2.0 + 1.0, result)

        result = parser.eval(expression, [person, person1])
        self.assertEquals([3.0 + age * 2.0 + 1.0, 3.0 + age1 * 2.0 + 1.0], result)


        # another test
        expression = "@SUM( (@GET(.age) + @GET(.age)) / 10)"
        result = parser.eval(expression, [person, person1])
        f_age = float(age)
        f_age1 = float(age1)
        expected = ( (f_age + f_age)/10 ) + ( (f_age1 + f_age1)/10 ) 
        self.assertEquals(expected, result)


        # test union
        expression = "@UNION(@GET(.age), @GET(.name_first))"
        result = parser.eval(expression, [person])
        expected = set([f_age, name_first])
        self.assertEquals(expected, set(result))

        # test intersect
        expression = "@INTERSECT(@GET(.age), @GET(.city_code))"
        result = parser.eval(expression, [person])
        expected = set([])
        self.assertEquals(expected, set(result))

        

        expression = "@INTERSECT(@SOBJECT(unittest/person), @SOBJECT(unittest/person['nationality','Smith0']))"
        result = parser.eval(expression)
        result_sk = [SearchKey.get_by_sobject(x) for x in result]
        expected = set([SearchKey.get_by_sobject(x) for x in [self.persons[0]]])
        self.assertEquals(expected, set(result_sk))
        self.assertEquals(1, len(result))


    def _test_literal(self):
        # test some full text paragraph
        person = self.persons[0]
        name_first = person.get_value("name_first")
        age = person.get_value("age")

        parser = ExpressionParser()

        # test eval of an expression within an expression
        expression = '''@EVAL( @GET(.age) )'''
        result = parser.eval(expression, person, single=True)
        self.assertEquals(age, result)


        # test shorthand of eval of an expression within an expression
        expression = '''@( @GET(.age) )'''
        result = parser.eval(expression, person)
        self.assertEquals([age], result)

        # deal with a literal
        expression = '''@( '@GET(.age)' )'''
        result = parser.eval(expression, person)
        self.assertEquals([age], result)


        # deal with a literal
        expression = '''@( '@GET(.age)'xx )'''
        try:
            result = parser.eval(expression, person)
        except SyntaxError:
            pass
        else:
            self.fail("Expression [%s] should have had a SyntaxError" % expression)


        # deal with a literal
        """
        expression = '''@( xx'@GET(.age)' )'''
        try:
            result = parser.eval(expression, person)
        except SyntaxError:
            pass
        else:
            self.fail("Expression [%s] should have had a SyntaxError" % expression)
        """



        # deal with a stringify in a literal
        expression = '''@( '{@GET(.age)}' )'''
        result = parser.eval(expression, person)
        self.assertEquals(str(age), result)

        # deal with a more complex literal
        expression = '''@( '{@GET(.age)},{@GET(.age)}' )'''
        result = parser.eval(expression, person)
        self.assertEquals("%s,%s" % (age,age), result)




    def _test_conditional(self):
        # test some full text paragraph
        person = self.persons[0]
        name_first = person.get_value("name_first")
        person.set_value('nationality', 'Cdn Cdn')

        age = person.get_value("age")

        person1 = self.persons[1]
        age1 = person1.get_value("age")

        person.set_value('nationality', 'Cdn Cdn')


        parser = ExpressionParser()

        # Try not enough arguments
        try:
            expression = '''@IF( @GET(.age) > 0 )'''
            result = parser.eval(expression, person)
        except SyntaxError:
            pass
        else:
            self.fail("Expression [%s] should have a syntax error")

        expression = '''@IF( @GET(.age) > 0, @GET(.age), '')'''
        result = parser.eval(expression, person)
        self.assertEquals([age], result)
        
        expression = '''@IF( @GET(.age) > 1000, @GET(.age), '')'''
        result = parser.eval(expression, person)
        self.assertEquals('', result)

        # try a more complex return
        expression = '''
        @IF(
            @GET(.age) > 0,
            ({@GET(.age)}),
            ''
        )
        '''
        result = parser.eval(expression, person)
        self.assertEquals('(%s)' % age, result)

        # try with 2 arguments
        expression = '''@IF(
            @GET(.age) > 1000, '({@GET(.age)})'
        )'''
        result = parser.eval(expression, person)
        self.assertEquals(None, result)

        # test string comparison
        expression = '''@IF(
            @GET(.name_first) == '%s', 'wow', 'blah'
        )''' % name_first
        result = parser.eval(expression, person)
        self.assertEquals('wow', result)


        # try it empty comparison
        expression = '''@IF(
            @GET(.name_first) == "", 'wow', 'blah'
        )'''
        result = parser.eval(expression, person)
        self.assertEquals('blah', result)


        # try it actual empty value
        expression = '''{@IF(
            @GET(.name_first) != '', 'wow', 'blah'
        )}'''
        result = parser.eval(expression, person)
        self.assertEquals('wow', result)


        # do the opposite ""
        expression = '''{@IF(
            "" != @GET(.name_first), 'wow', 'blah'
        )}'''
        result = parser.eval(expression, person)
        self.assertEquals('wow', result)


        # try it actual empty value
        expression = '''@IF(
            @GET(.name_first) != '', 'wow', 'blah'
        )'''
        result = parser.eval(expression, person)
        self.assertEquals('wow', result)


        # try it with NULL value
        expression = '''@IF(
            @GET(.name_first) != null, 'wow', 'blah'
        )'''
        result = parser.eval(expression, person)
        self.assertEquals('wow', result)

        # try a complete empty value
        expression = '''@IF(
            @GET(.name_first) != '', '', 'blah'
        )'''
        result = parser.eval(expression, person)
        self.assertEquals('', result)

        expression = '''@COUNT(sthpw/task)'''
        task_count = parser.eval(expression)

        expression = '''{@IF(@COUNT(sthpw/task)==%s, @COUNT(sthpw/task),'NONE')}'''%task_count
        result = parser.eval(expression)
        
        self.assertEquals(str(task_count), result)
        self.assertEquals(task_count, int(result))

        expression = '''{@IF(@COUNT(sthpw/task)==0, @COUNT(sthpw/task),'NONE')}'''
        result = parser.eval(expression)
        self.assertEquals('NONE', result)

        # try the case statement
        expression = '''@CASE(
            @GET(.age) > 10, 'blue',
            @GET(.age) < 10, 'green',
            @GET(.age) = 0, 'yellow',
        ) '''
        result = parser.eval(expression, person)

        if age > 10:
            expect = 'blue'
        elif age < 10:
            expect = 'green'
        elif age == 10:
            expect = 'yellow'
        #print expect, result
        self.assertEquals(expect, result)

        # try the case statement
        expression = '''@CASE(
            @GET(.nationality) == 'Cdn Cdn', 'blue',
            @GET(.nationality) == 'US US', 'green',
            @GET(.nationality) == 'Greek Greek', 'yellow'
        ) '''
        result = parser.eval(expression, person)
        nationality = person.get_value('nationality')
        if nationality == 'Cdn Cdn':
            expect = 'blue'
        elif nationality == 'US US':  
            expect = 'green'
        elif nationality == 'French French' :
            expect = 'yellow'
        #print expect, result

        
        # FIXME: this does not work yet
        #expression = '''@CASE($VALUE=~'Shot$','#4F7340')'''
        #vars = {
        #    "VALUE": 'New Shot'
        #}
        #result = parser.eval(expression, person, vars=vars)
        #self.assertEquals('#4F7340', result)

        # try a regular expression
        expression = ''''123COW' ~ '^123' '''
        result = parser.eval(expression, single=True)
        expect = True
        self.assertEquals(expect, result)


        # try some True/False comparisons
        expression = "'$VALUE' == True"
        expect = False
        vars = {
            'VALUE': ''
        }
        result = parser.eval(expression, vars=vars)
        self.assertEquals(expect, result)
	#
        vars = {'VALUE': 'foo Test'}
	self.assertEquals(Search.eval("$VALUE == 'foo Test'", vars=vars), True)
        self.assertEquals(Search.eval("'foo Test' == $VALUE", vars=vars) , True)

        # FIXME: This does not evaluate very well.  Not sure how to handle
        # this case
        '''
        expression = "$VALUE == True"
        expect = False
        vars = {
            'VALUE': ''
        }
        result = parser.eval(expression, vars=vars)
        self.assertEquals(expect, result)
        '''






    def _test_loop(self):
        # test some full text paragraph
        person = self.persons[0]
        name_first = person.get_value("name_first")
        age = person.get_value("age")

        person1 = self.persons[1]
        age1 = person1.get_value("age")


        parser = ExpressionParser()

        expr = '''@FOREACH(
                    @GET(unittest/person.name_first), '<li>%s</li>'
                  )'''
        result = parser.eval(expr)
        expected = ["<ul>%s</ul>" % x.get_value("name_first") for x in self.persons]
        #self.assertEquals(expected, result)


        # FIXME: ordering problem
        # test join
        #expr = '''@JOIN(
        #            @GET(unittest/person.name_first), ':'
        #          )'''
        #result = parser.eval(expr)
        #expected = [x.get_value("name_first") for x in self.persons]
        #expected.sort()
        #expected.reverse()
        #expected = ":".join( expected )
        #self.assertEquals(expected, result)



        # TODO: not yet functional ... cannot to two sub aggregates
        #expr = '''@JOIN(
        #            @FOREACH(
        #                @GET(sthpw/login.login), '<li>%s</li>'
        #            ), '\n'
        #          )'''
        #result = parser.eval(expr)
        #print result
        


    def _test_update(self):
        # test some updates
        person = self.persons[0]
        name_first = person.get_value("name_first")
        age = person.get_value("age")

        person1 = self.persons[1]
        age1 = person1.get_value("age")

        parser = ExpressionParser()


        expr = '''@UPDATE( @SOBJECT(), 'name_last', 'New Last Name' )'''
        result = parser.eval(expr, person, single=True)
        self.assertEquals("New Last Name", result.get_value('name_last') )


        # update all of the tasks
        
        # create task
        task = Task.create(person, "cow", "This is a cow task", context='cow')
        task.set_value('status', 'Waiting')
        task.commit()

        expr = '''@UPDATE( @SOBJECT(sthpw/task), 'status', 'Approved' )'''
        result = parser.eval(expr, person)
        self.assertEquals("Approved", result[0].get_value("status"))

        # before update, the original cow task is still "Waiting"
        self.assertEquals("Waiting", task.get_value("status"))
        task.update()

        self.assertEquals("Approved", task.get_value("status"))

        expression = '''@IF(@GET(sthpw/task.status) == 'Approved', @UPDATE( @SOBJECT(sthpw/task), 'status', 'Review' ))'''
        self.parser.eval(expression, person)
        expression = '''@GET(sthpw/task.status)'''
        result = self.parser.eval(expression, person)
        self.assertEquals(result, ["Review"])

        
    def _test_palette(self):

        from pyasm.web import Palette

        palette = Palette.get()

        keys = ['color', 'color2', 'color3', 'background', 'background2', 'background3']
        for key in keys:
            expr = "@GET(palette.%s)" % key
            parser = ExpressionParser()
            result = parser.eval(expr, single=True)
            expected = palette.color(key)

        self.assertEquals(expected, result)

        return





    def _test_file(self):
        person = self.persons[0]
        name_first = person.get_value("name_first")
        age = person.get_value("age")

        person1 = self.persons[1]
        age1 = person1.get_value("age")

        return



        # check in a file
        from pyasm.checkin import FileCheckin, FileAppendCheckin
        import shutil
        orig_path = "./expression_test.png"
        file_path = "./expression_testx1.png"
        shutil.copy(orig_path, file_path)
        file_path2 = "./expression_testx2.png"
        shutil.copy(orig_path, file_path2)
        file_path3 = "./expression_testx3.png"
        shutil.copy(orig_path, file_path3)

        checkin = FileCheckin(person, file_path, context="expr")
        checkin.execute()
        snapshot = checkin.get_snapshot()
        snapshot_code = snapshot.get_value("code")

        checkin = FileAppendCheckin(snapshot_code, file_path2, file_types='cow')
        checkin.execute()
        snapshot = checkin.get_snapshot()

        checkin = FileCheckin(person, file_path3, context="expr")
        checkin.execute()


        parser = ExpressionParser()

        # the hard long way of getting a file path
        base_dir = Environment.get_asset_dir()
        expr = '''@SOBJECT(sthpw/snapshot['context','expr']['is_latest','true'].sthpw/file)'''
        files = parser.eval(expr, person, list=True)
        for file in files:
            rel_dir = file.get_value("relative_dir")
            file_name = file.get_value("file_name")
            path = "%s/%s/%s" % (base_dir, rel_dir, file_name)
            print path
            print file.get_value("checkin_dir")

    def _test_custom_layout(self):
        html= '''
<td style='text-align:left'><b>[expr]@GET(.name_first)[/expr]</b></td>
<td style='text-align:right'><b>[abs_expr]@COUNT(sthpw/project['code','unittest'])[/abs_expr]</b></td>
<td style='text-align:right'><b>[abs_expr]@FORMAT('380.5', '-$1,234.00')[/abs_expr]</b></td>
<td style='text-align:right'><b>[abs_expr]@FORMAT(-100.80, '-$1,234.00')[/abs_expr]</b></td>'''
        
        p = re.compile('\[expr\](.*?)\[\/expr\]')
        parser = ExpressionParser()
        matches = p.finditer(html)
        self.search_key = 'unittest/person?project=unittest&id=2'
        #sobject = SearchKey.get_by_search_key(self.search_key)
        sobjects = [self.persons[0]]
        for m in matches:
            full_expr = m.group()
            expr = m.groups()[0]
            result = parser.eval(expr, sobjects, single=True, state={})
            result = Common.process_unicode_string(result)
            html = html.replace(full_expr, result )

        
        
        p = re.compile('\[abs_expr\](.*?)\[\/abs_expr\]')
        matches = p.finditer(html)
        for m in matches:
            full_expr = m.group()
            expr = m.groups()[0]
            result = parser.eval(expr, single=True)
            result = Common.process_unicode_string(result)
            html = html.replace(full_expr, result )
        try: 
            self.assertEquals( html, 
        '''
<td style='text-align:left'><b>person0</b></td>
<td style='text-align:right'><b>1</b></td>
<td style='text-align:right'><b>$380.50</b></td>
<td style='text-align:right'><b>-$100.80</b></td>''')
        except: # depends on the locale of the computer
            self.assertEquals( html, 
        '''
<td style='text-align:left'><b>person0</b></td>
<td style='text-align:right'><b>1</b></td>
<td style='text-align:right'><b>$380.50</b></td>
<td style='text-align:right'><b>($100.80)</b></td>''')
            

    def _test_color(self):
        parser = ExpressionParser()

        expr = '''@COLOR( 'color', '10' )'''
        result = parser.eval(expr, single=True)
        self.assertEquals(result, '#191919')

        expr = '''@COLOR( 'unknown_color' )'''
        result = parser.eval(expr, single=True)
        # default to color (black)
        self.assertEquals(result, '#000')
    
    def _test_connection(self):
        from tactic_client_lib import TacticServerStub
        from pyasm.biz import SObjectConnection
        server = TacticServerStub.get()
        server.connect_sobjects(self.country.get_search_key(), self.city_task.get_search_key(), context='task')
        sobj = SObjectConnection.get_connected_sobject(self.country, context='task')

       
        # verify the connection exists
        self.assertEquals(sobj.get_id(), self.city_task.get_id())
        self.assertEquals(sobj.get_search_type(), self.city_task.get_search_type())

        parser = ExpressionParser()
        expr = '@GET(connect.id)'
        result = parser.eval(expr, sobjects=[self.country], single=True)
        self.assertEquals(result, self.city_task.get_id())

        # without any input sobject or env_sobjects, it should return None
        parser = ExpressionParser()
        expr = '@GET(connect.id)'
        result = parser.eval(expr, single=True)
        self.assertEquals(result, None)


        expr = '@GET(sobject.connect.id)'
        result = parser.eval(expr, env_sobjects={ 'sobject': self.country}, single=True)
        self.assertEquals(result, self.city_task.get_id())

        expr = '@GET(sobject.connect.parent.code)'
        result = parser.eval(expr, env_sobjects={ 'sobject': self.country}, single=True)
        
        self.assertEquals(result, self.city.get_code())

        # ensure env_sobjects can be used multiple times
        expr = '@GET(sobject.connect.sobject.code)'
        result = parser.eval(expr, env_sobjects={ 'sobject': self.country}, single=True)
       
        self.assertEquals(result, self.country.get_code())



        server.connect_sobjects(self.country.get_search_key(), self.city_task2.get_search_key(), context='main_task')
        sobj = SObjectConnection.get_connected_sobject(self.country, context='main_task')
        self.assertEquals(sobj.get_id(), self.city_task2.get_id())
        expr = "@GET(connect['@CONTEXT','main_task'].id)"
        result = parser.eval(expr, sobjects=[self.country], single=True)
        self.assertEquals(result, self.city_task2.get_id())

        expr = "@GET(connect['@CONTEXT','main_task']['@CONTEXT','EQ','main'].id)"
        result = parser.eval(expr, sobjects=[self.country], single=True)
        self.assertEquals(result, self.city_task2.get_id())


    def _test_instance(self):
        expr = "@SOBJECT(unittest/city.unittest/person)"
        people = Search.eval(expr, [self.country])
        num = len(people)

        # test instance relationship
        expr = "@SEARCH(unittest/person)"
        search = Search.eval(expr, [self.country])
        people = search.get_sobjects()
        self.assertEquals(num, len(people))
        

        expr = "@SOBJECT(unittest/person)"
        people = Search.eval(expr, [self.country])
        self.assertEquals(num, len(people))
        
 

        expr = "@SOBJECT(unittest/country)"
        country = Search.eval(expr, self.persons[0], single=True)
        self.assertEquals( country.get_code(), self.country.get_code())
       

        Project.set_project('sample3d')
        shots = Search.eval("@SOBJECT(prod/shot)")
        print "shots: ", len(shots)
        assets = Search.eval("@SOBJECT(prod/asset)")
        print "assets: ", len(assets)

        Project.set_project("unittest")




    def _test_cache(self):
        expr = '@COUNT(unittest/person)'
        parser = ExpressionParser()
        result = parser.eval(expr, single=True)
        self.assertEquals(result, 8)
        person = Person.create( "new_person" , "Mr",
                        "Z" , "Fake Unittest Person Z")
        person.set_value("age", "300")
        person.commit()
        """TODO: add a use_cache=False kwargs to eval()
        expr = '@SOBJECT( unittest/person)'
        search = Search('unittest/person')
        print "LEN ", len(search.get_sobjects())
        parser = ExpressionParser()
        result = parser.eval(expr)
        print "RES ", result
        self.assertEquals(len(result), 9)
        """

if __name__ == '__main__':
    unittest.main()




