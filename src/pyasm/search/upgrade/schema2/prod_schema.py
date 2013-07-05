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

from pyasm.search import DbContainer, CreateTable

class ProdSchema(object):

    def create(my):

        my.sql = DbContainer.get("sample3d")

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
    CREATE TABLE asset (
        id integer NOT NULL,
        code character varying(256) NOT NULL,
        name character varying(100) NOT NULL,
        asset_type character varying(30) NOT NULL,
        description text,
        "timestamp" timestamp without time zone DEFAULT now(),
        images text,
        status text,
        snapshot text,
        retire_status character varying(30),
        asset_library character varying(100),
        pipeline_code character varying(256),
        s_status character varying(30),
        short_code character varying(256)
    );
    '''
    def create_asset(my):
        table = CreateTable()
        table.set_table("asset")
        table.add("id",             "int", not_null=True )
        table.add("short_code",     "varchar" )
        table.add("code",           "varchar", not_null=True )
        table.add("name",           "varchar")
        table.add("asset_type",     "varchar" )
        table.add("description",    "text" )
        table.add("timestamp",      "timestamp" )
        #table.add("images",         "text" )
        table.add("status",         "varchar" )
        #table.add("snapshot",       "text" )
        #table.add("retire_status",  "varchar" )
        table.add("asset_library",  "varchar" )
        table.add("pipeline_code",  "varchar" )
        table.add("s_status",       "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (50, 'prod/asset', 'prod', 'The base atomic entity that can exist shot', '{project}', '{public}.asset', 'pyasm.prod.biz.Asset', '3D Asset', 'public'); 
        '''

    '''
    CREATE TABLE asset_library (
        id integer NOT NULL,
        code character varying(30) NOT NULL,
        title character varying(100),
        description text,
        padding smallint,
        "type" character varying(30),
        s_status character varying(30)
    );
    '''
    def create_asset_library(my):
        table = CreateTable()
        table.set_table("asset_library")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar" )
        table.add("title",          "varchar" )
        table.add("description",    "text" )
        table.add("padding",        "number" )
        table.add("type",           "varchar" )
        table.add("s_status",       "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (49, 'prod/asset_library', 'prod', 'Asset Library Types', '{project}', '{public}.asset_library', 'pyasm.prod.biz.AssetLibrary', 'Asset Library Types', NULL);
        '''


    '''
    CREATE TABLE asset_type (
        id integer NOT NULL,
        code character varying(30) NOT NULL,
        description text
    );
    '''
    def create_asset_type(my):
        table = CreateTable()
        table.set_table("asset_type")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar" )
        table.add("descriptions",   "text" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (45, 'prod/asset_type', 'prod', 'Asset Type', '{project}', '{public}.asset_type', 'pyasm.search.SObject', 'Asset Type', 'public');
        '''


    '''
    CREATE TABLE bin (
        id integer NOT NULL,
        code character varying(256),
        description text,
        "type" character varying(100),
        s_status character varying(30),
        label character varying(100)
    );
    '''
    def create_bin(my):
        table = CreateTable()
        table.set_table("bin")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar" )
        table.add("description",    "text" )
        table.add("type",           "varchar" )
        table.add("s_status",       "varchar" )
        table.add("label",          "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (66, 'prod/bin', 'prod', 'Bin for submissions', '{project}', 'bin', 'pyasm.prod.biz.Bin', 'Bin for submissions', NULL);
        '''


    '''
    CREATE TABLE composite (
        id integer NOT NULL,
        name character varying(100),
        description text,
        shot_code character varying(100),
        snapshot text,
        "timestamp" timestamp without time zone DEFAULT now()
    );
    '''
    def create_composite(my):
        table = CreateTable()
        table.set_table("composite")
        table.add("id",             "int", not_null=True )
        table.add("name",           "varchar" )
        table.add("description",    "text" )
        table.add("shot_code",      "varchar" )
        #table.add("snapshot",       "text" )
        table.add("timestamp",      "timestamp" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (36, 'prod/composite', 'prod', 'Composites', '{project}', '{public}.composite', 'pyasm.prod.biz.Composite', 'Composites', 'public');
        '''

 
    '''
    CREATE TABLE episode (
        id integer NOT NULL,
        code character varying(256) NOT NULL,
        description text,
        "timestamp" timestamp without time zone DEFAULT now(),
        s_status character varying(30),
        sort_order smallint
    );
    '''
    def create_episode(my):
        table = CreateTable()
        table.set_table("episode")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar" )
        table.add("description",    "text" )
        table.add("timestamp",      "timestamp" )
        table.add("s_status",       "varchar" )
        table.add("sort_order",     "smallint" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (21, 'prod/episode', 'prod', 'Episode', '{project}', '{public}.episode', 'pyasm.prod.biz.Episode', 'Episode', 'public');
        '''


    '''
    CREATE TABLE layer (
        id integer NOT NULL,
        name character varying(100),
        description text,
        shot_code character varying(100),
        snapshot text,
        "timestamp" timestamp without time zone DEFAULT now(),
        s_status character varying(30)
    );
    '''
    def create_layer(my):
        table = CreateTable()
        table.set_table("layer")
        table.add("id",             "int", not_null=True )
        table.add("name",           "varchar" )
        table.add("description",    "text" )
        table.add("shot_code",      "varchar" )
        #table.add("snapshot",       "text" )
        table.add("timestamp",      "timestamp" )
        table.add("s_status",       "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (35, 'prod/layer', 'prod', 'Layers', '{project}', '{public}.layer', 'pyasm.prod.biz.Layer', 'Layers', 'public');
        '''


    '''
    CREATE TABLE render (
        id integer NOT NULL,
        "login" character varying(100),
        "timestamp" timestamp without time zone DEFAULT now(),
        search_type character varying(100),
        search_id integer,
        code character varying(256),
        "type" character varying(256),
        name character varying(256),
        s_status character varying(30)
    );
    '''
    def create_render(my):
        table = CreateTable()
        table.set_table("render")
        table.add("id",             "int", not_null=True )
        table.add("login",          "varchar" )
        table.add("timestamp",      "timestamp" )
        table.add("search_type",    "varchar" )
        table.add("search_id",      "int" )
        table.add("code",           "varchar" )
        table.add("type",           "varchar" )
        table.add("name",           "varchar" )
        table.add("s_status",       "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (54, 'prod/render', 'prod', 'Renders', '{project}', 'render', 'pyasm.prod.biz.Render', 'Renders', 'public');
        '''

    '''
    CREATE TABLE session_contents (
        id integer NOT NULL,
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
        table.add("login",          "varchar", not_null=True )
        table.add("pid",            "int" )
        table.add("data",           "text" )
        table.add("session",        "text" )
        table.add("timestamp",      "timestamp" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (40, 'prod/session_contents', 'prod', 'Introspection Contents of a users session', '{project}', 'session_contents', 'pyasm.prod.biz.SessionContents', 'Session Contents', 'public');
        '''



    '''
    CREATE TABLE shot (
        id integer NOT NULL,
        code character varying(30) NOT NULL,
        description text,
        "timestamp" timestamp without time zone DEFAULT now(),
        status text,
        images text,
        tc_frame_start smallint DEFAULT 1,
        tc_frame_end smallint DEFAULT 1,
        pipeline_code character varying(30),
        s_status character varying(30),
        parent_code character varying(30),
        sequence_code character varying(30),
        sort_order smallint,
        complexity smallint,
        frame_in smallint,
        frame_out smallint,
        frame_note text,
        scan_status character varying(256),
        "type" character varying(256),
        priority character varying(30),
        short_code character varying(256)
    );
    '''
    def create_shot(my):
        table = CreateTable()
        table.set_table("shot")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar" )
        table.add("description",    "text" )
        table.add("timestamp",      "timestamp" )
        table.add("status",         "varchar" )
        table.add("tc_frame_start", "number" )
        table.add("tc_frame_end",   "number" )
        table.add("pipeline_code",  "varchar" )
        table.add("s_status",       "varchar" )
        table.add("parent_code",    "varchar" )
        table.add("sequence_code",  "varchar" )
        table.add("sort_order",     "int" )
        table.add("complexity",     "int" )
        table.add("frame_in",       "int" )
        table.add("frame_out",      "int" )
        table.add("frame_note",     "text" )
        table.add("scan_status",    "varchar" )
        table.add("type",           "varchar" )
        table.add("priority",       "varchar" )
        table.add("short_code",     "varchar" )
        #table.add("images",         "text" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (48, 'prod/shot', 'prod', 'Shot', '{project}', '{public}.shot', 'pyasm.prod.biz.Shot', 'Shot', 'public');
        '''

    '''
    CREATE TABLE instance (
        id integer NOT NULL,
        code character varying(256),
        shot_code character varying(30) NOT NULL,
        asset_code character varying(100) NOT NULL,
        name character varying(100) NOT NULL,
        "timestamp" timestamp without time zone DEFAULT now(),
        status text,
        "type" character varying(30)
    );
    '''
    def create_shot_instance(my):
        table = CreateTable()
        table.set_table("instance")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar" )
        table.add("shot_code",      "varchar" )
        table.add("asset_code",     "varchar" )
        table.add("name",           "varchar" )
        table.add("timestamp",      "timestamp" )
        table.add("status",         "text" )
        table.add("type",           "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (63, 'prod/shot_instance', 'prod', 'An instance of an asset in a shot', '{project}', '{public}.instance', 'pyasm.prod.biz.ShotInstance', 'Shot Instance', 'public');
        '''


    '''
    CREATE TABLE plate (
        id integer NOT NULL,
        shot_code character varying(30),
        "type" character varying(30),
        "timestamp" timestamp without time zone DEFAULT now(),
        s_status character varying(30),
        description text,
        code character varying(256),
        pipeline_code character varying(256)
    );
    '''
    def create_plate(my):
        table = CreateTable()
        table.set_table("plate")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar" )
        table.add("shot_code",      "varchar" )
        table.add("type",           "varchar" )
        table.add("timestamp",      "timestamp" )
        table.add("description",    "text" )
        table.add("pipeline_code",  "varchar" )
        table.add("s_status",       "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (73, 'effects/plate', 'effects', 'Production Plates', '{project}', 'plate', 'pyasm.effects.biz.Plate', 'Production Plates', 'public');
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (127, 'prod/plate', 'prod', 'Production Plates', '{project}', 'plate', 'pyasm.effects.biz.Plate', 'Production plates', 'public');
        '''


    '''
    CREATE TABLE render (
        id integer NOT NULL,
        _images text,
        _session text,
        "login" character varying(100),
        "timestamp" timestamp without time zone DEFAULT now(),
        _snapshot text,
        search_type character varying(100),
        search_id integer,
        _snapshot_code character varying(30),
        _version smallint,
        _file_range character varying(200),
        code character varying(256),
        "type" character varying(256),
        name character varying(256),
        s_status character varying(30)
    );
    '''
    def create_render(my):
        table = CreateTable()
        table.set_table("render")
        table.add("id",             "int", not_null=True )
        table.add("login",          "varchar" )
        table.add("timestamp",      "timestamp" )
        table.add("search_type",    "varchar" )
        table.add("search_id",      "int" )
        table.add("code",           "varchar" )
        table.add("type",           "varchar" )
        table.add("name",           "varchar" )
        table.add("s_status",       "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ("search_object_id_seq".nextval, 'prod/render', 'prod', 'Renders', '{project}', 'render', 'pyasm.prod.biz.Render', 'Renders', 'public');
       '''


    '''
    CREATE TABLE shot_texture (
        id integer NOT NULL,
        description text,
        shot_code character varying(50),
        category character varying(200),
        "timestamp" timestamp without time zone DEFAULT now(),
        snapshot text,
        s_status character varying(32),
        code character varying(256),
        pipeline_code character varying(256),
        asset_context character varying(30),
        search_type character varying(256),
        search_id integer
    );
    '''
    def create_shot_texture(my):
        table = CreateTable()
        table.set_table("shot_texture")
        table.add("id",             "int", not_null=True )
        table.add("description",    "text" )
        table.add("shot_code",      "varchar" )
        table.add("category",       "varchar" )
        table.add("timestamp",      "timestamp" )
        #table.add("snapshot",       "text" )
        table.add("s_status",       "varchar" )
        table.add("code",           "varchar" )
        table.add("pipeline_code",  "varchar" )
        table.add("asset_context",  "varchar" )
        table.add("search_type",    "varchar" )
        table.add("search_id",      "int" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (38, 'prod/shot_texture', 'prod', 'Shot Texture maps', '{project}', '{public}.shot_texture', 'pyasm.prod.biz.ShotTexture', 'Shot Texture maps', 'public');
        '''

    '''
    CREATE TABLE "sequence" (
        id integer NOT NULL,
        code character varying(30) NOT NULL,
        description text,
        "timestamp" timestamp without time zone DEFAULT now(),
        s_status character varying(30),
        sort_order smallint,
        episode_code character varying(256)
    );
    '''
    def create_sequence(my):
        table = CreateTable()
        table.set_table("sequence")
        table.add("id",             "int", not_null=True )
        table.add("code",           "varchar" )
        table.add("description",    "text" )
        table.add("timestamp",      "timestamp" )
        table.add("s_status",       "varchar" )
        table.add("sort_order",     "int" )
        table.add("episode_cod",    "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (41, 'prod/sequence', 'prod', 'A list of shots that are grouped together', '{project}', '{public}.sequence', 'pyasm.prod.biz.Sequence', 'Sequence', 'public');
        '''


    '''
    CREATE TABLE sequence_instance (
        id integer NOT NULL,
        sequence_code character varying(30) NOT NULL,
        asset_code character varying(100) NOT NULL,
        "timestamp" timestamp without time zone DEFAULT now(),
        status text,
        "type" character varying(30)
    );
    '''
    def create_sequence_instance(my):
        table = CreateTable()
        table.set_table("sequence_instance")
        table.add("id",             "int", not_null=True )
        table.add("sequence_code",  "varchar", not_null=True )
        table.add("asset_code",     "varchar" )
        table.add("timestamp",      "timestamp" )
        table.add("status",         "varchar" )
        table.add("type",           "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (105, 'prod/sequence_instance', 'prod', 'Sequence Instance', '{project}', 'sequence_instance', 'pyasm.prod.biz.SequenceInstance', 'Sequence Instance', 'public');
        '''

    '''
    CREATE TABLE submission (
        id integer NOT NULL,
        search_type character varying(200),
        search_id integer,
        snapshot_code character varying(30),
        context character varying(100),
        version integer,
        description text,
        "login" character varying(30),
        "timestamp" timestamp without time zone DEFAULT now(),
        s_status character varying(30),
        artist character varying(256),
        status character varying(100)
    );
    '''
    def create_submission(my):
        table = CreateTable()
        table.set_table("submission")
        table.add("id",             "int", not_null=True )
        table.add("search_type",    "varchar" )
        table.add("search_id",      "number" )
        table.add("snapshot_code",  "varchar" )
        table.add("context",        "varchar" )
        table.add("version",        "number" )
        table.add("description",    "text" )
        table.add("login",          "varchar" )
        table.add("timestamp",      "timestamp" )
        table.add("s_status",       "varchar" )
        table.add("artist",         "varchar" )
        table.add("status",         "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (65, 'prod/submission', 'prod', 'Submission of quicktime, media files for an asset', '{project}', 'submission', 'pyasm.prod.biz.Submission', 'Submission', NULL);
        '''


    '''
    CREATE TABLE submission_in_bin (
        id integer NOT NULL,
        submission_id integer NOT NULL,
        bin_id integer NOT NULL
    );
    '''
    def create_submission_in_bin(my):
        table = CreateTable()
        table.set_table("submission_in_bin")
        table.add("id",             "int", not_null=True )
        table.add("submission_id",  "int", not_null=True )
        table.add("bin_id",         "int", not_null=True )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (67, 'prod/submission_in_bin', 'prod', 'Submissions in Bins', '{project}', 'submission_in_bin', 'pyasm.prod.biz.SubmissionInBin', 'Submissions in Bins', NULL);
        '''




    '''
    CREATE TABLE texture (
        id integer NOT NULL,
        description text,
        asset_code character varying(50),
        category character varying(200),
        "timestamp" timestamp without time zone DEFAULT now(),
        snapshot text,
        s_status character varying(32),
        code character varying(256),
        pipeline character varying(30),
        pipeline_code character varying(30),
        asset_context character varying(30)
    );
    '''
    def create_texture(my):
        table = CreateTable()
        table.set_table("texture")
        table.add("id",             "int", not_null=True )
        table.add("description",    "text" )
        table.add("asset_code",     "varchar" )
        table.add("category",       "varchar" )
        table.add("timestamp",      "timestamp" )
        #table.add("snapshot",       "text" )
        table.add("s_status",       "varchar" )
        table.add("code",           "varchar" )
        #table.add("pipeline",       "varchar" )
        table.add("pipeline_code",  "varchar" )
        table.add("asset_context",  "varchar" )
        table.set_primary_key("id")
        table.commit(my.sql)
        '''
        INSERT INTO "search_object" ("id", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES (37, 'prod/texture', 'prod', 'Textures', '{project}', '{public}.texture', 'pyasm.prod.biz.Texture', 'Textures', 'public');
        '''

if __name__ == '__main__':
    database = ProdSchema()
    database.create()



