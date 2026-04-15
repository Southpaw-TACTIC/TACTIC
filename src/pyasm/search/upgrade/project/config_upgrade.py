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


from pyasm.search.upgrade.project import *


class ConfigUpgrade(BaseUpgrade):


    def upgrade_v4_7_0_a10_002(self):
        if self.get_database_type() == 'PostgreSQL':
            self.run_sql('''
            ALTER TABLE "spt_authenticate" ADD COLUMN "data" jsonb;
            ''')
        else:
            self.run_sql('''
            ALTER TABLE "spt_authenticate" ADD COLUMN "data" json;
            ''')



    def upgrade_v4_7_0_a10_001(self):
        self.run_sql('''
        CREATE TABLE "spt_authenticate" (
            "id" serial PRIMARY KEY,
            "code" character varying(256),
            name character varying(256),
            description text,
            "type" character varying(256),
            "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
            login character varying(256),
            s_status varchar(32),
            CONSTRAINT "spt_authenticate_code_idx" UNIQUE ("code")
        );
        ''')




    #
    # 4.7.0.a08
    #
    def upgrade_v4_7_0_a08_002(self):
        self.run_sql('''
        ALTER TABLE "spt_process_state" ALTER COLUMN "status" TYPE varchar(256);
        ''')


    def upgrade_v4_7_0_a08_001(self):
        if self.get_database_type() == 'PostgreSQL':
            self.run_sql('''
            ALTER TABLE "spt_process_state" ALTER COLUMN "state" TYPE jsonb USING state::jsonb;
            ''')
        else:
            self.run_sql('''
            ALTER TABLE "spt_process_state" ALTER COLUMN "state" TYPE json;
            ''')


    #
    # 4.7.0.a01
    #
    def upgrade_v4_7_0_a01_002(self):
        if self.get_database_type() == 'PostgreSQL':
            self.run_sql('''
            ALTER TABLE "spt_process" ALTER COLUMN "workflow" TYPE jsonb USING workflow::jsonb;
            ''')
        else:
            self.run_sql('''
            ALTER TABLE "spt_process" ALTER COLUMN "workflow" TYPE json;
            ''')


    def upgrade_v4_7_0_a01_001(self):
        if self.get_database_type() == 'PostgreSQL':
            self.run_sql('''
            CREATE TABLE "spt_process_state" (
                "id" serial PRIMARY KEY,
                "code" character varying(256),
                "pipeline_code" character varying(256),
                "process" character varying(256),
                "search_type" character varying(256),
                "search_code" character varying(256),
                "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
                "state" jsonb,
                "status" character varying(256),
                "data" jsonb,
                "s_status" character varying(32),
                CONSTRAINT "spt_pipeline_info_code_idx" UNIQUE ("code")
            );
            ''')
        else:
            self.run_sql('''
            CREATE TABLE "spt_process_state" (
                "id" serial PRIMARY KEY,
                "code" character varying(256),
                "pipeline_code" character varying(256),
                "process" character varying(256),
                "search_type" character varying(256),
                "search_code" character varying(256),
                "timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
                "status" json,
                "state" character varying(256),
                "data" json,
                "s_status" character varying(32),
                CONSTRAINT "spt_pipeline_info_code_idx" UNIQUE ("code")
            );
            ''')

    #
    #
    #
    def upgrade_v4_6_0_a02_001(self):
        self.run_sql('''
        ALTER TABLE spt_pipeline ADD COLUMN type varchar(256);
        ''')



    def upgrade_v4_6_0_a01_003(self):
        self.run_sql('''
        ALTER TABLE spt_pipeline ADD COLUMN name varchar(256);
        ''')


    def upgrade_v4_6_0_a01_002(self):
        self.run_sql('''
        ALTER TABLE widget_config ADD COLUMN priority integer;
        ''')
        self.run_sql('''
        ALTER TABLE spt_widget_config ADD COLUMN priority integer;
        ''')





    def upgrade_v4_6_0_a01_001(self):
         self.run_sql('''
         ALTER TABLE prod_setting DROP CONSTRAINT "prod_setting_key_idx";
         ''')
         self.run_sql('''
         ALTER TABLE spt_prod_setting DROP CONSTRAINT "spt_prod_setting_key_idx";
         ''')


    #
    # 4.4.0.a01
    #

    def upgrade_v4_4_0_a01_003(self):
        self.run_sql('''
        ALTER TABLE "spt_process" ADD "subpipeline_code" varchar(256);
        ''')



    def upgrade_v4_4_0_a01_002(self):
        self.run_sql('''
        ALTER TABLE "spt_process" ADD "workflow" text;
        ''')


    def upgrade_v4_4_0_a01_001(self):
        self.run_sql('''
        ALTER TABLE "custom_script" ADD "path" text;
        ''')



    #
    # 4.2.0.a01
    #

    def upgrade_v4_2_0_a01_003(self):
        self.run_sql('''
        CREATE TABLE spt_translation (
            id serial PRIMARY KEY,
            code character varying(256),
            name character varying(256),
            en text,
            fr text,
            ja text,
            es text,
            login character varying(256),
            "timestamp" timestamp without time zone DEFAULT now(),
            CONSTRAINT "spt_translation_code_idx" UNIQUE (code),
            CONSTRAINT "spt_translation_name_idx" UNIQUE (name)
        );
        ''')




    def upgrade_v4_2_0_a01_002(self):
        self.run_sql('''
        ALTER TABLE "naming" ADD "sandbox_dir_alias" varchar(256);
        ''')
        self.run_sql('''
        ALTER TABLE "spt_naming" ADD "sandbox_dir_alias" varchar(256);
        ''')



    def upgrade_v4_2_0_a01_001(self):
        self.run_sql('''
        ALTER TABLE "naming" ADD "base_dir_alias" varchar(256);
        ''')
        self.run_sql('''
        ALTER TABLE "spt_naming" ADD "base_dir_alias" varchar(256);
        ''')




    #
    # 4.1.0.b02
    #

    def upgrade_v4_1_0_b02_002(self):
        self.run_sql('''
        CREATE TABLE spt_pipeline (
            id serial PRIMARY KEY,
            code varchar(256),
            pipeline text,
            "timestamp" timestamp DEFAULT now(),
            search_type varchar(256),
            description text,
            s_status varchar(32),
            color character varying(256),
            autocreate_tasks boolean,
            CONSTRAINT "spt_pipeline_code_idx" UNIQUE (code)
        );
        ''')






    def upgrade_v4_1_0_b02_001(self):
        self.run_sql('''
        ALTER TABLE "widget_config" ADD "title" varchar(1024);
        ''')
        self.run_sql('''
        ALTER TABLE "spt_widget_config" ADD "title" varchar(1024);
        ''')



    #
    # 4.1.0.a01
    #
    def upgrade_v4_1_0_a01_003(self):
        self.run_sql('''
        ALTER TABLE spt_url add CONSTRAINT url_unique UNIQUE (url);
        ''')



    def upgrade_v4_1_0_a01_002(self):
        self.run_sql('''
        CREATE TABLE spt_plugin_content (
            id serial PRIMARY KEY,
            code varchar(256),
            plugin_code varchar(256),
            search_type varchar(256),
            search_code varchar(256)
        );
        ''')


    def upgrade_v4_1_0_a01_001(self):
        self.run_sql('''
        ALTER TABLE "widget_config" ADD "description" text;
        ''')
        self.run_sql('''
        ALTER TABLE "spt_widget_config" ADD "description" text;
        ''')

    #
    # 4.0.0.b08
    #
    def upgrade_v4_0_0_b08_003(self):
        self.run_sql('''
        ALTER TABLE "naming" DROP COLUMN "checkin_mode";
        ''')
        self.run_sql('''
        ALTER TABLE "spt_naming" DROP COLUMN "checkin_mode";
        ''')

    def upgrade_v4_0_0_b08_002(self):
        self.run_sql('''
        UPDATE "naming" SET "checkin_type" = "checkin_mode";
        ''')
        self.run_sql('''
        UPDATE "spt_naming" SET "checkin_type" = "checkin_mode";
        ''')

    def upgrade_v4_0_0_b08_001(self):
        self.run_sql('''
        ALTER TABLE "naming" ADD "checkin_type" varchar(256);
        ''')
        self.run_sql('''
        ALTER TABLE "spt_naming" ADD "checkin_type" varchar(256);
        ''')


    #
    # 4.0.0.b03
    #
    def upgrade_v4_0_0_b03_003(self):
        self.run_sql('''
        ALTER TABLE "naming" ADD "checkin_mode" varchar(256);
        ''')
        self.run_sql('''
        ALTER TABLE "spt_naming" ADD "checkin_mode" varchar(256);
        ''')


    #
    # 4.0.0.b01
    #
    def upgrade_v4_0_0_b01_002(self):
        self.run_sql('''
        ALTER TABLE "widget_config" ADD "widget_type" varchar(256);
        ''')
        self.run_sql('''
        ALTER TABLE "spt_widget_config" ADD "widget_type" varchar(256);
        ''')




    def upgrade_v4_0_0_b01_001(self):
        self.run_sql('''
        CREATE UNIQUE INDEX "spt_url_code_idx" on spt_url (code);
        ''')


    #
    # 4.0.0.a02
    #
    def upgrade_v4_0_0_a09_001(self):
        self.run_sql('''
        ALTER TABLE spt_plugin add column rel_dir text;
        ''')



    def upgrade_v4_0_0_a02_002(self):
        self.run_sql('''
        ALTER TABLE prod_setting add CONSTRAINT prod_setting_code_unique UNIQUE (code);
        ''')
        self.run_sql('''
        ALTER TABLE spt_prod_setting add CONSTRAINT spt_prod_setting_code_unique UNIQUE (code);
        ''')

    def upgrade_v4_0_0_a02_001(self):
        self.run_sql('''ALTER TABLE prod_setting ADD COLUMN code varchar(256);''')

        self.run_sql('''ALTER TABLE spt_prod_setting ADD COLUMN code varchar(256);''')



    """
    #
    # 3.9.0.b04
    #
    def upgrade_v3_8_0_b06_001(self):
        self.run_sql('''
        ALTER TABLE widget_config ADD COLUMN folder text;
        ''')



    #
    # 3.8.0.b06
    #
    def upgrade_v3_8_0_b06_001(self):
        self.run_sql('''
        ALTER TABLE spt_process ADD COLUMN transfer_mode varchar(256);
        ''')



    #
    # 3.8.0.b05
    #
    def upgrade_v3_8_0_b05_001(self):
        self.run_sql('''
        ALTER TABLE custom_script ADD COLUMN language varchar(256);
        ''')





    #
    # 3.8.0.b02
    #
    # repeated from 3.7 to ensure it's run for early 3.8 adopters
    def upgrade_v3_8_0_b02_002(self):
        self.run_sql('''
        ALTER TABLE spt_process ADD COLUMN context_options text;
        ''')


    def upgrade_v3_8_0_b02_001(self):
        self.run_sql('''ALTER TABLE spt_process ADD COLUMN repo_type varchar(256)''')


    #
    # 3.8.0.b01
    #
    def upgrade_v3_8_0_b01_001(self):
        self.run_sql('''ALTER TABLE spt_process ADD COLUMN description text''')



    #
    # 3.8.0.a01
    #
    def upgrade_v3_8_0_a01_001(self):
        self.run_sql('''ALTER TABLE spt_trigger ADD COLUMN search_type varchar(256)''')

    #
    # 3.7.0.v03
    #

    def upgrade_v3_7_0_v03_001(self):
        self.run_sql('''
        ALTER TABLE spt_process ADD COLUMN context_options text;
        ''')


    #
    # 3.7.0.v01
    #
    def upgrade_v3_7_0_v01_001(self):
        self.run_sql('''UPDATE spt_process SET subcontext_options='(main)' where subcontext_options='(none)';''')




    def upgrade_v3_7_0_v01_001(self):
        self.run_sql('''UPDATE spt_process SET subcontext_options='(main)' where subcontext_options='(none)';''')



    #
    # 3.7.0.rc04
    #
    def upgrade_v3_7_0_rc04_001(self):
        self.run_sql('''ALTER TABLE spt_process ADD COLUMN sandbox_create_script_path text''');


    #
    # 3.7.0.rc02
    #
    def upgrade_v3_7_0_rc02_004(self):
        self.run_sql('''
        ALTER TABLE naming ADD COLUMN script_path text;
        ''')


    #
    # 3.7.0.a01
    #
    def upgrade_v3_7_0_a01_004(self):
        self.run_sql('''
        ALTER TABLE spt_process ADD COLUMN checkin_options_view text;
        ''')


    def upgrade_v3_7_0_a01_003(self):
        self.run_sql('''
        ALTER TABLE spt_process ADD COLUMN checkin_validate_script_path text;
        ''')


    def upgrade_v3_7_0_a01_002(self):
        self.run_sql('''
        ALTER TABLE spt_process ADD COLUMN subcontext_options text;
        ''')



    def upgrade_v3_7_0_a01_001(self):
        self.run_sql('''
        ALTER TABLE spt_process ADD COLUMN checkin_mode text;
        ''')



    #
    # 3.6.0.b02
    #

    def upgrade_v3_6_0_rc01_001(self):
        self.run_sql('''
        ALTER TABLE spt_process ADD COLUMN color varchar(256);
        ''')

    def upgrade_v3_6_0_b02_002(self):
        self.run_sql('''
        ALTER TABLE naming ADD COLUMN ingest_rule_code varchar(256);
        ''')

    def upgrade_v3_6_0_b02_001(self):
        self.run_sql('''
        ALTER TABLE naming ADD COLUMN class_name text;
        ''')



    #
    # 3.6.0.b01
    #

    def upgrade_v3_6_0_b01_001(self):
        self.run_sql('''
        ALTER TABLE naming ADD COLUMN "condition" text;
        ''')



    #
    # 3.6.0.a01
    #
    def upgrade_v3_6_0_a01_002(self):
        self.run_sql('''
        CREATE TABLE spt_ingest_session (
            id serial PRIMARY KEY,
            code varchar(256),
            title text,
            base_dir varchar(1024),
            location varchar(256),
            data text
        );
        ''')


    def upgrade_v3_6_0_a01_001(self):
        self.run_sql('''
        CREATE TABLE spt_ingest_rule (
            id serial PRIMARY KEY,
            code varchar(256),
            spt_ingest_session_code varchar(256),
            title text,
            base_dir varchar(1024),
            rule varchar(1024),
            data text
        );
        ''')


    #
    # 3.5.0.rc01
    #
    def upgrade_v3_5_0_rc01_001(self):
        self.run_sql('''
        UPDATE widget_config SET category = 'SideBarWdg' WHERE search_type = 'SideBarWdg';
        ''')


    #
    # 3.1.0.b09
    #
    def upgrade_v3_1_0_b09_002(self):
        self.run_sql('''
        ALTER TABLE spt_trigger ADD COLUMN trigger_type VARCHAR(256);
        ''')

    def upgrade_v3_1_0_b09_001(self):
        self.run_sql('''
        ALTER TABLE spt_trigger ADD COLUMN process VARCHAR(256);
        ''')


    #
    # 3.1.0.b04
    #


    def upgrade_v3_1_0_b04_001(self):
        self.run_sql('''
        ALTER TABLE naming ADD COLUMN snapshot_type varchar(256);
        ''')

    #
    # 3.1.0.b03
    #

    def upgrade_v3_1_0_b03_001(self):
        self.run_sql('''
        ALTER TABLE spt_trigger ADD COLUMN data text;
        ''')



    def upgrade_v3_1_0_a02_002(self):
        self.run_sql('''
        ALTER TABLE spt_trigger ADD COLUMN title varchar(256);
        ''')


    def upgrade_v3_1_0_a02_001(self):
        self.run_sql('''
        ALTER TABLE spt_trigger ADD COLUMN process varchar(256);
        ''')


    #
    # 3.0.0.rc03
    #
    def upgrade_v3_0_0_rc03_001(self):
        self.run_sql('''
        ALTER TABLE naming ADD COLUMN manual_version boolean;
        ''')


    def upgrade_v3_0_0_b01_003(self):
        self.run_sql('''
        ALTER TABLE spt_plugin ADD COLUMN version varchar(256);
        ''')



    def upgrade_v3_0_0_b01_002(self):
        self.run_sql('''
        CREATE TABLE spt_process (
            id serial PRIMARY KEY,
            code varchar(256),
            pipeline_code varchar(256),
            process varchar(256),
            sort_order integer,
            "timestamp" timestamp,
            s_status varchar(256)
        )
        ''')



    def upgrade_v3_0_0_b01_001(self):
        self.run_sql('''
        CREATE TABLE spt_trigger (
            id serial PRIMARY KEY,
            code varchar(256),
            class_name varchar(256),
            script_path varchar(256),
            description text,
            event varchar(256),
            mode varchar(256),
            "timestamp" timestamp,
            s_status varchar(256)
        )
        ''')



    #
    # 2.7.0.a01
    #
    def upgrade_v2_7_0_a01_003(self):
        self.run_sql('''
        ALTER TABLE naming ADD COLUMN latest_versionless boolean;
        ''')


    def upgrade_v2_7_0_a01_002(self):
        self.run_sql('''
        ALTER TABLE naming ADD COLUMN current_versionless boolean;
        ''')





    def upgrade_v2_7_0_a01_001(self):
        self.run_sql('''
        CREATE TABLE spt_plugin (
            id serial PRIMARY KEY,
            code varchar(256),
            description text,
            manifest text,
            "timestamp" timestamp,
            s_status varchar(256)
        )
        ''')


    #
    # 2.6.0.b02
    #
    def upgrade_v2_6_0_b02_001(self):
        self.run_sql('''
        CREATE TABLE spt_client_trigger (
            id serial PRIMARY KEY,
            code varchar(256),
            event varchar(256),
            callback varchar(256),
            description text,
            "timestamp" timestamp,
            s_status varchar(256)
        )
        ''')


    #
    # 2.6.0.a01
    #
    def upgrade_v2_6_0_a01_001(self):
        self.run_sql('''
        CREATE TABLE spt_url (
            id serial PRIMARY KEY,
            code varchar(256),
            url varchar(256),
            widget text,
            description text,
            "timestamp" timestamp,
            s_status varchar(256)
        )
        ''')

    #
    # 2.5.0.rc10
    #
    def upgrade_v2_5_0_rc10_001(self):
        self.run_sql('''
        ALTER TABLE naming ADD COLUMN context varchar(256);
        ''')
    #
    # 2.5.0.rc06
    #
    def upgrade_v2_5_0_rc08_001(self):
        self.run_sql('''
        alter table naming add column sandbox_dir_naming text;
        ''')


    #
    # 2.5.0.a01
    #
    def upgrade_v2_5_0_a01_006(self):
        self.run_sql('''
        CREATE TABLE custom_script (
            id serial PRIMARY KEY,
            code varchar(256),
            title varchar(256),
            description text,
            folder varchar(1024),
            script text,
            login varchar(256),
            "timestamp" timestamp,
            s_status varchar(256)
        );
        ''')



    def upgrade_v2_5_0_a01_005(self):
        self.run_sql('''
        alter table naming add column code varchar(256);
        ''')


    def upgrade_v2_5_0_a01_004(self):
        self.run_sql('''
        create unique index pipeline_code_idx on pipeline (code);
        ''')


    def upgrade_v2_5_0_a01_003(self):
        self.run_sql('''
        CREATE TABLE pipeline (
            id serial,
            code varchar(256),
            pipeline text,
            "timestamp" timestamp DEFAULT now(),
            search_type varchar(256),
            description text,
            s_status varchar(32),
            PRIMARY KEY (id)
        );
        ''')


    def upgrade_v2_5_0_a01_002(self):
        self.run_sql('''
        create unique index widget_config_code_idx on widget_config (code);
        ''')


    def upgrade_v2_5_0_a01_001(self):
        self.run_sql('''
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
        ''')

    """

