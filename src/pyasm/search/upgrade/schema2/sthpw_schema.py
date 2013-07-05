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

import inspect

from pyasm.search import CreateTable, DbContainer


class Column(object):
    def __init__(my):
        print my


class DatabaseIndex(Column):
    def __init__(my):
        Column.__init__(my)


class StringCol(Column):
    def __init__(my, length=None, default=None):
        Column.__init__(my)


class DateTimeCol(Column):
    def __init__(my):
        Column.__init__(my)



class SthpwSchema(object):

    def create(my):

        my.sql = DbContainer.get("sthpw")

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
    CREATE TABLE access_rule (
        id integer NOT NULL,
        project_code character varying(256),
        code character varying(256),
        description text,
        "rule" text,
        "timestamp" timestamp without time zone DEFAULT now()
    );
    '''
    def create_access_rule(my):
        table = CreateTable()
        table.set_table("access_rule")
        table.add("id",              "int", not_null=True )
        table.add("code",            "varchar")
        table.add("project_code",    "varchar")
        table.add("description",     "text")
        table.add("rule",            "text")
        table.add("timestamp",       "timestamp")
        table.set_primary_key("id")
        table.commit(my.sql)


    '''
    CREATE TABLE access_rule_in_group (
        id integer NOT NULL,
        login_group character varying(256),
        access_rule_code character varying(256),
        "timestamp" timestamp without time zone DEFAULT now()
    );
    '''
    def create_access_rule_in_group(my):
        table = CreateTable()
        table.set_table("access_rule_in_group")
        table.add("id",              "int", not_null=True )
        table.add("login_group",     "varchar")
        table.add("access_rule_code","varchar")
        table.add("timestamp",       "timestamp")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (82, 'sthpw/access_rule_in_group', 'sthpw', 'Access Rules In Group', 'sthpw', '{public}.access_rule_in_group', 'pyasm.security.AccessRuleInGroup', '', 'public');
        '''


    '''
    CREATE TABLE annotation (
        id integer NOT NULL,
        xpos integer NOT NULL,
        ypos integer NOT NULL,
        message text,
        "login" character varying(100) NOT NULL,
        "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
        file_code character varying(30)
    );
    '''
    def create_annotation(my):
        table = CreateTable()
        table.set_table("annotation")
        table.add("id",             "int", not_null=True )
        table.add("xpos",           "varchar")
        table.add("ypos",           "varchar")
        table.add("message",        "text")
        table.add("login",          "varchar")
        table.add("timestamp",      "timestamp")
        table.add("file_code",      "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (1, 'sthpw/annotation', 'sthpw', 'Image Annotations', 'sthpw', 'annotation', 'pyasm.search.search.SObject', 'Image Annotations', 'public');
        '''



    '''
    CREATE TABLE clipboard (
        id integer NOT NULL,
        project_code character varying(256),
        "login" character varying(256),
        search_type character varying(256),
        search_id integer,
        "timestamp" timestamp without time zone DEFAULT now(),
        category character varying(256)
    );
    '''
    def create_clipboard(my):
        table = CreateTable()
        table.set_table("clipboard")
        table.add("id",             "int", not_null=True )
        table.add("project",        "varchar")
        table.add("login",          "varchar")
        table.add("search_type",    "text")
        table.add("search_id",      "int")
        table.add("timestamp",      "timestamp")
        table.add("category",       "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (83, 'sthpw/clipboard', 'sthpw', 'Clipboard', 'sthpw', '{public}.clipboard', 'pyasm.biz.Clipboard', '', 'public');
        '''


    def create_cache(my):
        table = CreateTable()
        table.set_table("cache")
        table.add("id",             "int", not_null=True )
        table.add("key",            "varchar")
        table.add("mtime",          "timestamp")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ("search_object_id_seq".nextval, 'sthpw/cache', 'sthpw', 'Cache', 'sthpw', '{public}.cache', 'pyasm.search.SObject', '', 'public');
        '''

    '''
    CREATE TABLE "connection" (
        id integer NOT NULL,
        context character varying(60),
        project_code character varying(30),
        src_search_type character varying(200),
        src_search_id integer,
        dst_search_type character varying(200),
        dst_search_id integer,
        "login" character varying(30),
        "timestamp" timestamp without time zone DEFAULT now()
    );
    '''
    def create_connection(my):
        table = CreateTable()
        table.set_table("connection")
        table.add("id",             "int", not_null=True )
        table.add("context",        "varchar")
        table.add("project",        "varchar")
        table.add("src_search_type",    "varchar")
        table.add("src_search_id",      "int")
        table.add("dst_search_type",    "varchar")
        table.add("dst_search_id",      "int")
        table.add("login",          "varchar")
        table.add("timestamp",      "timestamp")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (34, 'sthpw/connection', 'sthpw', 'Connections', 'sthpw', 'connection', 'pyasm.biz.SObjectConnection', 'Connections', NULL);
        '''


    '''
    CREATE TABLE debug_log (
        id integer NOT NULL,
        category character varying(256),
        "level" character varying(256),
        message text,
        "timestamp" timestamp without time zone DEFAULT now(),
        "login" character varying(256),
        s_status character varying(30)
    );
    '''
    def create_debug_log(my):
        table = CreateTable()
        table.set_table("debug_log")
        table.add("id",             "int", not_null=True )
        table.add("category",       "varchar")
        table.add("level",          "varchar")
        table.add("message",        "text")
        table.add("timestamp",      "timestamp")
        table.add("login",          "varchar")
        table.add("s_status",       "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (121, 'sthpw/debug_log', 'sthpw', 'Debug Log', 'sthpw', 'debug_log', 'pyasm.biz.DebugLog', 'Debug Log', 'public');
        '''



    '''
    CREATE TABLE exception_log (
        id integer NOT NULL,
        "class" character varying(100),
        message text,
        stack_trace text,
        "login" character varying(100) NOT NULL,
        "timestamp" timestamp without time zone DEFAULT now() NOT NULL
    );
    '''
    def create_exception_log(my):
        table = CreateTable()
        table.set_table("exception_log")
        table.add("id",             "int", not_null=True )
        table.add("class",          "varchar")
        table.add("message",        "text")
        table.add("stack_trace",    "text")
        table.add("login",          "varchar")
        table.add("timestamp",      "timestamp")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (8, 'sthpw/exception_log', 'sthpw', 'Exception Log', 'sthpw', 'exception_log', 'pyasm.search.SObject', 'Exception Log', 'public');
        '''





    '''
    CREATE TABLE file (
        id integer NOT NULL,
        file_name character varying(512) NOT NULL,
        search_type character varying(100) NOT NULL,
        search_id integer NOT NULL,
        "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
        st_size bigint,
        file_range text,
        code character varying(30),
        snapshot_code character varying(30),
        project_code character varying(100),
        md5 character varying(32),
        checkin_dir text,
        source_path text,
        relative_dir text,
        type character varying(256)
    );
    '''
    def create_file(my):
        table = CreateTable()
        table.set_table("file")
        table.add("id",             "int", not_null=True )
        table.add("file_name",      "varchar", length=512)
        table.add("search_type",    "varchar")
        table.add("search_id",      "int")
        table.add("timestamp",      "timestamp")
        table.add("st_size",        "int")
        table.add("file_range",     "varchar")
        table.add("code",           "varchar")
        table.add("type",           "varchar")
        table.add("base_type",      "varchar")
        table.add("snapshot_code",  "varchar")
        table.add("project_code",   "varchar")
        table.add("md5",            "varchar")
        table.add("checkin_dir",    "varchar", length=2048)
        table.add("source_path",    "varchar", length=2048)
        table.add("relative_dir",   "varchar", length=2048)
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (1, 'sthpw/file', 'sthpw', 'A record of all files that are tracked', 'sthpw', 'file', 'pyasm.biz.file.File', 'File', 'public');
        '''


    '''
    CREATE TABLE group_notification (
        id integer NOT NULL,
        login_group character varying(100) NOT NULL,
        notification_id integer NOT NULL
    );
    '''
    def create_group_notification(my):
        table = CreateTable()
        table.set_table("group_notification")
        table.add("id",             "int", not_null=True )
        table.add("login_group",    "varchar", length=512)
        table.add("notification_id","varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ("search_object_id_seq".nextval, 'sthpw/group_notification', 'sthpw', 'Associate one of more kinds of notification with groups', 'sthpw', 'group_notification', 'pyasm.biz.GroupNotification', 'Group Notification', 'public');
        '''


    '''
    CREATE TABLE notification_log (
        id integer NOT NULL,
        project_code character varying(256),
        "login" character varying(256),
        command_cls character varying(256),
        subject text,
        message text,
        "timestamp" timestamp without time zone DEFAULT now()
    );
    '''
    def create_notification_log(my):
        table = CreateTable()
        table.set_table("notification_log")
        table.add("id",             "int", not_null=True )
        table.add("project_code",   "varchar")
        table.add("login",          "varchar")
        table.add("command_cls",    "varchar")
        table.add("subject",        "varchar")
        table.add("message",         "text")
        table.add("timestamp",      "timestamp")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ("search_object_id_seq".nextval, 'sthpw/notification_log', 'sthpw', 'Notification Log', 'sthpw', '{public}.notification_log', 'pyasm.search.SObject', '', 'public');
        '''


    '''
    CREATE TABLE "login" (
        id integer NOT NULL,
        "login" character varying(100) NOT NULL,
        "password" character varying(255) NOT NULL,
        login_groups text,
        first_name character varying(100),
        last_name character varying(100),
        email character varying(200),
        phone_number varying(32),
        department varying(256),
        namespace character varying(255),
        snapshot text,
        s_status character varying(30),
        project_code text
    );
    '''
    def create_login(my):
        table = CreateTable()
        table.set_table("login")
        table.add("id",             "int", not_null=True )
        table.add("login",          "varchar", not_null=True)
        table.add("password",       "varchar")
        table.add("login_groups",   "text")
        table.add("first_name",     "varchar")
        table.add("last_name",      "varchar")
        table.add("email",          "varchar")
        table.add("phone_number",   "varchar")
        table.add("department",     "varchar")
        table.add("namespace",      "varchar")
        table.add("project_code",   "text")
        table.add("license_type",   "varchar")
        table.add("s_status",       "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)

        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (9, 'sthpw/login', 'sthpw', 'List of users', 'sthpw', 'login', 'pyasm.security.Login', 'Users', 'public');
        '''

    '''
    CREATE TABLE login_group (
        id integer NOT NULL,
        login_group character varying(100) NOT NULL,
        sub_groups text,
        access_rules text,
        redirect_url text,
        namespace character varying(255),
        description text,
        project_code text,
        s_status character varying(256)
    );
    '''
    def create_login_group(my):
        table = CreateTable()
        table.set_table("login_group")
        table.add("id",             "int", not_null=True )
        table.add("login_group",    "varchar", not_null=True)
        table.add("sub_groups",     "text")
        table.add("access_rules",   "text")
        #table.add("redirect_url",   "text")
        table.add("namespace",      "varchar")
        table.add("description",    "text")
        table.add("project_code",   "text")
        table.add("s_status",       "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)

        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (11, 'sthpw/login_group', 'sthpw', 'List of groups that user belong to', 'sthpw', 'login_group', 'pyasm.security.LoginGroup', 'Groups', 'public');
        '''


    '''
    CREATE TABLE login_in_group (
        id integer NOT NULL,
        "login" character varying(100) NOT NULL,
        login_group character varying(100) NOT NULL
    );
    '''
    def create_login_in_group(my):
        table = CreateTable()
        table.set_table("login_in_group")
        table.add("id",             "int", not_null=True )
        table.add("login",          "varchar", not_null=True)
        table.add("login_group",    "varchar", not_null=True)
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (7, 'sthpw/login_in_group', 'sthpw', 'Users in groups', 'sthpw', 'login_in_group', 'pyasm.security.LoginInGroup', 'Users in groups', 'public');
        '''



    '''
    CREATE TABLE milestone (
        id integer NOT NULL,
        code character varying(200),
        project_code character varying(30),
        description text,
        due_date timestamp without time zone
    );
    '''
    def create_milestone(my):
        table = CreateTable()
        table.set_table("milestone")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar", not_null=True)
        table.add("project_code",   "varchar")
        table.add("description",    "varchar")
        table.add("due_date",       "timestamp")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (31, 'sthpw/milestone', 'sthpw', 'Project Milestones', 'sthpw', 'milestone', 'pyasm.search.SObject', 'Project Milestones', 'public');
        '''


    '''
    CREATE TABLE note (
        id integer NOT NULL,
        project_code character varying(30),
        search_type character varying(200),
        search_id integer,
        "login" character varying(30),
        context character varying(60),
        "timestamp" timestamp without time zone DEFAULT now(),
        note text,
        title character varying(1024),
        parent_id bigint,
        status character varying(256),
        label character varying(256),
        process character varying(60)
    );
    '''
    def create_note(my):
        table = CreateTable()
        table.set_table("note")
        table.add("id",             "int", not_null=True )
        table.add("project_code",   "varchar")
        table.add("search_type",    "varchar")
        table.add("search_id",      "number")
        table.add("login",          "varchar")
        table.add("context",        "varchar")
        table.add("timestamp",      "timestamp")
        table.add("note",           "text")
        table.add("title",          "varchar")
        table.add("parent_id",      "number")
        table.add("status",         "varchar")
        table.add("label",          "varchar")
        table.add("process",        "varchar")
        table.add("sort_order",        "int")
        table.add("access",        "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (33, 'sthpw/note', 'sthpw', 'Notes', 'sthpw', 'note', 'pyasm.biz.Note', 'Notes', NULL);
        '''


    '''
    CREATE TABLE notification (
        id integer NOT NULL,
        code character varying(30) NOT NULL,
        description text,
        "type" character varying(30) NOT NULL,
        search_type character varying(100),
        project_code character varying(30),
        rules text,
        subject text,
        message text,
        email_handler_cls character varying(200)
    );
    '''
    def create_notification(my):
        table = CreateTable()
        table.set_table("notification")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar")
        table.add("event",          "varchar")
        table.add("description",    "varchar")
        table.add("type",           "varchar")
        table.add("search_type",    "varchar")
        table.add("project_code",   "varchar")
        table.add("rules",          "text")
        table.add("subject",        "text")
        table.add("message",        "text")
        table.add("email_handler_cls","varchar")
        table.add("mail_to",        "text")
        table.add("mail_cc",        "text")
        table.add("mail_bcc",       "text")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ("search_object_id_seq".nextval, 'sthpw/notification', 'sthpw', 'Different types of Notification', 'sthpw', 'notification', 'pyasm.biz.Notification', 'Notification', 'public');
        '''

    '''
    CREATE TABLE notification_login (
        id integer NOT NULL,
        notification_log_id integer,
        "login" character varying(256),
        "type" character varying(256),
        project_code character varying(256),
        "timestamp" timestamp without time zone DEFAULT now()
    );
    '''
    def create_notification_login(my):
        table = CreateTable()
        table.set_table("notification_login")
        table.add("id",             "int", not_null=True )
        table.add("notification_log_id","int")
        table.add("login",          "varchar")
        table.add("type",    "varchar")
        table.add("project_code",           "varchar")
        table.add("timestamp",    "timestamp")
        table.set_primary_key("id")
        table.commit(my.sql)
        ''' 
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ("search_object_id_seq".nextval, 'sthpw/notification_login', 'sthpw', 'Notification Login', 'sthpw', '{public}.notification_login', 'pyasm.search.SObject', '', 'public');
        '''



    '''
    CREATE TABLE pipeline (
        id integer NOT NULL,
        code character varying(128) NOT NULL,
        pipeline text,
        "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
        search_type character varying(100),
        project_code character varying(30),
        description text,
        s_status character varying(30)
    );
    '''
    def create_pipeline(my):
        table = CreateTable()
        table.set_table("pipeline")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar")
        table.add("pipeline",       "text")
        table.add("timestamp",      "timestamp")
        table.add("search_type",    "varchar")
        table.add("project_code",   "varchar")
        table.add("description",    "text")
        table.add("s_status",       "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (12, 'sthpw/pipeline', 'sthpw', 'List of piplines available for sobjects', 'sthpw', 'pipeline', 'pyasm.biz.Pipeline', 'Pipelines', 'public');
        '''


    '''
    CREATE TABLE pref_list (
        id integer NOT NULL,
        "key" character varying(256),
        description text,
        options text,
        "type" character varying(256),
        category character varying(256),
        "timestamp" timestamp without time zone DEFAULT now(),
        title text
    );
    '''
    def create_pref_list(my):
        table = CreateTable()
        table.set_table("pref_list")
        table.add("id",             "int", not_null=True )
        table.add("key",            "varchar")
        table.add("description",    "text")
        table.add("options",        "text")
        table.add("type",           "varchar")
        table.add("category",       "varchar")
        table.add("timestamp",      "timestamp")
        table.add("title",          "text")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (84, 'sthpw/pref_list', 'sthpw', 'Preferences List', 'sthpw', '{public}.pref_list', 'pyasm.biz.PrefList', '', 'public');
        '''
 

    '''
    CREATE TABLE pref_setting (
        id integer NOT NULL,
        project_code character varying(256),
        "login" character varying(256),
        "key" character varying(256),
        value text,
        "timestamp" timestamp without time zone DEFAULT now()
    );
    '''
    def create_pref_setting(my):
        table = CreateTable()
        table.set_table("pref_setting")
        table.add("id",             "int", not_null=True )
        table.add("project_code",   "varchar")
        table.add("login",          "varchar")
        table.add("key",            "varchar")
        table.add("value",          "text")
        table.add("timestamp",      "timestamp")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (80, 'sthpw/pref_setting', 'sthpw', 'Preference Setting', 'sthpw', '{public}.pref_setting', 'pyasm.biz.PrefSetting', '', 'public'); 
        '''


    '''
    CREATE TABLE project (
        id integer NOT NULL,
        code character varying(30) NOT NULL,
        title character varying(100),
        sobject_mapping_cls character varying(100),
        dir_naming_cls character varying(200),
        code_naming_cls character varying(200),
        pipeline character varying(30),
        snapshot text,
        "type" character varying(30),
        last_db_update timestamp without time zone,
        description text,
        initials character varying(30),
        file_naming_cls character varying(200),
        reg_hours numeric,
        node_naming_cls character varying(200),
        s_status character varying(30),
        status character varying(256),
        last_version_update character varying(256)
    );
    '''
    def create_project(my):
        table = CreateTable()
        table.set_table("project")
        table.add("id",                     "int", not_null=True )
        table.add("code",                   "varchar", not_null=True)
        table.add("title",                  "varchar")
        table.add("description",            "varchar")
        table.add("type",                   "varchar")
        table.add("initials",               "varchar")
        table.add("pipeline",               "varchar")
        table.add("sobject_mapping_cls",    "varchar")
        table.add("dir_naming_cls",         "varchar")
        table.add("code_naming_cls",        "varchar")
        table.add("file_naming_cls",        "varchar")
        table.add("node_naming_cls",        "varchar")
        table.add("last_db_update",         "timestamp")
        table.add("last_version_update",    "varchar")
        table.add("s_status",               "varchar")
        table.add("resource",               "text")
        #table.add("snapshot",               "text")
        #table.add("reg_hours",              "varchar")
        #table.add("status",                 "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (24, 'sthpw/project', 'sthpw', 'Projects', 'sthpw', 'project', 'pyasm.biz.Project', 'Projects', NULL)
        '''



    '''
    CREATE TABLE project_type (
        id integer NOT NULL,
        code character varying(30),
        dir_naming_cls character varying(200),
        file_naming_cls character varying(200),
        code_naming_cls character varying(200),
        node_naming_cls character varying(200),
        sobject_mapping_cls character varying(200),
        s_status character varying(32),
        "type" character varying(100) NOT NULL,
        repo_handler_cls character varying(200)
    );
    '''
    def create_project_type(my):
        table = CreateTable()
        table.set_table("project_type")
        table.add("id",             "int", not_null=True )
        table.add("code",          "varchar", not_null=True)
        table.add("dir_naming_cls",         "varchar")
        table.add("file_naming_cls",        "varchar")
        table.add("code_naming_cls",        "varchar")
        table.add("node_naming_cls",        "varchar")
        table.add("sobject_mapping_cls",    "varchar")
        table.add("repo_handler_cls",       "varchar")
        table.add("type",                   "varchar", not_null=True)
        table.add("s_status",               "varchar")

        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (79, 'sthpw/project_type', 'sthpw', 'Project Type', 'sthpw', 'project_type', 'pyasm.biz.ProjectType', 'Project Type', 'public')
        '''

    '''
    CREATE TABLE queue (
        id integer NOT NULL,
        queue character varying(30) NOT NULL,
        priority character varying(10) NOT NULL,
        description text,
        state character varying(30) DEFAULT 'pending'::character varying NOT NULL,
        "login" character varying(30) NOT NULL,
        "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
        command character varying(200) NOT NULL,
        serialized text NOT NULL,
        s_status character varying(30),
        project_code character varying(100),
        search_id integer,
        search_type character varying(100),
        dispatcher_id integer,
        policy_code character varying(30)
    );
    '''
    def create_queue(my):
        table = CreateTable()
        table.set_table("queue")
        table.add("id",             "int", not_null=True )
        table.add("queue",          "varchar", not_null=True)
        table.add("priority",       "varchar", not_null=True)
        table.add("description",    "text")
        table.add("state",          "varchar")
        table.add("login",          "varchar")
        table.add("timestamp",      "timestamp")
        table.add("command",        "varchar")
        table.add("serialized",     "text")
        table.add("s_status",       "varchar")
        table.add("project_code",   "varchar")
        table.add("search_id",      "int")
        table.add("search_type",    "varchar")
        table.add("dispatcher_id",  "int")
        table.add("policy_code",    "varchar")
        table.add("queue",          "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (21, 'sthpw/queue', 'sthpw', 'Tactic Dispatcher', 'sthpw', 'queue', 'pyasm.search.SObject', 'Tactic Dispatcher', NULL);
        '''

    '''
    CREATE TABLE remote_repo (
        id integer NOT NULL,
        code character varying(30),
        ip_address character varying(30),
        ip_mask character varying(30),
        repo_base_dir character varying(200),
        sandbox_base_dir character varying(200),
        "login" character varying(100)
    );
    '''
    def create_remote_repo(my):
        table = CreateTable()
        table.set_table("remote_repo")
        table.add("id",                 "int", not_null=True )
        table.add("code",               "varchar", not_null=True)
        table.add("ip_address",         "varchar")
        table.add("ip_mask",            "varchar")
        table.add("repo_base_dir",      "varchar", not_null=True)
        table.add("sandbox_base_dir",   "varchar")
        table.add("login",              "varchar", not_null=True)
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (32, 'sthpw/remote_repo', 'sthpw', 'Remote Repositories', 'sthpw', 'remote_repo', 'pyasm.biz.RemoteRepo', 'Remote Repositories', NULL);
        '''



    '''
    CREATE TABLE retire_log (
        id integer NOT NULL,
        search_type character varying(100),
        search_id character varying(100),
        "login" character varying(100) NOT NULL,
        "timestamp" timestamp without time zone DEFAULT now() NOT NULL
    );
    '''
    def create_retire_log(my):
        table = CreateTable()
        table.set_table("retire_log")
        table.add("id",                 "int", not_null=True )
        table.add("search_type",        "varchar")
        table.add("search_id",          "int")
        table.add("login",              "varchar", not_null=True)
        table.add("timestamp",          "timestamp")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (3, 'sthpw/retire_log', 'sthpw', 'Retire SObject log', 'sthpw', 'retire_log', 'pyasm.search.RetireLog', 'Retire SObject log', 'public');
        '''


    '''
    CREATE TABLE "schema" (
        id integer NOT NULL,
        code character varying(256),
        description text,
        "schema" text,
        "timestamp" timestamp without time zone DEFAULT now(),
        "login" character varying(256),
        s_status character varying(30)
    );
    '''
    def create_schema(my):
        table = CreateTable()
        table.set_table("schema")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar")
        table.add("description",    "text")
        table.add("schema",         "text")
        table.add("timestamp",      "timestamp")
        table.add("login",          "varchar")
        table.add("s_status",       "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (116, 'sthpw/schema', 'sthpw', 'Schema', 'sthpw', 'schema', 'pyasm.biz.Schema', 'Schema', 'public');
        '''

    '''
    CREATE TABLE status_log (
        id integer NOT NULL,
        search_type character varying(100) NOT NULL,
        search_id integer NOT NULL,
        status text,
        "login" character varying(100) NOT NULL,
        "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
        to_status character varying(256),
        from_status character varying(256),
        project_code character varying(256)
    );
    '''
    def create_status_log(my):
        table = CreateTable()
        table.set_table("status_log")
        table.add("id",             "int", not_null=True )
        table.add("search_type",    "varchar")
        table.add("search_id",      "int")
        table.add("status",         "text")
        table.add("login",          "varchar")
        table.add("timestamp",      "timestamp")
        table.add("s_status",       "varchar")
        table.add("from_status",    "varchar")
        table.add("to_status",      "varchar")
        table.add("project_code",   "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ("search_object_id_seq".nextval, 'sthpw/status_log', 'sthpw', 'Log of status changes', 'sthpw', 'status_log', 'pyasm.search.SObject', 'Status Log', 'public');
        '''



    '''
    CREATE TABLE search_object (
        id integer NOT NULL,
        search_type character varying(100) NOT NULL,
        namespace character varying(200) NOT NULL,
        description text,
        "database" character varying(100) NOT NULL,
        table_name character varying(100) NOT NULL,
        class_name character varying(100) NOT NULL,
        title character varying(100),
        "schema" character varying(100)
    );
    '''
    def create_search_object(my):
        table = CreateTable()
        table.set_table("search_object")
        table.add("id",             "int", not_null=True )
        table.add("search_type",    "varchar", not_null=True)
        table.add("namespace",      "varchar", not_null=True)
        table.add("description",    "text")
        table.add("database",       "varchar", not_null=True)
        table.add("table_name",     "varchar", not_null=True)
        table.add("class_name",     "varchar", not_null=True)
        table.add("title",          "varchar")
        table.add("schema",         "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (14, 'sthpw/search_object', 'sthpw', 'List of all the search objects', 'sthpw', 'search_object', 'pyasm.search.SearchType', 'Search Objects', 'public');
        '''




    '''
    CREATE TABLE snapshot (
        id integer NOT NULL,
        search_type character varying(100) NOT NULL,
        search_id integer NOT NULL,
        column_name character varying(100) NOT NULL,
        snapshot text NOT NULL,
        description text,
        "login" character varying(100) NOT NULL,
        "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
        context character varying(256),
        version integer,
        s_status character varying(30),
        snapshot_type character varying(30),
        code character varying(30),
        repo character varying(30),
        is_current boolean,
        label character varying(100),
        revision smallint,
        level_type character varying(256),
        level_id integer,
        metadata text,
        is_latest boolean,
        status character varying(256),
        project_code character varying(256),
        search_code character varying(256)
    );
    '''
    def create_snapshot(my):
        table = CreateTable()
        table.set_table("snapshot")
        table.add("id",             "int", not_null=True )
        table.add("search_type",    "varchar", not_null=True)
        table.add("search_id",      "int", not_null=True)
        table.add("column_name",    "varchar", not_null=True)
        table.add("snapshot",       "text", not_null=True)
        table.add("description",    "text", not_null=True)
        table.add("login",          "varchar", not_null=True)
        table.add("timestamp",      "timestamp", not_null=True)
        table.add("context",        "varchar", not_null=True)
        table.add("version",        "int", not_null=True)
        table.add("s_status",       "varchar")
        table.add("snapshot_type",  "varchar")
        table.add("code",           "varchar")
        table.add("repo",           "varchar")
        table.add("is_current",     "boolean")
        table.add("label",          "varchar")
        table.add("revision",       "int")
        table.add("level_type",     "varchar")
        table.add("level_id",       "int")
        table.add("metadata",       "text")
        table.add("is_latest",      "boolean")
        table.add("is_synced",      "boolean")
        table.add("status",         "varchar")
        table.add("project_code",   "varchar")
        table.add("search_code",    "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (13, 'sthpw/snapshot', 'sthpw', 'All versions of snapshots of assets', 'sthpw', 'snapshot', 'pyasm.biz.Snapshot', 'Snapshot', 'public');
        '''

 



    '''
    CREATE TABLE sobject_log (
        id integer NOT NULL,
        search_type character varying(100) NOT NULL,
        search_id integer NOT NULL,
        data text,
        "login" character varying(100) NOT NULL,
        "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
        transaction_log_id integer
    );
    '''
    def create_sobject_log(my):
        table = CreateTable()
        table.set_table("sobject_log")
        table.add("id",             "int", not_null=True )
        table.add("search_type",    "varchar", not_null=True)
        table.add("search_id",      "number", not_null=True)
        table.add("data",           "text")
        table.add("login",          "varchar", not_null=True)
        table.add("timestamp",      "timestamp", not_null=True)
        table.add("transaction_log_id","number")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (15, 'sthpw/sobject_log', 'sthpw', 'Log of actions on an sobject', 'sthpw', 'sobject_log', 'pyasm.search.SObject', 'SObject Log', 'public');
        '''

    '''
    CREATE TABLE task (
        id integer NOT NULL,
        assigned character varying(100),
        description text,
        status text,
        discussion text,
        bid_start_date timestamp without time zone,
        bid_end_date timestamp without time zone,
        bid_duration double precision,
        actual_start_date timestamp without time zone,
        actual_end_date timestamp without time zone,
        search_type character varying(100),
        search_id integer,
        "timestamp" timestamp without time zone DEFAULT now(),
        s_status character varying(30),
        priority smallint,
        process character varying(256),
        context character varying(256),
        milestone_code character varying(200),
        pipeline_code character varying(30),
        parent_id integer,
        sort_order smallint,
        depend_id integer,
        project_code character varying(100),
        supervisor character varying(100),
        code character varying(256,
        completion character float
    );
    '''
    def create_task(my):
        table = CreateTable()
        table.set_table("task")
        table.add("id",                 "int", not_null=True )
        table.add("assigned",           "varchar")
        table.add("description",        "text")
        table.add("status",             "varchar")
        #table.add("discussion",         "varchar")
        table.add("bid_start_date",     "timestamp")
        table.add("bid_end_date",       "timestamp")
        table.add("bid_duration",       "number")
        #table.add("actual_start_date",  "timestamp")
        #table.add("actual_end_date",    "timestamp")
        table.add("search_type",        "varchar")
        table.add("search_id",          "number")
        table.add("timestamp",          "timestamp")
        table.add("s_status",           "varchar")
        table.add("priority",           "number")
        table.add("process",            "varchar")
        table.add("context",            "varchar")
        table.add("milestone_code",     "varchar")
        table.add("pipeline_code",      "varchar")
        table.add("parent_id",          "number")
        table.add("sort_order",         "number")
        table.add("depend_id",          "number")
        table.add("project_code",       "varchar")
        table.add("supervisor",         "varchar")
        table.add("code",               "varchar")
        table.add("completion",         "float")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (25, 'sthpw/task', 'sthpw', 'Tasks', 'sthpw', 'task', 'pyasm.biz.Task', 'Tasks', NULL);
        '''



    '''
    CREATE TABLE ticket (
        id integer NOT NULL,
        ticket character varying(100) NOT NULL,
        "login" character varying(100),
        "timestamp" timestamp without time zone DEFAULT now(),
        expiry timestamp without time zone
    );
    '''
    def create_ticket(my):
        table = CreateTable()
        table.set_table("ticket")
        table.add("id",         "int", not_null=True )
        table.add("ticket",     "varchar", not_null=True)
        table.add("login",      "varchar", not_null=True)
        table.add("timestamp",  "timestamp")
        table.add("expiry",     "timestamp")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (17, 'sthpw/ticket', 'sthpw', 'Valid login tickets to enter the system', 'sthpw', 'ticket', 'pyasm.security.Ticket', 'Ticket', 'public');
        '''


    '''
    CREATE TABLE timecard (
        id integer NOT NULL,
        search_type character varying(100),
        search_id integer,
        week smallint,
        mon real,
        tue real,
        wed real,
        thu real,
        fri real,
        sat real,
        sun real,
        "login" character varying(100),
        project_code character varying(30),
        "year" integer,
        description text
    );
    '''
    def create_timecard(my):
        table = CreateTable()
        table.set_table("timecard")
        table.add("id",         "int", not_null=True )
        table.add("search_type","varchar")
        table.add("search_id",  "int")
        table.add("week",       "int")
        table.add("mon",        "float")
        table.add("tue",        "float")
        table.add("wed",        "float")
        table.add("thu",        "float")
        table.add("fri",        "float")
        table.add("sat",        "float")
        table.add("sun",        "float")
        table.add("year",       "int")
        table.add("login",      "varchar", not_null=True)
        table.add("project_code","varchar")
        table.add("description","text")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (22, 'sthpw/timecard', 'sthpw', 'Timecard Registration', 'sthpw', 'timecard', 'pyasm.search.SObject', 'Timecard', NULL);
        '''


    '''
    CREATE TABLE transaction_log (
        id integer NOT NULL,
        "transaction" text,
        "login" character varying(100) NOT NULL,
        "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
        description text,
        command character varying(100),
        title text,
        "type" character varying(30),
        namespace character varying(100)
    );
    '''
    def create_transaction_log(my):
        table = CreateTable()
        table.set_table("transaction_log")
        table.add("id",                 "int", not_null=True )
        table.add("transaction",        "text")
        table.add("login",              "varchar", not_null=True)
        table.add("timestamp",          "timestamp")
        table.add("description",        "text")
        table.add("command",            "varchar")
        table.add("title",              "text")
        table.add("type",               "varchar")
        table.add("namespace",          "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (18, 'sthpw/transaction_log', 'sthpw', NULL, 'sthpw', 'transaction_log', 'pyasm.search.TransactionLog', 'Transaction Log', 'public')
        '''


    '''
    CREATE TABLE transaction_state (
        id integer NOT NULL,
        ticket character varying(100),
        "timestamp" timestamp without time zone,
        data text
    );
    '''
    def create_transaction_state(my):
        table = CreateTable()
        table.set_table("transaction_state")
        table.add("id",                 "int", not_null=True )
        table.add("ticket",             "varchar")
        table.add("timestamp",          "timestamp")
        table.add("data",               "text")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (107, 'sthpw/transaction_state', 'sthpw', 'XMLRPC State', 'sthpw', 'transaction_state', 'pyasm.search.TransactionState', 'transaction_state', 'public');
        '''



    '''
    CREATE TABLE "trigger" (
        id integer NOT NULL,
        class_name character varying(100) NOT NULL,
        description text,
        event character varying(32),
        project_code character varying(256)
    );
    '''
    def create_trigger(my):
        table = CreateTable()
        table.set_table("trigger")
        table.add("id",                 "int", not_null=True )
        table.add("class_name",         "varchar")
        table.add("script_path",        "varchar")
        table.add("description",        "text")
        table.add("event",              "varchar")
        table.add("mode",               "varchar")
        table.add("project_code",       "varchar")
        table.add("s_status",           "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        ''' 
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (29, 'sthpw/trigger', 'sthpw', 'Triggers', 'sthpw', 'trigger', 'pyasm.biz.TriggerSObj', 'Triggers', 'public')
        '''


    '''
    CREATE TABLE wdg_settings (
        id integer NOT NULL,
        "key" character varying(255) NOT NULL,
        "login" character varying(30) NOT NULL,
        data text,
        "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
        project_code character varying(30)
    );
    '''
    def create_wdg_settings(my):
        table = CreateTable()
        table.set_table("wdg_settings")
        table.add("id",             "int", not_null=True )
        table.add("key",            "varchar", not_null=True)
        table.add("login",          "varchar", not_null=True)
        table.add("data",           "text")
        table.add("timestamp",      "timestamp")
        table.add("project_code",   "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (19, 'sthpw/wdg_settings', 'sthpw', 'Persistent store for widgets to remember user settings', 'sthpw', 'wdg_settings', 'pyasm.web.WidgetSettings', 'Widget Settings', 'public');
        '''

    '''
    CREATE TABLE widget_extend (
        id integer NOT NULL,
        "key" character varying(256),
        "type" character varying(256),
        data text,
        project_code character varying(256),
        "login" character varying(32),
        "timestamp" timestamp without time zone,
        s_status character varying(32),
        description text
    );
    '''
    def create_widget_extend(my):
        table = CreateTable()
        table.set_table("widget_extend")
        table.add("id",             "int", not_null=True )
        table.add("key",            "varchar", not_null=True)
        table.add("type",           "varchar", not_null=True)
        table.add("data",           "text")
        table.add("project_code",   "varchar")
        table.add("login",          "varchar")
        table.add("timestamp",      "timestamp")
        table.add("s_status",       "varchar")
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (104, 'sthpw/widget_extend', 'sthpw', 'Extend Widget', 'sthpw', 'widget_extend', 'pyasm.search.SObject', 'widget_extend', 'public');
        '''


if __name__ == '__main__':
    database = SthpwSchema()
    database.create()

