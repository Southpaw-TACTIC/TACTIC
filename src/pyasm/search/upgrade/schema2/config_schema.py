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

__all__ = ['ConfigSchema']

import tacticenv
import inspect

from pyasm.security import Batch
from pyasm.search import DbContainer, CreateTable, SearchType

class ConfigSchema(object):

    def create(my, project_code):

        my.sql = DbContainer.get(project_code)

        members = inspect.getmembers(my.__class__, predicate=inspect.ismethod)
        methods = []
        for name, member in members:
            if name.startswith('create_'):
                methods.append((name, member))

        methods.sort()
        for name, method in methods:
            print name
            method(my)


    #
    # Tables
    #



    def create_client_trigger(my):
        table = CreateTable()
        table.set_table("spt_client_trigger")
        table.add("id",             "serial", not_null=True )
        table.add("code",           "varchar" )
        table.add("event",          "varchar" )
        table.add("callback",       "varchar" )
        table.add("description",    "text" )
        table.add("timestamp",      "timestamp" )
        table.add("s_status",       "varchar", length=32 )
        table.set_primary_key("id")
        table.commit(my.sql)

        try:
            sobject = SearchType.create("sthpw/search_object")
            sobject.set_value("search_type", "config/client_trigger")
            sobject.set_value("namespace", "config")
            sobject.set_value("description", "Client Trigger")
            sobject.set_value("database", "{project}")
            sobject.set_value("table_name", "spt_client_trigger")
            sobject.set_value("class_name", "pyasm.search.SObject")
            sobject.set_value("title", "Client Trigger")
            sobject.set_value("schema", "public")
            sobject.commit()
        except Exception, e:
            print "WARNING: ", str(e)


    '''
    CREATE TABLE spt_plugin (
        id serial PRIMARY KEY,
        code varchar(256),
        description text,
        manifest text,
        timestamp timestamp,
        s_status varchar(256)
    );
    '''
    def create_plugin(my):
        table = CreateTable()
        table.set_table("spt_plugin")
        table.add("id",             "serial", not_null=True )
        table.add("code",           "varchar" )
        table.add("version",        "varchar" )
        table.add("description",    "varchar", length=2048 )
        table.add("manifest",       "text" )
        table.add("timestamp",      "timestamp" )
        table.add("s_status",       "varchar", length=32 )
        table.set_primary_key("id")
        table.commit(my.sql)

        try:
            sobject = SearchType.create("sthpw/search_object")
            sobject.set_value("search_type", "config/plugin")
            sobject.set_value("namespace", "config")
            sobject.set_value("description", "Plugin")
            sobject.set_value("database", "{project}")
            sobject.set_value("table_name", "spt_plugin")
            sobject.set_value("class_name", "pyasm.search.SObject")
            sobject.set_value("title", "Plugin")
            sobject.set_value("schema", "public")
            sobject.commit()
        except Exception, e:
            print "WARNING: ", str(e)




    '''
    CREATE TABLE custom_property (
        id integer NOT NULL,
        search_type character varying(256),
        name character varying(256),
        description text,
        "login" character varying(256)
    );
    '''
    def create_custom_property(my):
        table = CreateTable()
        table.set_table("custom_property")
        table.add("id",             "serial", not_null=True )
        table.add("search_type",    "varchar" )
        table.add("name",           "varchar" )
        table.add("description",    "varchar", length=2048 )
        table.add("login",          "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (120, 'prod/custom_property', 'sthpw', 'Custom Property', '{project}', 'custom_property', 'pyasm.search.SObject', 'Custom Property', 'public');
        '''



    '''
    CREATE TABLE custom_script (
        id serial PRIMARY KEY,
        code varchar(256),
        title varchar(256),
        description text,
        folder varchar(1024),
        script text,
        login varchar(256),
        timestamp timestamp,
        s_status varchar(256)
    );
    '''
    def create_custom_script(my):
        table = CreateTable()
        table.set_table("custom_script")
        table.add("id",             "serial", not_null=True )
        table.add("code",           "varchar" )
        table.add("title",          "varchar" )
        table.add("description",    "text" )
        table.add("folder",         "varchar", length=1024 )
        table.add("script",         "text" )
        table.add("login",          "varchar" )
        table.add("timestamp",      "timestamp" )
        table.add("s_status",       "varchar", length=32 )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (136, 'config/custom_script', 'sthpw', 'Custom Script', '{project}', 'custom_script', 'pyasm.search.SObject', 'Custom Script', 'public'); 
        '''


    '''
    CREATE TABLE naming (
        id integer NOT NULL,
        search_type character varying(100),
        dir_naming text,
        file_naming text,
        sandbox_naming text,
        snapshot_type character varying(256),
        context character varying(256),
        latest_versionless boolean,
        current_versionless boolean
    );
    '''
    def create_naming(my):
        table = CreateTable()
        table.set_table("naming")
        table.add("id",             "serial", not_null=True )
        table.add("search_type",    "varchar" )
        table.add("dir_naming",     "text" )
        table.add("file_naming",    "text" )
        table.add("sandbox_dir_naming", "text" )
        table.add("snapshot_type",  "varchar" )
        table.add("context",        "varchar" )
        table.add("latest_versionless", "boolean" )
        table.add("current_versionless","boolean" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (103, 'config/naming', 'config', 'Naming', '{project}', '{public}.naming', 'pyasm.biz.Naming', '', 'public');
        '''



    '''
    CREATE TABLE prod_setting (
        id integer NOT NULL,
        "key" character varying(100),
        value text,
        description text,
        "type" character varying(30),
        search_type character varying(200)
    );
    '''
    def create_prod_setting(my):
        table = CreateTable()
        table.set_table("prod_setting")
        table.add("id",             "serial", not_null=True )
        table.add("key",            "varchar" )
        table.add("value",          "text" )
        table.add("description",    "text" )
        table.add("type",           "varchar" )
        table.add("search_type",    "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (68, 'prod/prod_setting', 'prod', 'Production Settings', '{project}', 'prod_setting', 'pyasm.prod.biz.ProdSetting', 'Production Settings', 'public');
        '''




    def create_url(my):
        table = CreateTable()
        table.set_table("spt_url")
        table.add("id",             "serial", not_null=True )
        table.add("code",           "varchar" )
        table.add("url",            "text" )
        #table.add("class_name",     "varchar" )
        #table.add("args",           "text" )
        table.add("widget",         "text" )
        table.add("description",    "text" )
        table.add("timestamp",      "timestamp" )
        table.add("s_status",       "varchar", length=32 )
        table.set_primary_key("id")
        table.commit(my.sql)

        try:
            sobject = SearchType.create("sthpw/search_object")
            sobject.set_value("search_type", "config/url")
            sobject.set_value("namespace", "config")
            sobject.set_value("description", "Custom URL")
            sobject.set_value("database", "{project}")
            sobject.set_value("table_name", "spt_url")
            sobject.set_value("class_name", "pyasm.search.SObject")
            sobject.set_value("title", "Custom URL")
            sobject.set_value("schema", "public")
            sobject.commit()
        except Exception, e:
            print "WARNING: ", str(e)


    '''
    CREATE TABLE widget_config (
        id serial,
        code character varying(256),
        "view" character varying(256),
        category character varying(256),
        search_type character varying(256),
        "login" character varying(256),
        config text,
        "timestamp" timestamp without time zone DEFAULT now(),
        s_status character varying(32),
        PRIMARY KEY (id)
    );
    '''
    def create_widget_config(my):
        table = CreateTable()
        table.set_table("widget_config")
        table.add("id",             "serial", not_null=True )
        table.add("code",           "varchar" )
        table.add("view",           "varchar" )
        table.add("category",       "varchar" )
        table.add("search_type",    "varchar" )
        table.add("login",          "varchar" )
        table.add("config",         "text" )
        table.add("timestamp",      "timestamp" )
        table.add("s_status",       "varchar", length=32 )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (133, 'config/widget_config', 'config', 'Widget Config', '{project}', 'widget_config', 'pyasm.search.WidgetDbConfig', 'Widget Config', 'public');
        '''



    def create_process(my):
        table = CreateTable()
        table.set_table("spt_process")
        table.add("id",             "serial", not_null=True )
        table.add("code",           "varchar" )
        table.add("pipeline_code",  "varchar" )
        table.add("process",        "varchar" )
        table.add("sort_order",     "integer" )
        table.add("timestamp",      "timestamp" )
        table.add("s_status",       "varchar", length=32 )
        table.set_primary_key("id")
        table.commit(my.sql)

        try:
            sobject = SearchType.create("sthpw/search_object")
            sobject.set_value("search_type", "config/process")
            sobject.set_value("namespace", "config")
            sobject.set_value("description", "Process")
            sobject.set_value("database", "{project}")
            sobject.set_value("table_name", "spt_process")
            sobject.set_value("class_name", "pyasm.search.SObject")
            sobject.set_value("title", "Process")
            sobject.set_value("schema", "public")
            sobject.commit()
        except Exception, e:
            print "WARNING: ", str(e)


    def create_trigger(my):
        table = CreateTable()
        table.set_table("spt_trigger")
        table.add("id",                 "int", not_null=True )
        table.add("class_name",         "varchar")
        table.add("script_path",        "varchar")
        table.add("description",        "text")
        table.add("event",              "varchar")
        table.add("mode",               "varchar")
        table.add("s_status",           "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (29, 'config/trigger', '{project}', 'Triggers', 'sthpw', 'spt_trigger', 'pyasm.biz.TriggerSObj', 'Triggers', 'public')
        '''
        try:
            sobject = SearchType.create("sthpw/search_object")
            sobject.set_value("search_type", "config/trigger")
            sobject.set_value("namespace", "config")
            sobject.set_value("description", "Trigger")
            sobject.set_value("database", "{project}")
            sobject.set_value("table_name", "spt_trigger")
            sobject.set_value("class_name", "pyasm.search.SObject")
            sobject.set_value("title", "Trigger")
            sobject.set_value("schema", "public")
            sobject.commit()
        except Exception, e:
            print "WARNING: ", str(e)



if __name__ == '__main__':

    Batch(project_code='admin')

    import sys
    args = sys.argv[1:]
    executable = sys.argv[0]
    if not args:
        print
        print "Usage: python %s <database>" % executable
        print
        sys.exit(1)

    project_code = args[0]

    database = ConfigSchema()
    database.create(project_code)



