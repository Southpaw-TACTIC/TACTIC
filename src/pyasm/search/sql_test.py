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

from pyasm.security import *
from transaction import *
from search import *
from sql import *
from database_impl import *
from pyasm.biz import Project
from pyasm.common import Container
from pyasm.unittest import UnittestEnvironment
from pyasm.unittest import UnittestEnvironment

import unittest

class SqlTest(unittest.TestCase):

    def setUp(my):
        # intialiaze the framework as a batch process
        batch = Batch()
        from pyasm.web.web_init import WebInit
        WebInit().execute()

        my.test_env = UnittestEnvironment()
        my.test_env.create()

    def test_all(my):

      

        try:

            db_res = DbResource.get_default('unittest')
            sql = DbContainer.get(db_res)
            impl = sql.get_database_impl()
            db_type = impl.get_database_type()
            if db_type == "PostgreSQL":
                my.prefix = '''"unittest"."public".'''
                my.sthpw_prefix = '''"sthpw"."public".'''
            elif db_type == "Sqlite":
                my.prefix = ""
                my.sthpw_prefix = ""
            else:
                my.prefix = '''"unittest".'''
                my.sthpw_prefix = '''"sthpw".'''


            my._test_get_connect()
            my._test_select_class()
            my._test_insert_class()
            my._test_update_class()
            my._test_insert_and_delete()
            my._test_create_table()
            my._test_transaction()
            my._test_order_by()
            my._test_rpn_filters()
            my._test_search_filter()
            my._test_join()

            # it doesn't allow dropping of a column
            if db_type != 'Sqlite':
                my._test_add_drop_column()
       
        finally:
            Project.set_project('unittest')
            my.test_env.delete()

    def _test_get_connect(my):
        database= 'unittest'
        project = Project.get_by_code(database)
        db_resource= project.get_project_db_resource()
        sql1 = DbContainer.get(db_resource)
        sql2 = DbContainer.get(db_resource)
        
        my.assertEquals(sql1, sql2)

    def _test_select_class(my):
        """ test a select """
        select = Select()
        db_res = DbResource.get_default('unittest')
        select.set_database(db_res)
        select.add_table("person")
        select.add_where("\"name_first\" = 'megumi'")
        select.add_order_by("name_last")

        statement = select.get_statement()

        
        sql = DbContainer.get(db_res)
        impl = sql.get_database_impl()
        db_type = impl.get_database_type()

        expected = '''SELECT %s"person".* FROM %s"person" WHERE "name_first" = 'megumi' ORDER BY "person"."name_last"''' % (my.prefix, my.prefix)

        my.assertEquals( expected, statement )

        # test for doubling of apostrophe
        select = Select()
        select.set_database(db_res)
        select.add_table("person")
        select.add_filter('name_last', "john's", op='!=')
        statement = select.get_statement()

        expected = """SELECT %s"person".* FROM %s"person" WHERE "person"."name_last" != 'john''s'""" % (my.prefix, my.prefix)
        my.assertEquals( expected, statement )


    def _test_insert_class(my):
        """test an insert"""
        insert = Insert()
        insert.set_table("person");
        insert.set_value("name_first", "megumi");
        insert.set_value("name_last", "takamori");
        statement = insert.get_statement()

        db_res = DbResource.get_default('unittest')
        sql = DbContainer.get(db_res)

        if sql.get_database_type() == "Oracle":
            expected = "INSERT INTO \"person\" (\"id\", \"name_first\", \"name_last\") VALUES (\"person_id_seq\".nextval, 'megumi', 'takamori')"
        elif sql.get_database_type() == "SQLServer":
            expected = "INSERT INTO [person] (\"name_first\", \"name_last\") VALUES ('megumi', 'takamori')"
        else:
            expected = "INSERT INTO \"person\" (\"name_first\", \"name_last\") VALUES ('megumi', 'takamori')"

        my.assertEquals( expected, statement )


    def _test_update_class(my):
        """test an update"""
        update = Update()
        update.set_table("person");
        update.set_value("name_first", "megumi");
        update.add_where("\"person_id\" = '1'");
        statement = update.get_statement()
        expected = "UPDATE \"person\" SET \"name_first\" = 'megumi' WHERE \"person_id\" = '1'"

        my.assertEqual( expected, statement )



    def _test_insert_and_delete(my):

        # ensure that we are *NOT* in a transaction
        Transaction.clear_stack()
        transaction = Transaction.get()
        # comment out for now
        #my.assertEquals( None, transaction )

        db_res = DbResource.get_default('unittest')
        sql = DbContainer.get(db_res)
        my.assertEquals( False, sql.is_in_transaction() )


        count_sql = """select count(*) from "person"
                    where "name_first" = 'Bugs' and "name_last" = 'Bunny'"""

        num_records = sql.get_int(count_sql)
        my.assertEquals(0, num_records)

        # test with no transaction
        transaction = Transaction.get(create=True)

        insert = Insert()
        insert.set_table("person")
        insert.set_value("name_first", "Bugs")
        insert.set_value("name_last", "Bunny")
        statement = insert.get_statement()
        expected = '''INSERT INTO "person" ("name_first", "name_last") VALUES ('Bugs', 'Bunny')'''
        my.assertEquals(expected, statement)

        # with a db_res added, it should scope the database
        insert = Insert()
        insert.set_database(db_res)
        insert.set_table("person")
        insert.set_value("name_first", "Bugs")
        insert.set_value("name_last", "Bunny")
        statement = insert.get_statement()
        expected = '''INSERT INTO %s"person" ("name_first", "name_last") VALUES ('Bugs', 'Bunny')''' % my.prefix
        my.assertEquals(expected, statement)



        sql.do_update(statement)

        num_records = sql.get_int(count_sql)
        my.assertEquals(1, num_records)

        delete = """delete from "person"
                 where "name_first" = 'Bugs' and "name_last" = 'Bunny'"""
        sql.do_update(delete)

        num_records = sql.get_int(count_sql)
        my.assertEquals(0, num_records)

        transaction.rollback()



    def _test_create_table(my):

        create = CreateTable()
        create.set_table("coffee")

        create.add_column("id", "int4")
        create.add_column("type", "varchar(10)")
        create.add_column("login", "varchar(30)")
        create.add_column("discussion", "text")

        create.set_primary_key("id")

        statement = create.get_statement()
        db_res = DbResource.get_default('unittest')
        sql = DbContainer.get(db_res)
        if sql.get_database_type() == "Oracle":
            expected = \
'''CREATE TABLE "coffee" (
    "id" NUMBER,
    "type" VARCHAR2(10),
    "login" VARCHAR2(30),
    "discussion" CLOB,
    PRIMARY KEY ("id")
);'''
        else:
            expected = \
'''CREATE TABLE "coffee" (
    "id" int4,
    "type" varchar(10),
    "login" varchar(30),
    "discussion" text,
    PRIMARY KEY ("id"));'''



        statement = statement.replace("\n", "")
        statement = statement.replace("    ", " ")
        statement = statement.replace("\t", " ")
        expected = expected.replace("\n", "")
        statement = expected.replace("    ", " ")
        statement = expected.replace("\t", " ")

        my.assertEquals(expected, statement)




    def _test_transaction(my):
        """test a transaction"""

        database_type = Project.get_by_code("unittest").get_database_type()
        if database_type == "MySQL":
            print
            print "WARNING: !!!!!!!"
            print "_test_tranaction is disabled"
            print "WARNING: !!!!!!!"
            print
            return


        db_res = DbResource.get_default('unittest')
        sql = DbContainer.get(db_res)

        count_sql = 'select count(*) from "person"'

        num_records = sql.get_int(count_sql)

        # start the transaction, update and roll back
        sql.start()


        insert = Insert()
        insert.set_table("person")
        insert.set_value("name_first", "cow")
        insert.set_value("name_last", "sql")
        query = insert.get_statement()

        sql.do_update(query)
        new_num_records = sql.get_value(count_sql)
        my.assertEquals( new_num_records, num_records+1 )
        sql.rollback()

        # dump after the rollback
        new_num_records = sql.get_int(count_sql)
        my.assertEqual( new_num_records, num_records )



    def _test_order_by(my):
        

        select = Select()
        db_res = DbResource.get_default('unittest')
        select.set_database(db_res)
        select.add_table("asset")
        select.add_enum_order_by("code", ['cow', 'dog', 'horse'])

        expected = '''SELECT %s"asset".* FROM %s"asset" ORDER BY ( CASE "code"
WHEN 'cow' THEN 1 
WHEN 'dog' THEN 2 
WHEN 'horse' THEN 3 
ELSE 4 END )''' % (my.prefix, my.prefix)

        statement = select.get_statement()

        my.assertEqual(expected, statement)




    def _test_rpn_filters(my):
        select = Select()
        db_res = DbResource.get_default('unittest')
        select.set_database(db_res)
        select.add_table("asset")
        select.add_where("begin")
        select.add_where("\"code\" = 'chr001'")
        select.add_where("\"code\" = 'chr002'")
        select.add_where("\"code\" = 'chr003'")
        select.add_where("or")
        select.add_where("\"status\" = 'complete'")
        select.add_where("and")
        statement = select.get_statement()

        expected = """SELECT %s"asset".* FROM %s"asset" WHERE ( "code" = 'chr001' OR "code" = 'chr002' OR "code" = 'chr003' ) AND "status" = 'complete'""" % (my.prefix, my.prefix)
        my.assertEquals(expected, statement)



        # test some simple fringe cases
        select = Select()
        select.add_table("asset")
        select.add_where("begin")
        select.add_where("or")
        select.add_where("\"status\" = 'complete'")
        select.add_where("and")
        statement = select.get_statement()
        expected = """SELECT "asset".* FROM "asset" WHERE "status" = 'complete'"""
        my.assertEquals(expected, statement)

 

        # assumed begin
        select = Select()
        select.add_table("asset")
        select.add_where("\"status\" = 'retired'")
        select.add_where("\"code\" = 'chr001'")
        select.add_where("\"code\" = 'chr002'")
        select.add_where("or")
        statement = select.get_statement()
        expected = """SELECT "asset".* FROM "asset" WHERE "status" = 'retired' OR "code" = 'chr001' OR "code" = 'chr002'"""
        my.assertEquals(expected, statement)



        # add a more complex case
        search = Select()
        search.add_table("person")
        search.add_where("begin")
        search.add_where("begin")
        search.add_filter("login", "joe")
        search.add_filter("login", "mary")
        search.add_where("and")
        search.add_where("begin")
        search.add_filter("attr", "tom")
        search.add_filter("attr", "peter")
        search.add_where("and")

        search.add_where("or")
        statement = search.get_statement()
        expected = '''SELECT "person".* FROM "person" WHERE ( "person"."login" = 'joe' AND "person"."login" = 'mary' ) OR ( "person"."attr" = 'tom' AND "person"."attr" = 'peter' )'''

        my.assertEquals(expected, statement)


        # try to throw in an extra begin in the middle
        project_code = "unittest"
        filter_search_type = "unittest/city"
        search_type = 'sthpw/sobject_list'
        search = Search(search_type)
        search.add_filter("project_code", project_code)
        search.add_filter("search_type", filter_search_type)
        
        search.add_op("begin")
        values = ["chr001"]
        columns = ['keywords']
        for column in columns:
            search.add_startswith_keyword_filter(column, values) 

        statement = search.get_statement()
        expected = '''SELECT %s"sobject_list".* FROM %s"sobject_list" WHERE "sobject_list"."project_code" = 'unittest' AND "sobject_list"."search_type" = 'unittest/city' AND ( lower("sobject_list"."keywords") like lower('%% chr001%%') OR lower("sobject_list"."keywords") like lower('chr001%%') )''' % (my.sthpw_prefix, my.sthpw_prefix)
        my.assertEquals(expected, statement)

    def _test_search_filter(my):

        select = Select()
        db_res = DbResource.get_default('unittest')
        select.set_database(db_res)
        select.add_table("job")
        select.add_column("request_id")
        select.add_filter("code", "123MMS")

        select2 = Select()
        #db_res = DbResource.get_default('unittest')
        select2.set_database(db_res)
        select2.add_table("request")
        select2.add_select_filter("id", select)
        statement = select2.get_statement()
        expected = '''SELECT %s"request".* FROM %s"request" WHERE "request"."id" in ( SELECT %s"job"."request_id" FROM %s"job" WHERE "job"."code" = '123MMS' )''' % (my.prefix, my.prefix, my.prefix, my.prefix)
        my.assertEquals(expected, statement)

        select3 = Select()
        select3.set_database(db_res)
        select3.add_op("begin")
        select3.add_table("request")
        select3.add_select_filter("id", select)

        statement = select3.get_statement()
        expected = '''SELECT %s"request".* FROM %s"request" WHERE "request"."id" in ( SELECT %s"job"."request_id" FROM %s"job" WHERE "job"."code" = '123MMS' )''' % (my.prefix, my.prefix, my.prefix, my.prefix)
        my.assertEquals(expected, statement)
 
    def _test_add_drop_column(my):
        #Project.set_project('unittest')
        from pyasm.command import ColumnAddCmd, ColumnDropCmd, Command
        cmd = ColumnAddCmd('unittest/country','special_place','varchar(256)')
        Command.execute_cmd(cmd)
        search_type = 'unittest/country'

        # clear cache
       
        SearchType.clear_column_cache(search_type)

        DatabaseImpl.clear_table_cache()
        exists = SearchType.column_exists(search_type, 'special_place')
        my.assertEquals(exists, True)

        # now drop the column
        cmd = ColumnDropCmd(search_type,'special_place')
        Command.execute_cmd(cmd)

        # clear cache
        SearchType.clear_column_cache(search_type)
        cache_dict = Container.get("DatabaseImpl:column_info")

       
        # assume database is the same as sthpw
        database_type = Project.get_by_code("unittest").get_database_type()
        db_resource = DbResource.get_default('unittest')
        table_info = cache_dict.get("%s:%s" % (db_resource, "country"))
        my.assertEquals(table_info == None, True)


        key = "%s:%s" % (db_resource, "country")
        cache_dict[key] = None
        exists = SearchType.column_exists(search_type, 'special_place')
        my.assertEquals(exists, False)

    def _test_join(my):
        """ test a select """
        Project.set_project('unittest')
        select = Select()
        db_res = DbResource.get_default('unittest')
        select.set_database(db_res)
        select.add_table("person")
        select.add_join('person','city', 'city_code','code')
        select.add_join('city','country', 'country_code','code')
        select.add_order_by("name_last")

        statement = select.get_statement()
        my.assertEquals(statement, '''SELECT %s"person".* FROM %s"person" LEFT OUTER JOIN %s"city" ON "person"."city_code" = "city"."code" LEFT OUTER JOIN %s"country" ON "city"."country_code" = "country"."code" ORDER BY "person"."name_last"''' % (my.prefix, my.prefix, my.prefix, my.prefix) )


        search = Search('unittest/person')
        search.add_join('unittest/city', 'unittest/person')
        statement = search.get_statement()
        my.assertEquals(statement, '''SELECT %s"person".* FROM %s"person" LEFT OUTER JOIN %s"city" ON "person"."city_code" = "city"."code"''' % (my.prefix,my.prefix, my.prefix))

        statement = search.get_statement()
        # this one has no schema connection, so will be ignored
        search.add_join('sthpw/login', 'unittest/person')
        my.assertEquals(statement, '''SELECT %s"person".* FROM %s"person" LEFT OUTER JOIN %s"city" ON "person"."city_code" = "city"."code"''' % (my.prefix, my.prefix, my.prefix))

        search.add_join('unittest/country', 'unittest/city')
        statement = search.get_statement()
        my.assertEquals(statement, '''SELECT %s"person".* FROM %s"person" LEFT OUTER JOIN %s"city" ON "person"."city_code" = "city"."code" LEFT OUTER JOIN %s"country" ON "city"."country_code" = "country"."code"''' % (my.prefix, my.prefix, my.prefix, my.prefix) )



    
if __name__ == "__main__":
    Batch()
    unittest.main()

