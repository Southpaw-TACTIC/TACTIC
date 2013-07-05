###########################################################
#
# Copyright (c) 2005-2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['ConfigUpgrade']


from base_upgrade import *


class ConfigUpgrade(BaseUpgrade):

    #
    # 3.6.0.v03_MSQL
    #

    def upgrade_v3_6_0_v03_MSQL_001(my):
        my.run_sql('''
        ALTER TABLE "custom_property" ALTER COLUMN "description" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_002(my):
        my.run_sql('''
        ALTER TABLE "custom_script" ALTER COLUMN "description" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_003(my):
        my.run_sql('''
        ALTER TABLE "custom_script" ALTER COLUMN "script" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_004(my):
        my.run_sql('''
        ALTER TABLE "naming" ALTER COLUMN "dir_naming" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_005(my):
        my.run_sql('''
        ALTER TABLE "naming" ALTER COLUMN "file_naming" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_006(my):
        my.run_sql('''
        ALTER TABLE "naming" ALTER COLUMN "sandbox_dir_naming" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_007(my):
        my.run_sql('''
        ALTER TABLE "prod_setting" ALTER COLUMN "value" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_008(my):
        my.run_sql('''
        ALTER TABLE "prod_setting" ALTER COLUMN "description" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_009(my):
        my.run_sql('''
        ALTER TABLE "widget_config" ALTER COLUMN "config" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_010(my):
        my.run_sql('''
        ALTER TABLE "spt_url" ALTER COLUMN "widget" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_011(my):
        my.run_sql('''
        ALTER TABLE "spt_url" ALTER COLUMN "description" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_012(my):
        my.run_sql('''
        ALTER TABLE "spt_client_trigger" ALTER COLUMN "description" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_013(my):
        my.run_sql('''
        ALTER TABLE "spt_plugin" ALTER COLUMN "description" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_014(my):
        my.run_sql('''
        ALTER TABLE "spt_plugin" ALTER COLUMN "manifest" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_015(my):
        my.run_sql('''
        ALTER TABLE "spt_trigger" ALTER COLUMN "description" VARCHAR(MAX)
        ''')
        
    def upgrade_v3_6_0_v03_MSQL_016(my):
        my.run_sql('''
        ALTER TABLE "spt_trigger" ALTER COLUMN "data" VARCHAR(MAX)
        ''')
        
    #
    # 3.6.0.rc01
    #

    def upgrade_v3_6_0_rc01_001(my):
        my.run_sql('''
        ALTER TABLE spt_process ADD color varchar(256);
        ''')

    def upgrade_v3_6_0_b02_002(my):
        my.run_sql('''
        ALTER TABLE naming ADD ingest_rule_code varchar(256);
        ''')

    def upgrade_v3_6_0_b02_001(my):
        my.run_sql('''
        ALTER TABLE naming ADD class_name text;
        ''')


    
    #
    # 3.6.0.b01
    #

    def upgrade_v3_6_0_b01_001(my):
        my.run_sql('''
        ALTER TABLE naming ADD condition text;
        ''')



    #
    # 3.6.0.a01
    #
    def upgrade_v3_6_0_a01_002(my):
        my.run_sql('''
        CREATE TABLE spt_ingest_session (
            id INT IDENTITY,
            code varchar(256),
            title text,
            base_dir varchar(1024),
            location varchar(256),
            data text
        );
        ''')


    def upgrade_v3_6_0_a01_001(my):
        my.run_sql('''
        CREATE TABLE spt_ingest_rule (
            id INT IDENTITY,
            code varchar(256),
            spt_ingest_session_code varchar(256),
            title text,
            base_dir varchar(1024),
            [rule] varchar(1024),
            data text
        );
        ''')


    #
    # 3.5.0.rc01
    #
    def upgrade_v3_5_0_rc01_001(my):
        my.run_sql('''
        UPDATE widget_config SET category = 'SideBarWdg' WHERE search_type = 'SideBarWdg';
        ''')


    #
    # 3.1.0.b09
    #
    def upgrade_v3_1_0_b09_002(my):
        my.run_sql('''
        ALTER TABLE spt_trigger ADD trigger_type VARCHAR(256);
        ''')

    def upgrade_v3_1_0_b09_001(my):
        my.run_sql('''
        ALTER TABLE spt_trigger ADD process VARCHAR(256);
        ''')


    #
    # 3.1.0.b04
    #

   
    def upgrade_v3_1_0_b04_001(my):
        my.run_sql('''
        ALTER TABLE naming ADD snapshot_type varchar(256);
        ''')

    #
    # 3.1.0.b03
    #

    def upgrade_v3_1_0_b03_001(my):
        my.run_sql('''
        ALTER TABLE spt_trigger ADD data text;
        ''')

    #
    # 3.1.0.a02
    #
    """
    def upgrade_v3_1_0_a02_006(my):
        my.run_sql('''
        INSERT INTO "spt_search_type" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('config/pipeline', '{project}', 'Pipeline', '{project}', 'spt_pipeline', 'pyasm.biz.Pipeline', 'Pipeline', 'public');
        ''')



    def upgrade_v3_1_0_a02_005(my):
        my.run_sql('''
        INSERT INTO "spt_search_type" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('config/search_type', '{project}', 'Search Type', '{project}', 'spt_search_type', 'pyasm.search.SObject', 'Search Type', 'public');
        ''')



    def upgrade_v3_1_0_a02_004(my):
        my.run_sql('''
        CREATE TABLE spt_search_type (
            id INT IDENTITY,
            search_type character varying(100) NOT NULL,
            namespace character varying(200) NOT NULL,
            description text,
            [database] character varying(100) NOT NULL,
            table_name character varying(100) NOT NULL,
            class_name character varying(100) NOT NULL,
            title character varying(100),
            [schema] character varying(100)
        );
        ''')




    def upgrade_v3_1_0_a02_003(my):
        my.run_sql('''
        CREATE TABLE spt_pipeline (
            id INT IDENTITY,
            code character varying(128) NOT NULL,
            pipeline text,
            [timestamp] datetime2(6) DEFAULT (getdate()) NOT NULL,
            search_type character varying(100),
            description text,
            s_status character varying(30)
        );
        ''')
    """



    def upgrade_v3_1_0_a02_002(my):
        my.run_sql('''
        ALTER TABLE spt_trigger ADD title varchar(256);
        ''')


    def upgrade_v3_1_0_a02_001(my):
        my.run_sql('''
        ALTER TABLE spt_trigger ADD process varchar(256);
        ''')


    #
    # 3.0.0.rc03
    #
    def upgrade_v3_0_0_rc03_001(my):
        my.run_sql('''
        ALTER TABLE naming ADD manual_version BIT;
        ''')

    #
    # 3.0.0.b01
    #
    """
    def upgrade_v3_0_0_b01_005(my):
        my.run_sql('''
        CREATE TABLE spt_bid (
            id INT IDENTITY,
            code varchar(256),
            category varchar(256),
            search_type varchar(256),
            description text,
            pipeline_code varchar(256),
            items integer,
            unit_cost float,
            s_status varchar(256)
        )
        ''')
    """


    def upgrade_v3_0_0_b01_003(my):
        my.run_sql('''
        ALTER TABLE spt_plugin ADD version varchar(256);
        ''')



    def upgrade_v3_0_0_b01_002(my):
        my.run_sql('''
        CREATE TABLE spt_process (
            id INT IDENTITY,
            code varchar(256),
            pipeline_code varchar(256),
            process varchar(256),
            sort_order integer,
            [timestamp] datetime2(6),
            s_status varchar(256)
        )
        ''')



    def upgrade_v3_0_0_b01_001(my):
        my.run_sql('''
        CREATE TABLE spt_trigger (
            id INT IDENTITY,
            code varchar(256),
            class_name varchar(256),
            script_path varchar(256),
            description text,
            event varchar(256),
            mode varchar(256),
            [timestamp] datetime2(6),
            s_status varchar(256)
        )
        ''')



    #
    # 2.7.0.a01
    #
    def upgrade_v2_7_0_a01_003(my):
        my.run_sql('''
        ALTER TABLE naming ADD latest_versionless BIT;
        ''')


    def upgrade_v2_7_0_a01_002(my):
        my.run_sql('''
        ALTER TABLE naming ADD current_versionless BIT;
        ''')





    def upgrade_v2_7_0_a01_001(my):
        my.run_sql('''
        CREATE TABLE spt_plugin (
            id INT IDENTITY,
            code varchar(256),
            description text,
            manifest text,
            [timestamp] datetime2(6),
            s_status varchar(256)
        )
        ''')


    #
    # 2.6.0.b02
    # 
    def upgrade_v2_6_0_b02_001(my):
        my.run_sql('''
        CREATE TABLE spt_client_trigger (
            id INT IDENTITY,
            code varchar(256),
            event varchar(256),
            callback varchar(256),
            description text,
            [timestamp] datetime2(6),
            s_status varchar(256)
        )
        ''')


    #
    # 2.6.0.a01
    # 
    def upgrade_v2_6_0_a01_001(my):
        my.run_sql('''
        CREATE TABLE spt_url (
            id INT IDENTITY,
            code varchar(256),
            url varchar(256),
            widget text,
            description text,
            [timestamp] datetime2(6),
            s_status varchar(256)
        )
        ''')

    #
    # 2.5.0.rc10
    # 
    def upgrade_v2_5_0_rc10_001(my):
        my.run_sql('''
        ALTER TABLE naming ADD context varchar(256);
        ''')
    #
    # 2.5.0.rc06
    # 
    def upgrade_v2_5_0_rc08_001(my):
        my.run_sql('''
        ALTER TABLE naming ADD sandbox_dir_naming text;
        ''')


    #
    # 2.5.0.a01
    # 
    def upgrade_v2_5_0_a01_006(my):
        my.run_sql('''
        CREATE TABLE custom_script (
            id INT IDENTITY,
            code varchar(256),
            title varchar(256),
            description text,
            folder varchar(1024),
            script text,
            login varchar(256),
            [timestamp] datetime2(6),
            s_status varchar(256)
        );
        ''')



    def upgrade_v2_5_0_a01_005(my):
        my.run_sql('''
        ALTER TABLE naming ADD code varchar(256);
        ''')


    def upgrade_v2_5_0_a01_004(my):
        my.run_sql('''
        CREATE UNIQUE INDEX pipeline_code_idx ON pipeline (code);
        ''')


    def upgrade_v2_5_0_a01_003(my):
        my.run_sql('''
        CREATE TABLE pipeline (
            id INT IDENTITY,
            code varchar(256),
            pipeline text,
            [timestamp] datetime2(6) DEFAULT (getdate()),
            search_type varchar(256),
            description text,
            s_status varchar(32),
            
        );
        ''')


    def upgrade_v2_5_0_a01_002(my):
        my.run_sql('''
        CREATE UNIQUE INDEX widget_config_code_idx ON widget_config (code);
        ''')


    def upgrade_v2_5_0_a01_001(my):
        my.run_sql('''
        CREATE TABLE widget_config (
            id INT IDENTITY,
            code character varying(256),
            [view] character varying(256),
            category character varying(256),
            search_type character varying(256),
            [login] character varying(256),
            config text,
            [timestamp] datetime2(6) DEFAULT (getdate()),
            s_status character varying(32),
            
        );
        ''')



