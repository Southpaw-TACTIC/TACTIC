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
# TODO: prod_setting , snapshot_type table
__all__ = ['UnittestSchema']

import tacticenv
import inspect

from pyasm.search import DbContainer, CreateTable

class UnittestSchema(object):
    
    def create(my):

        my.sql = DbContainer.get("unittest")

        members = inspect.getmembers(my.__class__, predicate=inspect.ismethod)
        methods = []
        for name, member in members:
            if name.startswith('create_'):
                methods.append((name, member))

        methods.sort()
        for name, method in methods:
            print name
            method(my)



    '''
    CREATE TABLE person (
        id serial NOT NULL,
        code character varying(256),
        name_first character varying(100),
        name_last character varying(100),
        nationality character varying(100),
        description text,
        picture text,
        discussion text,
        approval text,
        city_code character varying(256),
        metadata text,
        age integer,
        timestamp timestamp,
        birth_date timestamp
    );
    '''
    def create_person(my):
        table = CreateTable()
        table.set_table("person")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar")
        table.add("name_first",     "varchar")
        table.add("name_last",      "varchar")
        table.add("age",            "int")
        table.add("nationality",    "varchar")
        table.add("description",    "text")
        table.add("picture",        "text")
        table.add("discussion",     "text")
        table.add("approval",      "text")
        table.add("city_code",      "varchar")
        table.add("metadata",       "varchar")
        table.add("timestamp",      "timestamp")
        table.add("birth_date",     "timestamp")
        table.add("pipeline_code",      "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (123, 'unittest/person', 'unittest', 'Unittest Person', 'unittest', 'person', 'pyasm.search.SObject', 'Unittest Person', 'public')
        '''


    '''
    CREATE TABLE city (
        id serial NOT NULL,
        code character varying(256),
        name character varying(256),
        country_code character varying(256),
        s_status character varying(32)
    );
    '''
    def create_city(my):
        table = CreateTable()
        table.set_table("city")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar")
        table.add("name",           "varchar")
        table.add("country_code",   "varchar")
        table.add("s_status",       "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (125, 'unittest/city', 'unittest', 'Unittest City', 'unittest', 'city', 'pyasm.search.SObject', 'Unittest City', 'public');
        '''






    '''
    CREATE TABLE country (
        id serial NOT NULL,
        code character varying(256),
        name character varying(256),
        s_status character varying(32)
    );
    '''
    def create_country(my):
        table = CreateTable()
        table.set_table("country")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar")
        table.add("name",           "varchar")
        table.add("s_status",       "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (126, 'unittest/country', 'unittest', 'Unittest Country', 'unittest', 'country', 'pyasm.search.SObject', 'Unittest Country', 'public');
        '''




    '''
    CREATE TABLE session_contents (
        id serial NOT NULL,
        "login" character varying(100) NOT NULL,
        pid integer NOT NULL,
        data text,
        "session" text,
        "timestamp" timestamp without time zone DEFAULT now()
    );
    '''
    def create_session_contents(my):
        table = CreateTable()
        table.set_table("session_contents")
        table.add("id",             "int", not_null=True )
        table.add("login",          "varchar")
        table.add("pid",            "int")
        table.add("data",           "text")
        table.add("session",        "varchar")
        table.add("timestamp",      "timestamp")
        table.set_primary_key("id")
        table.commit(my.sql)




    '''
    CREATE TABLE status (
        id serial NOT NULL,
        status text,
        "timestamp" timestamp without time zone DEFAULT now(),
        name character varying(128)
    );
    '''
    def create_status(my):
        table = CreateTable()
        table.set_table("status")
        table.add("id",             "int", not_null=True )
        table.add("status",         "varchar")
        table.add("timestamp",      "timestamp")
        table.add("name",           "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)


if __name__ == '__main__':
    database = UnittestSchema()
    database.create()



