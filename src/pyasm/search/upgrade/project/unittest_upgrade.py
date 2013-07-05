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

__all__ = ['UnittestUpgrade']


from pyasm.search.upgrade.project import *


class UnittestUpgrade(BaseUpgrade):

    def upgrade_v3_8_0_rc01_001(my):
        my.run_sql('''
        ALTER TABLE city add column metadata text;
        ''')


    def upgrade_v3_1_0_b09_001(my):
        my.run_sql('''
        ALTER TABLE person add column pipeline_code varchar(256);
        ''')

    def upgrade_v2_5_0_v01_003(my):
        my.run_sql('''
        ALTER TABLE person add column timestamp timestamp default now();
        ''')

    def upgrade_v2_5_0_v01_002(my):
        my.run_sql('''
        ALTER TABLE person add column age integer;
        ''')

    def upgrade_v2_5_0_v01_001(my):
        my.run_sql('''
        ALTER TABLE person add column birth_date timestamp;
        ''')

    def upgrade_v2_5_0_rc12_001(my):
        my.run_sql('''
        ALTER TABLE city ADD CONSTRAINT city_code_unique UNIQUE(code);
        ''')

    def upgrade_v2_5_0_rc12_002(my):
        my.run_sql('''
        ALTER TABLE country ADD CONSTRAINT country_code_unique UNIQUE(code);
        ''')

    def upgrade_v2_5_0_rc12_003(my):
        my.run_sql('''
        ALTER TABLE person ADD CONSTRAINT person_code_unique UNIQUE(code);
        ''')

    # 2.5.0.rc01
    def upgrade_v2_5_0_rc01_001(my):
        my.run_sql('''
        ALTER TABLE person ADD COLUMN age integer
        ''')

    def upgrade_v2_5_0_b03_001(my):
        my.run_sql('''
        CREATE TABLE widget_config (
            id serial,
            code character varying(256) UNIQUE,
            "view" character varying(256),
            category character varying(256),
            search_type character varying(256),
            "login" character varying(256),
            config text,
            "timestamp" timestamp without time zone DEFAULT now(),
            s_status character varying(32),
            PRIMARY KEY (id)
        );
        ''')
    #
    # 2.1.0.b01
    #
    def upgrade_v2_1_0_b01_001(my):
        my.run_sql('''
        alter table person add column metadata text;
        ''')
    #
    # 2.1.0.a02
    #
    def upgrade_v2_1_0_a02_001(my):
        my.run_sql('''
        CREATE TABLE snapshot_type (
            id serial,
            code character varying(256),
            pipeline_code text,
            "timestamp" timestamp without time zone DEFAULT now(),
            "login" character varying(256),
            s_status character varying(30),
            relpath text,
            project_code character varying(256),
            subcontext text,
            snapshot_flavor text
        );
        ''')



    #
    # 2.0.0.a01
    #
    
    def upgrade_v2_0_0_a01_003(my):
        my.run_sql('''
        CREATE TABLE session_contents (
            id serial NOT NULL,
            "login" character varying(100) NOT NULL,
            pid integer NOT NULL,
            data text,
            "session" text,
            "timestamp" timestamp without time zone DEFAULT now()
        );
        ''')



    #
    # 1.9.0.a9
    #
    def upgrade_v1_9_0_a9_004(my):
        my.run_sql('''
        alter table country add column s_status varchar(32);
        ''')

    def upgrade_v1_9_0_a9_003(my):
        my.run_sql('''
        CREATE TABLE city (
            id serial NOT NULL,
            code character varying(256),
            name character varying(256),
            country_code character varying(256)
        );
        ''')

    def upgrade_v1_9_0_a9_002(my):
        my.run_sql('''
        CREATE TABLE country (
            id serial NOT NULL,
            code character varying(256),
            name character varying(256)
        );
        ''')


    def upgrade_v1_9_0_a9_001(my):
        my.run_sql('''
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
            city_code character varying(256)
        );
        ''')


