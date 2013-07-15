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

from pyasm.security import *

from sql import *
from search import *
from transaction import *
from database_impl import *
from pyasm.unittest import *
from pyasm.biz import Project
import unittest

class SearchTest(unittest.TestCase):


    def setUp(my):
        # start batch environment
        Batch()
        from pyasm.web.web_init import WebInit
        WebInit().execute()


    def test_all(my):
        test_env = UnittestEnvironment()
        test_env.create()
        my.transaction = Transaction.get(create=True)
        try:

            my.person = Person.create( "5", "a",
                    "ComputerWorld", "1")
            my.person = Person.create( "4", "b",
                    "ComputerWorld", "3")
            my.person = Person.create( "3", "c",
                    "ComputerWorld", "3")
            my.person = Person.create( "2", "d",
                    "ComputerWorld", "4") 
            my.person = Person.create( "1", "e",
                    "ComputerWorld", "5") 
            my._test_order_by()                               
            my._test_search_key()
            my._test_search()

            # FIXME: this requires sample3d project
            #my._test_search_other_project()
            my._test_search_type()
            my._test_metadata()
            my._test_search_type_existence()
            my._test_project()
            my._test_search_filter()
            my._test_dates_search()
            my._test_child_search()
            my._test_parent_search()
            my._test_add_column_search()
            my._test_commit()
            my._test_set_value()
            my._test_get_by_statement()
        finally:
            my.transaction.rollback()
            Project.set_project('unittest')

            test_env.delete()

    def _test_order_by(my):


        sobjects = Search.eval("@SOBJECT(unittest/person['@ORDER_BY','description desc, name_first desc'])")
        sobjects1 = Search.eval("@SOBJECT(unittest/person['@ORDER_BY','description, name_first'])")
        sobjects2 = Search.eval("@SOBJECT(unittest/person['@ORDER_BY','description desc, name_first'])")
        name_list = []
        name_list1 = []
        name_list2 = []
        for x in sobjects:
             name = x.get_value('name_last') 
             name_list.append(name)
        for x in sobjects1:
             name = x.get_value('name_last') 
             name_list1.append(name)
        for x in sobjects2:
             name = x.get_value('name_last') 
             name_list2.append(name)
        my.assertEquals(name_list,['e','d','b','c','a'])
        my.assertEquals(name_list1,['a','c','b','d','e'])
        my.assertEquals(name_list2,['e','d','c','b','a'])


        search = Search('unittest/city')
        search.add_order_by('name')
        statement = search.get_statement()
        my.assertEquals(statement, '''SELECT "city".* FROM "city" ORDER BY "city"."name"''')


        search = Search('unittest/person')
        search.add_order_by('unittest/city.unittest/country.code')
        statement = search.get_statement()
        my.assertEquals(statement, '''SELECT "person".* FROM "person" LEFT OUTER JOIN "city" ON "person"."city_code" = "city"."code" LEFT OUTER JOIN "country" ON "city"."country_code" = "country"."code" ORDER BY "country"."code"''')


        search = Search('unittest/person')
        search.add_order_by('unittest/city.id')
        statement = search.get_statement()
        my.assertEquals(statement, '''SELECT "person".* FROM "person" LEFT OUTER JOIN "city" ON "person"."city_code" = "city"."code" ORDER BY "city"."id"''')


        search = Search('unittest/person')
        search.add_order_by('unittest/city.id desc')
        statement = search.get_statement()
        my.assertEquals(statement, '''SELECT "person".* FROM "person" LEFT OUTER JOIN "city" ON "person"."city_code" = "city"."code" ORDER BY "city"."id" desc''')
        
        
        # with the built-in order-by logic, order by code is added
        search.get_sobjects()
        statement = search.get_statement()
        my.assertEquals(statement, '''SELECT "person".* FROM "person" LEFT OUTER JOIN "city" ON "person"."city_code" = "city"."code" ORDER BY "city"."id" desc, "person"."code"''')


    def _test_get_by_statement(my):
        types = ['admin','ben','beth']
        joined_statements = []
        for type in types:
            select = Search('sthpw/login')
            select.add_filter('login', type)
            select.set_show_retired(False)
            select.add_order_by("login")
            statement = select.get_statement()
            joined_statements.append(statement)

 
        if len(joined_statements) > 1:
            joined_statements = ["(%s)"%x for x in joined_statements]
            statement = ' union all '.join(joined_statements)
        elif len(joined_statements) == 1:
            statement = joined_statements[0]
      
    
        logins =  Login.get_by_statement(statement)
        my.assertEquals(len(logins), 3)
        my.assertEquals(statement, '''(SELECT "login".* FROM "login" WHERE "login" = 'admin' ORDER BY "login"."login") union all (SELECT "login".* FROM "login" WHERE "login" = 'ben' ORDER BY "login"."login") union all (SELECT "login".* FROM "login" WHERE "login" = 'beth' ORDER BY "login"."login")''')

        
    def _test_add_column_search(my):
        search = Search('sthpw/task')
        search.add_filter('status','Assignment')
        search.add_column('id')
        search.add_column('timestamp')
        sobject = search.get_sobject()
        my.assertEquals(len(sobject.data), 2)
        my.assertEquals(True, sobject.has_value('timestamp'))
        
        search = Search('sthpw/task')
        search.add_filter('status','Assignment')
        sobject = search.get_sobject()

        #my.assertEquals(len(sobject.data), 27)
        my.assertEquals(True, sobject.has_value('assigned'))
        my.assertEquals(True, sobject.has_value('process'))

    def _test_child_search(my):

        from pyasm.biz import Task
        person = SearchType.create('unittest/person')
        person.set_value('name_first','pete')
        person.commit()
        for xrange in (1, 50):
            Task.create(person, 'process_AA','some task', 'admin', context='process_AA')
        person2 = SearchType.create('unittest/person')
        person2.set_value('name_first','jamie')
        person2.commit()

        person2_tasks = []
        for xrange in (1, 50):
            person2_tasks.append(Task.create(person2, 'process_BB','some task', 'admin', context='process_BB'))
        task_search = Search('sthpw/task')
        task_search.add_filters('process', ['process_AA', 'process_BB'])
        tasks = task_search.get_sobjects()
        search2 = Search('unittest/person')
        search2.add_relationship_filters(tasks)
        persons = search2.get_sobjects()
        
        search3 = Search('unittest/person')
        search3.add_relationship_search_filter(task_search)
        persons_fast = search3.get_sobjects()
        
        my.assertEquals(SObject.get_values(persons, 'id'), SObject.get_values(persons_fast, 'id'))
        my.assertEquals(SObject.get_values(persons_fast, 'name_first'), ['pete','jamie'])

        # if I retire all the tasks for person2
        for task in tasks:
            if task.get_value('process') =='process_BB':
                task.retire()

        task_search = Search('sthpw/task')
        task_search.add_filters('process', ['process_AA', 'process_BB'])
        tasks = task_search.get_sobjects()
        search4 = Search('unittest/person')
        search4.add_relationship_search_filter(task_search)
        persons_fast = search4.get_sobjects()
        
        search2 = Search('unittest/person')
        search2.add_relationship_filters(tasks)
        persons = search2.get_sobjects()

        my.assertEquals(SObject.get_values(persons, 'id'), SObject.get_values(persons_fast, 'id'))
        my.assertEquals(SObject.get_values(persons_fast, 'name_first'), ['pete'])


        
            
    def _test_parent_search(my):
        from pyasm.biz import Task
        person = SearchType.create('unittest/person')
        person.set_value('name_first','burt')
        person.commit()

        person2 = SearchType.create('unittest/person')
        person2.set_value('name_first','sean')
        person2.commit()
 
        person_search = Search('unittest/person')
        person_search.add_filters('id', [person.get_id(), person2.get_id()])
        for xrange in (1, 50):
            Task.create(person, 'process_CC','some task', 'admin', context='process_CC')
        for xrange in (1, 50):
            Task.create(person2, 'process_DD','some task', 'admin')
        
        # find parent of tasks
        search2 = Search('sthpw/task')
        search2.add_relationship_filters([person,person2])
        tasks = search2.get_sobjects()
        
        search3 = Search('sthpw/task')
        search3.add_relationship_search_filter(person_search)
        tasks2 = search3.get_sobjects()
        
        my.assertEquals(SObject.get_values(tasks, 'id'), SObject.get_values(tasks2, 'id'))






    def _test_search_other_project(my):
        # while in unittest, search for pacman assets
        search = Search('sthpw/search_object')
        search.add_filter('search_type','prod/asset')
        sobject = search.get_sobject()
        # make sure the database field is not hardcoded pacman
        sobject.set_value('database', '{project}')
        sobject.commit()

        asset = SearchType.create('prod/asset?project=sample3d')
        asset.set_value('code','unittest001')
        asset.set_value('pipeline_code','model')
        asset.commit()

        asset = SearchType.create('prod/asset?project=sample3d')
        asset.set_value('code','unittest002')
        asset.set_value('pipeline_code','model')
        asset.commit()

        search2 = Search("prod/asset?project=sample3d")
        search2.add_filter("pipeline_code", "model")
        sobjects = search2.get_sobjects()
        my.assertEquals(True, len(sobjects) > 0 )
        my.assertEquals("model", sobjects[0].get_value('pipeline_code'))
        my.assertEquals("sample3d", sobjects[0].get_database())
        my.assertEquals("sample3d", sobjects[1].get_database())

        search3 = Search("prod/asset?project=sample3d")
        search3.add_regex_filter("pipeline_code", "model|cg_asset")
        search3.add_filter("code", "chr003")
        sobject = search3.get_sobject()
        sobject.set_value('description','some char')
        sobject.commit()

        updated_sobject = search3.get_sobject(redo=True)

        my.assertEquals("some char", updated_sobject.get_value('description'))

    def _test_search(my):

        # create the person
        person = SObjectFactory.create("unittest/person")
        person.set_value("name_first", "XXX")
        person.set_value("name_last", "Smith")
        person.set_value("nationality", "Canada")
        person.commit()

        search = Search("unittest/person")
        search.add_filter("name_first", "XXX")
        search.add_filter("name_last", "Smith")
        person = search.get_sobject()
        my.assertEquals("XXX", person.get_value("name_first") )

        xxx_id = person.get_id()

        # test_set_value
        person.set_value("name_first", "YYY")
        person.set_value("name_last", "Cowser")
        person.commit()

        search2 = Search("unittest/person")
        search2.add_filter("name_first", "YYY")
        search2.add_filter("name_last", "Cowser")
        person2 = search2.get_sobject()

        yyy_id = person2.get_id()

        my.assertEquals( xxx_id, yyy_id )


        # test attributes
        name_first = person.get_attr_value("name_first")
        my.assertEquals("YYY", name_first )

        name_last = person.get_attr_value("name_last")
        my.assertEquals("Cowser", name_last )




    def _test_search_type(my):
        '''test that search types behave properly for templating'''
        SearchType.set_global_template("project", "unittest")

        #search_type = SearchType.get("prod/asset")
        sobject = SearchType.create("unittest/person")
        key = sobject.get_search_type()
        my.assertEquals(key, "unittest/person?project=unittest")



    def _test_metadata(my):
        # create an arbitrary sobject
        person = SearchType.create("unittest/person")

        # get metadata that does not exist
        cow = person.get_metadata_value("cow")
        my.assertEquals("", cow)

        # json dict doesn't have this method
        #person.get_metadata_xml().clear_xpath_cache()

        # set the value
        person.set_metadata_value("cow", "angus")
        cow = person.get_metadata_value("cow")
        my.assertEquals("angus", cow)

        # add a whole bunch of entries:
        data = {
            'color': 'blue',
            'height': '195cm',
            'weight': '102Kg'
        }
        person.add_metadata(data)
        
        color = person.get_metadata_value("color")
        height = person.get_metadata_value("height")
        my.assertEquals("blue", color)
        my.assertEquals("195cm", height)

        # replace the entire structure
        person.add_metadata(data, replace=True)
        cow = person.get_metadata_value("cow")
        my.assertEquals("", cow)

        # if someone set it with non-json data, it should still return as is
        person.metadata = None
        person.set_value('metadata','testing==OK')
        meta_dict = person.get_metadata_dict()
        my.assertEquals('testing==OK', meta_dict)
            



    def _test_search_type_existence(my):
        '''test a bunch of search types to see if they are registered'''
        # DEPRECATED
        return
        #TODO: add more search types here
        st_list = ['prod/shot_instance','prod/sequence_instance','sthpw/widget_extend']
        for st in st_list:
            search = Search(SearchType.SEARCH_TYPE)
            search.add_filter('search_type', st)
            sobjects = search.get_sobjects()
            my.assertEquals(len(sobjects), 1)



    def _test_search_key(my):

        # test a correct search_key
        search_key = "prod/asset?project=sample3d&code=chr001"

        search_type = SearchKey.extract_base_search_type(search_key)
        my.assertEquals("prod/asset", search_type)

        project = SearchKey.extract_project(search_key)
        my.assertEquals("sample3d", project)

        code = SearchKey.extract_code(search_key)
        my.assertEquals("chr001", code)

        # test a long one
        search_key = "prod/asset?project=sample3d&db=postgres&code=chr001"

        search_type = SearchKey.extract_base_search_type(search_key)
        my.assertEquals("prod/asset", search_type)

        database = SearchKey.extract_database(search_key)
        my.assertEquals("postgres", database)

 
        project = SearchKey.extract_project(search_key)
        my.assertEquals("sample3d", project)

        code = SearchKey.extract_code(search_key)
        my.assertEquals("chr001", code)


        #eval(@GET(prod/asset.code))
        #eval(@GET(prod/asset.code?project=sample3d)) ???


        search_key = "sthpw/project"
        code = "unittest"

        search = Search(search_key)
        search.add_filter("code", code)
        sobject = search.get_sobject()

        search_key = SearchKey.get_by_sobject(sobject)
        my.assertEquals("sthpw/project?code=unittest", search_key)







    def _test_project(my):

        from pyasm.biz import Project
        sql = Project.get_database_impl()

        # Don't bother running if you don't have sample3d
        if not sql.database_exists('sample3d'):
            return


        Project.set_project("sthpw")

        sobject = SearchType.create('prod/shot?project=sample3d', columns=['code', 'sequence_code', 'pipeline_code'], result=['S001','HT001','shot'])
        my.assertEquals("prod/shot?project=sample3d", sobject.get_search_type())
       
        if sql.database_exists('sample3d'):
            db_resource = Project.get_db_resource_by_search_type('prod/bin?project=sample3d')
            exists= sql.table_exists(  db_resource ,'bin')
            if exists:
                search = Search('prod/bin', project_code='sample3d')
                my.assertEquals("prod/bin?project=sample3d", search.get_search_type())
        # check that a search type is properly created
        search_type = SearchType.get("prod/shot?project=sample3d")
        base_key = search_type.get_base_key()
        my.assertEquals("prod/shot", base_key)

    
        # NOTE: search_type get_full_key() method is deprecated.
       


        # test that the sobject maintains the search type
        sobject = SearchType.create("prod/shot?project=sample3d")
        search_type = sobject.get_search_type()
        my.assertEquals("prod/shot?project=sample3d", search_type)

        # set it back to unittest
        Project.set_project("unittest")

        # test current project is added when there is not project set
        sobject = SearchType.create("prod/shot")
        search_type = sobject.get_search_type()
        my.assertEquals("prod/shot?project=unittest", search_type)


        # test current project is added when there is not project set, even
        # when the project has changed
        sobject = SearchType.create("prod/shot")
        
        search_type = sobject.get_search_type()
        my.assertEquals("prod/shot?project=unittest", search_type)

        if sql.database_exists('sample3d'):
            Project.set_project("sample3d")

            project_code = Project.get_project_code()
            my.assertEquals("sample3d", project_code)

        # set it back to unittest project
        Project.set_project("unittest")

        # test the search
        if sql.database_exists('sample3d'):
            search_type = "prod/shot?project=sample3d"
            search = Search(search_type)
            project_code = search.get_project_code()
            my.assertEquals("sample3d", project_code)

            # test the search project code even though the project has hanved
            search_type = "prod/shot?project=sample3d"
            search = Search(search_type)
            project_code = search.get_project_code()
            my.assertEquals("sample3d", project_code)

            Project.set_project("admin")
            project_code = search.get_project_code()
            my.assertEquals("sample3d", project_code)

            project_code = Project.get_project_code()
            my.assertEquals("admin", project_code)

        # set it back to unittest project
        Project.set_project("unittest")


    def _test_search_filter(my):
        search = Search("unittest/person")
        search.add_filter("name_first", "YYY")
        search.add_filter("name_last", "Cowser")

        statement = search.get_statement()
        expected = """SELECT "person".* FROM "person" WHERE "name_first" = 'YYY' AND "name_last" = 'Cowser'"""

        my.assertEquals(expected, statement)

        search2 = Search("unittest/city")
        search2.add_search_filter("id", search)

        statement = search2.get_statement()
        expected = """SELECT "city".* FROM "city" WHERE "id" in ( SELECT "person".* FROM "person" WHERE "name_first" = 'YYY' AND "name_last" = 'Cowser' )"""
        my.assertEquals(expected, statement)

        search = Search("unittest/person")
        search.add_op('begin')
        search.add_filter("name_first", "YYY")
        search.add_filter("name_last", "Cowser")
        search.add_op('or')
        search.add_filter("city_code", "YYZ")
        statement = search.get_statement()
        expected = """SELECT "person".* FROM "person" WHERE ( "name_first" = 'YYY' OR "name_last" = 'Cowser' ) AND "city_code" = 'YYZ'"""

        my.assertEquals(expected, statement)

        
        # mix "is not" with "is" logic
        search = Search("unittest/person")


        search.add_op('begin')
        search.add_filter('name_first', 'T', op='~')
        search.add_filter('name_first', 'U', op='~')
        search.add_op('or')

        search.add_op('begin')
        search.add_filter('nationality','canadian', op='!=')
        search.add_filter('nationality', None)
        search.add_op('or')


        search.add_op('begin')
        search.add_filter("name_first", "YYY")
        search.add_filter("name_last", "Cowser")
        search.add_filter("city_code", "YYZ")
        search.add_op('or')
    

        # this is optional
        #search.add_op('and')
        expected = """SELECT "person".* FROM "person" WHERE "name_first" ~ 'T' OR "name_first" ~ 'U' ) AND ( "nationality" != 'canadian' OR "nationality" is NULL ) AND ( "name_first" = 'YYY' OR "name_last" = 'Cowser' OR "city_code" = 'YYZ'"""


        statement = search.get_statement()
        my.assertEquals(expected, statement)


        # old style without begin
        search = Search('sthpw/login')
        search.add_where("\"license_type\" = 'user'")
        search.add_where("\"license_type\" is NULL")
        search.add_op('or')

        expected = """SELECT "login".* FROM "login" WHERE "license_type" = \'user\' OR "license_type" is NULL"""
        statement = search.get_statement()
        my.assertEquals(expected, statement)


        # extra dangling begin, default back to AND
        search = Search('sthpw/login')
        #search.add_op('begin')
        search.add_op('begin')
        search.add_where("\"license_type\" = 'user'")
        search.add_where("\"license_type\" is NULL")
        #search.add_op('or')

        expected = """SELECT "login".* FROM "login" WHERE "license_type" = \'user\' AND "license_type" is NULL"""
        statement = search.get_statement()
        my.assertEquals(expected, statement)
    
        # extra dangling begin, with 2 ORs applied already
        search = Search('sthpw/login')
        search.add_op('begin')
        search.add_op('begin')
        search.add_where("\"license_type\" = 'user'")
        search.add_where("\"license_type\" is NULL")
        search.add_op('or')

        search.add_op('begin')
        search.add_where("\"license_type\" = 'float'")
        search.add_op('or')


        expected = """SELECT "login".* FROM "login" WHERE ( "license_type" = \'user\' OR "license_type" is NULL ) AND "license_type" = \'float\'"""
        statement = search.get_statement()
        my.assertEquals(expected, statement)

        # extra dangling begin, with 2 ORs applied already
        search = Search('sthpw/login')
        search.add_op('begin')
        search.add_filter('namespace','sample3d')
        search.add_op('begin')
        search.add_where("\"license_type\" = 'user'")
        search.add_where("\"license_type\" is NULL")
        search.add_op('or')

        search.add_op('begin')
        search.add_where("\"license_type\" = 'float'")
        search.add_op('or')
        search.add_op('or')


        expected = """SELECT "login".* FROM "login" WHERE "namespace" = \'sample3d\' OR ( "license_type" = \'user\' OR "license_type" is NULL ) OR "license_type" = \'float\'"""
        statement = search.get_statement()
        my.assertEquals(expected, statement)


        # triple ands on level 0, OR on level 1
        search = Search("sthpw/task")


        search.add_op('begin')
        search.add_filter('process', 'anim')
        search.add_filter('status', 'Pending')
        search.add_filter('assigned' , 'admin')
        search.add_op('and')
        
        search.add_op('begin')
        search.add_filter('process', 'layout')
        search.add_filter('status', 'Assignment')
        search.add_filter('assigned' , 'fil')
        search.add_op('and')


       
        search.add_op('or')
    

        expected = """SELECT "task".* FROM "task" WHERE ( "process" = \'anim\' AND "status" = \'Pending\' AND "assigned" = \'admin\' ) OR ( "process" = \'layout\' AND "status" = \'Assignment\' AND "assigned" = \'fil\' )"""


        statement = search.get_statement()
        my.assertEquals(expected, statement)
       
        # test is NULL and is not NULL
        search = Search("unittest/person")
        search.add_op_filters([("name_first", 'is', 'NULL')])

        statement = search.get_statement()
        expected = """SELECT "person".* FROM "person" WHERE "name_first" is NULL"""
        my.assertEquals(expected, statement)

        # lowercase null treated as string
        search = Search("unittest/person")
        search.add_op_filters([("name_first", 'is', 'null')])

        statement = search.get_statement()
        expected = """SELECT "person".* FROM "person" WHERE "name_first" is 'null'"""
        my.assertEquals(expected, statement)

        search = Search("unittest/person")
        search.add_op_filters([("name_last", 'is not', 'NULL')])

        statement = search.get_statement()
        expected = """SELECT "person".* FROM "person" WHERE "name_last" is not NULL"""
        my.assertEquals(expected, statement)

    def _test_relationship_filter(my):

        search = Search("unittest/person")
        search.add_filter("name_first", "YYY")
        search.add_filter("name_last", "Cowser")

        search2 = Search("unittest/city")
        search2.add_search_filter("id", search)

    def _test_dates_search(my):

        search = Search("unittest/person")
        search.add_date_range_filter("start_date", "2010-01-01", "2010-02-01")
        expected = """SELECT "person".* FROM "person" WHERE "start_date" >= '2010-01-01 00:00:00' AND "start_date" < '2010-02-02 00:00:00'"""
        my.assertEquals(expected, search.get_statement() )


        search = Search("unittest/person")
        search.add_dates_overlap_filter("start_date", "end_date", "2010-01-01", "2010-02-01")
        expected = '''SELECT "person".* FROM "person" WHERE "person"."id" in (SELECT "person"."id" FROM "person" WHERE ( "person"."start_date" <= '2010-01-01 00:00:00' AND "person"."end_date" >= '2010-01-01 00:00:00' ) OR ( "person"."end_date" >= '2010-02-02 00:00:00' AND "person"."start_date" <= '2010-02-02 00:00:00' ) OR ( "person"."start_date" >= '2010-01-01 00:00:00' AND "person"."end_date" <= '2010-02-02 00:00:00' ))'''

        my.assertEquals(expected, search.get_statement() )

    def _test_commit(my):
        
        person_s = Search('unittest/person')
        person_s.add_filter('name_first','pete')

        person = person_s.get_sobject()
        from pyasm.biz import Note
        Note.create(person, "3 slashes \\\\\\", context="unittest_commit", process="unittest_commit")
        search = Search('sthpw/note')
        search.add_filter('process','unittest_commit')
        search.set_limit(1)
        note = search.get_sobject()
        my.assertEquals(note.get_value('note'), "3 slashes \\\\\\")


    def _test_set_value(my): 
        ''' test with different Database Impl'''
        update = Update()
        update.set_database('sthpw')
        update.set_table('task')
        update.set_value('timestamp','2012-12-12')
        update.set_value('timestamp','2012-12-12')
        my.assertEquals( update.get_statement(), """UPDATE "task" SET "timestamp" = '2012-12-12'""")

        update.set_value('timestamp','NOW')
        my.assertEquals( update.get_statement(), """UPDATE "task" SET "timestamp" = 'now()'""")

        sql_impl = DatabaseImpl.get('SQLServer')
        update.impl = sql_impl
        update.set_value('timestamp','2012-12-12')
        update.set_value('timestamp','2012-12-12')
        my.assertEquals( update.get_statement(), """UPDATE [task] SET "timestamp" = convert(datetime2, \'2012-12-12\', 0)""")
        update.set_value('timestamp','NOW')
        my.assertEquals( update.get_statement(), """UPDATE [task] SET "timestamp" = getdate()""")




if __name__ == "__main__":
    unittest.main()

