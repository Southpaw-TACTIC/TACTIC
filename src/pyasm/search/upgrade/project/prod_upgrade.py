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

__all__ = ['ProdUpgrade']



# DEPRECATED


from pyasm.search.upgrade.project import *


class ProdUpgrade(BaseUpgrade):

    def upgrade_v3_8_0_v01_001(my):
        my.run_sql('''
        alter table submission add column "code" varchar(256);
        ''')

    def upgrade_v2_6_0_v01_001(my):
        my.run_sql('''
        alter table instance drop constraint shot_code_fkey;
        ''')


    #
    # 2.6.0.rc02 again
    #

    def upgrade_v2_6_0_rc02_002(my):
        my.run_sql('''
        ALTER TABLE asset ALTER COLUMN asset_type DROP NOT NULL;
        ''')

    def upgrade_v2_6_0_rc02_001(my):
        my.run_sql('''
        ALTER TABLE asset ALTER COLUMN name DROP NOT NULL;
        ''')


    #
    # 2.5.0.v01 again
    #
    def upgrade_v2_5_0_v01_001(my):
        my.run_sql('''
        ALTER TABLE shot_texture add constraint shot_texture_code_unique UNIQUE
        (code);
        ''')


    def upgrade_v2_5_0_rc09_002(my):
        my.run_sql('''
        CREATE INDEX texture_asset_code_idx ON texture(asset_code);
        ''')

    def upgrade_v2_5_0_rc09_001(my):
        my.run_sql('''
        CREATE INDEX texture_code_idx ON texture(code);
        
        ''')
    #
    # 2.5.0.b07 again
    #
    def upgrade_v2_5_0_b07_001(my):
        my.run_sql('''
        ALTER TABLE layer ADD COLUMN sort_order integer;
        ''')
    #
    # 2.5.0.b04
    # 
    def upgrade_v2_5_0_b04_002(my):
        my.run_sql('''
        ALTER TABLE texture alter column code type varchar(256);
        ''')

    def upgrade_v2_5_0_b04_001(my):
        my.run_sql('''
        ALTER TABLE shot_texture alter column code type varchar(256);
        ''')

    #
    # 2.5.0.b03
    # 
    def upgrade_v2_5_0_b03_003(my):
        my.run_sql('''
        ALTER TABLE asset DROP COLUMN images
        ''')


    def upgrade_v2_5_0_b03_002(my):
        my.run_sql('''
        ALTER TABLE asset DROP COLUMN snapshot
        ''')


    def upgrade_v2_5_0_b03_001(my):
        my.run_sql('''
        ALTER TABLE asset DROP COLUMN retire_status
        ''')




    #
    # 2.5.0.a01
    # 

    def upgrade_v2_5_0_a01_006(my):
        my.run_sql('''
        ALTER TABLE asset ALTER COLUMN code DROP NOT NULL;
        ''')


    def upgrade_v2_5_0_a01_005(my):
        my.run_sql('''
        alter table asset add primary key (id);
        ''')



    def upgrade_v2_5_0_a01_004(my):
        my.run_sql('''
        alter table asset drop constraint asset_pkey;
        ''')



    def upgrade_v2_5_0_a01_003(my):
        #"$2" FOREIGN KEY (asset_code) REFERENCES asset(code) ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
        my.run_sql('''
        alter table layer_instance drop constraint "$2";
        ''')




    def upgrade_v2_5_0_a01_002(my):
         #"asset_code_fkey" FOREIGN KEY (asset_code) REFERENCES asset(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED
        my.run_sql('''
        alter table instance drop constraint asset_code_fkey;
        ''')




    def upgrade_v2_5_0_a01_001(my):
        my.run_sql('''
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


    #
    # 2.4.0.a01
    #
    def upgrade_v2_4_0_a01_009(my):
        my.run_sql('''
        alter table shot alter column code drop not null;
        ''')



    def upgrade_v2_4_0_a01_008(my):
        my.run_sql('''
        alter table shot add primary key (id);
        ''')

    def upgrade_v2_4_0_a01_007(my):
        my.run_sql('''
        alter table shot drop constraint shot_pkey;
        ''')


    def upgrade_v2_4_0_a01_006(my):
        my.run_sql('''
        create unique index naming_code_idx on naming (code);
        ''')

    def upgrade_v2_4_0_a01_005(my):
        my.run_sql('''
        alter table naming add column code varchar(256);
        ''')


    def upgrade_v2_4_0_a01_004(my):
        my.run_sql('''
        create unique index pipeline_code_idx on pipeline (code);
        ''')

    def check_v2_4_0_a01_003(my):
        my.table_exists("pipeline") 

    def upgrade_v2_4_0_a01_003(my):
        my.run_sql('''
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


    def upgrade_v2_4_0_a01_002(my):
        my.run_sql('''
        create unique index widget_config_code_idx on widget_config (code);
        ''')


    def upgrade_v2_4_0_a01_001(my):
        my.run_sql('''
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


    #
    # 2.2.0.rc03
    #
    def upgrade_v2_2_0_rc03_003(my):
        my.run_sql('''
        CREATE INDEX texture_asset_code_idx ON texture(asset_code);
        ''')

    def upgrade_v2_2_0_rc03_002(my):
        my.run_sql('''
        CREATE INDEX texture_code_idx ON texture(code);
        
        ''')

    def upgrade_v2_2_0_rc03_001(my):
        my.run_sql('''
        ALTER TABLE layer ADD COLUMN sort_order integer;
        ''')
    
    #
    # 2.1.0.b01
    #

    def upgrade_v2_1_0_b01_009(my):
        my.run_sql('''
        ALTER TABLE plate ADD COLUMN file_range text;
        ''')


    def upgrade_v2_1_0_b01_008(my):
        my.run_sql('''
        ALTER TABLE plate ADD COLUMN client_name varchar(256);
        ''')


    def upgrade_v2_1_0_b01_007(my):
        my.run_sql('''
        ALTER TABLE plate ADD COLUMN link text;
        ''')



    def upgrade_v2_1_0_b01_006(my):
        my.run_sql('''
        ALTER TABLE plate ADD COLUMN login varchar(256);
        ''')


    def upgrade_v2_1_0_b01_005(my):
        my.run_sql('''
        ALTER TABLE plate ADD COLUMN name varchar(256);
        ''')


    def upgrade_v2_1_0_b01_004(my):
        my.run_sql('''
        ALTER TABLE plate ADD COLUMN search_id int4;
        ''')

    def upgrade_v2_1_0_b01_003(my):
        my.run_sql('''
        ALTER TABLE plate ADD COLUMN search_type varchar(256);
        ''')


    def upgrade_v2_1_0_b01_002(my):
        my.run_sql('''
        ALTER TABLE render ADD COLUMN pipeline_code varchar(256);
        ''')

    def upgrade_v2_1_0_b01_001(my):
        my.run_sql('''
        ALTER TABLE render ADD COLUMN link text;
        ''')


    #
    # 2.1.0.a01
    #
    """
    def upgrade_v2_1_0_a01_001(my):
        my.run_sql('''
        CREATE TABLE snapshot_type (
            id integer NOT NULL,
            code character varying(256),
            pipeline_code text,
            "timestamp" timestamp without time zone DEFAULT now(),
            "login" character varying(256),
            s_status character varying(30),
            relpath text,
            refile text,
            project_code character varying(256),
            subcontext text,
            snapshot_flavor text
        );
        ''')
    """


    #
    # 2.1.0.a01
    #
    def upgrade_v2_1_0_a01_001(my):
        my.run_sql('''
        ALTER TABLE session_contents ADD COLUMN session text;
        ''')

    def upgrade_v2_0_0_b03_001(my):
        my.run_sql('''
        ALTER TABLE asset alter column code TYPE varchar(256); 
        ''')


    #
    # 2.0.0.b01
    #
    def upgrade_v2_0_0_b01_001(my):
        my.run_sql('''
        ALTER TABLE instance ADD COLUMN code VARCHAR(256);
        ''')

    #
    # 1.9.1.a07
    #
    def upgrade_v1_9_1_a06_016(my):
        my.run_sql('''
        ALTER TABLE render ADD COLUMN name varchar(256);
        ''')


    def upgrade_v1_9_1_a06_015(my):
        my.run_sql('''
        ALTER TABLE render RENAME COLUMN context to type;
        ''')

    def upgrade_v1_9_1_a07_014(my):
        my.run_sql('''
        ALTER TABLE render ALTER COLUMN login DROP NOT NULL;
        ''')


    def upgrade_v1_9_1_a07_013(my):
        my.run_sql('''
        ALTER TABLE naming ADD COLUMN context varchar(256);
        ''')


    def upgrade_v1_9_1_a07_012(my):
        my.run_sql('''
        ALTER TABLE naming ADD COLUMN snapshot_type varchar(256);
        ''')




    def upgrade_v1_9_1_a07_011(my):
        my.run_sql('''
        CREATE UNIQUE INDEX render_code_idx on render (code);
        ''')




    def upgrade_v1_9_1_a07_010(my):
        my.run_sql('''
        ALTER TABLE render ADD COLUMN type varchar(256);
        ''')



    def upgrade_v1_9_1_a07_009(my):
        my.run_sql('''
        ALTER TABLE render RENAME COLUMN snapshot_code to _snapshot_code;
        ''')



    def upgrade_v1_9_1_a07_008(my):
        my.run_sql('''
        ALTER TABLE render RENAME COLUMN snapshot to _snapshot;
        ''')



    def upgrade_v1_9_1_a07_007(my):
        my.run_sql('''
        ALTER TABLE render RENAME COLUMN file_range to _file_range;
        ''')



    def upgrade_v1_9_1_a07_006(my):
        my.run_sql('''
        ALTER TABLE render RENAME COLUMN session to _session;
        ''')

    def upgrade_v1_9_1_a07_005(my):
        my.run_sql('''
        ALTER TABLE render RENAME COLUMN version to _version;
        ''')


    def upgrade_v1_9_1_a07_003(my):
        my.run_sql('''
        ALTER TABLE render RENAME COLUMN images to _images;
        ''')




    def upgrade_v1_9_1_a07_002(my):
        my.run_sql('''
        ALTER TABLE plate ADD COLUMN pipeline_code varchar(256);
        ''')

    def upgrade_v1_9_1_a07_001(my):
        my.run_sql('''
        CREATE UNIQUE INDEX plate_code_idx on plate (code);
        ''')

    #
    # 1.9.1.a06
    #

    def upgrade_v1_9_1_a06_002(my):
        my.run_sql('''
        ALTER TABLE render add column context varchar(256);
        ''')

    def upgrade_v1_9_1_a06_001(my):
        my.run_sql('''
        ALTER TABLE render add column code varchar(256);
        ''')


    def upgrade_v1_9_1_a04_002(my):
        my.run_sql('''
        ALTER TABLE asset add column short_code varchar(256);
        ''')

    def upgrade_v1_9_1_a04_001(my):
        my.run_sql('''
        ALTER TABLE shot add column short_code varchar(256);
        ''')


    def upgrade_v1_9_1_a02_003(my):
        my.run_sql('''
        ALTER TABLE texture alter column code TYPE varchar(256);
        ''')

    def upgrade_v1_9_1_a02_002(my):
        my.run_sql('''
        ALTER TABLE shot_texture alter column code TYPE varchar(256);
        ''')

    def upgrade_v1_9_1_a02_001(my):
        my.run_sql('''
        alter table plate add column code varchar(256);
        ''')


    def upgrade_v1_9_0_a1_005(my):
        my.run_sql('''
        insert into prod_setting (key, value, description, type, category) values ('render_job_type', 'tacticsample', 'Sample Job Type', 'sequence', 'Render');
        ''')

    def upgrade_v1_9_0_a1_005(my):
        my.run_sql('''
        CREATE TABLE custom_property (
            id serial NOT NULL,
            search_type varchar(256),
            name varchar(256),
            description text,
            login varchar(256),
            PRIMARY KEY (id)
        );
        ''') 


    def upgrade_v1_9_0_a1_004(my):
        my.run_sql('''
        INSERT INTO prod_setting ("category", "key", value, description, "type", search_type) VALUES ('Naming', 'use_name_as_asset_code', 'false', 'Use name as the asset code', 'sequence', 'prod/asset');
        ''')


    def upgrade_v1_9_0_a1_003(my):
        my.run_sql('''
        update prod_setting set category = 'General' where category is NULL;
        ''')

    def upgrade_v1_9_0_a1_002(my):
        my.run_sql('''
        ALTER TABLE prod_setting ADD COLUMN category varchar(256);
        ''')


   

    def upgrade_v1_7_0_rc1_003(my):
        my.run_sql('''
        ALTER TABLE sequence ADD CONSTRAINT episode_code_fkey FOREIGN KEY (episode_code) REFERENCES episode(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;
        ''')

    def upgrade_v1_7_0_rc1_002(my):
        my.run_sql('''
        ALTER TABLE sequence add column episode_code varchar(256);
        ''')

    def upgrade_v1_7_0_rc1_001(my):
        my.run_sql('''
        CREATE TABLE episode (
        id serial NOT NULL,
        code character varying(256) NOT NULL,
        description text,
        "timestamp" timestamp without time zone DEFAULT now(),
        s_status character varying(30),
        sort_order smallint,
        CONSTRAINT episode_code_unique UNIQUE(code)
);
        ''')

    def upgrade_v1_6_0_rc1_001(my):
        my.run_sql('''
        INSERT INTO prod_setting ("key", value, description, "type", search_type) VALUES ('notes_asset_prod_context', 'model|uv_layout|shader|texture|rig', 'notes context for Asset Pipeline', 'sequence', 'sthpw/note');
        ''')
   

    

    

    def upgrade_v1_6_0_b2_001(my):
        my.run_sql('''
        CREATE TABLE sequence_instance (
            id serial NOT NULL,
            sequence_code character varying(30) NOT NULL,
            asset_code character varying(100) NOT NULL,
            "timestamp" timestamp without time zone DEFAULT now(),
            status text,
            "type" character varying(30)
        );
        ''')


    def upgrade_20080110(my):
        my.run_sql('''
        ALTER TABLE render ADD COLUMN s_status varchar(30);
        ''')

    def upgrade_20080103(my):
        my.run_sql('''
        ALTER TABLE texture ALTER COLUMN code TYPE varchar(256);
        ''')


    def upgrade_20071121(my):
        # adding a priority column for Omnilab
        # This should be handled by custom properties
        my.run_sql('''
        ALTER TABLE shot ADD COLUMN priority varchar(30);
        ''')

        my.run_sql('''
        INSERT INTO prod_setting (description, key, value, type) values ('Shot Priority', 'shot_priority', 'high|med|low', 'sequence');
        ''')
    

    def upgrade_20071116(my):
        my.run_sql('''
        -- take milestone_code out from invisible elements
        UPDATE prod_setting set value='priority' where key='invisible_elements' and search_type='sthpw/task';
        ''')


    def upgrade_20071112(my):
        my.run_sql('''
        CREATE TABLE custom_property (
            id serial NOT NULL,
            search_type varchar(256),
            name varchar(256),
            description text,
            login varchar(256),
            PRIMARY KEY (id)
        );
        ''')


    
    def upgrade_20071007(my):
        my.run_sql('''
        ALTER TABLE layer ADD COLUMN s_status varchar(30);
        ''')

   
    def upgrade_20071002(my):
        my.run_sql('''
        ALTER TABLE shot rename column pipeline to pipeline_code;
        ''')

    def upgrade_20070922(my):
        my.run_sql('''
        CREATE TABLE render_policy (
            id serial NOT NULL,
            code character varying(30),
            description text,
            width int2,
            height int2,
            frame_by int2,
            extra_settings text,
            PRIMARY KEY (id)
        );
        ''')



    def upgrade_20070912(my):
        my.run_sql('''
        CREATE TABLE shot_audio (
            id serial NOT NULL,
            title character varying(30),
            shot_code character varying(100),
            PRIMARY KEY (id),
            CONSTRAINT shot_code_fkey FOREIGN KEY (shot_code)
              REFERENCES shot (code) 
              ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED
        );
        ''')

    def upgrade_20070903(my):
        my.run_sql('''
            ALTER TABLE ONLY storyboard
            ADD CONSTRAINT storyboard_pkey PRIMARY KEY (id);
        ''')

    def upgrade_20070817(my):
        my.run_sql('''
        ALTER TABLE script ADD PRIMARY KEY (id);
        ''')

    def upgrade_20070719(my):
        my.run_sql('''
        ALTER TABLE cut_sequence add column sequence_code character varying(100);
        ALTER TABLE cut_sequence ADD CONSTRAINT sequence_code_fkey FOREIGN KEY (sequence_code) REFERENCES sequence(code) ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;
        ''')

    def upgrade_20070706(my):
        my.run_sql('''
        ALTER TABLE script ADD COLUMN sequence_code varchar(30);
        ''')
        my.run_sql('''
        ALTER TABLE script ADD COLUMN stage varchar(256);
        ''')
        my.run_sql('''
        ALTER TABLE script ADD COLUMN title text;
        ''')
        my.run_sql('''
        ALTER TABLE script ADD COLUMN author varchar(256);
        ''')
        my.run_sql('''
        ALTER TABLE script DROP COLUMN shot_code;
        ''')




    def upgrade_20070628(my):
        my.run_sql('''
        CREATE TABLE cut_sequence
        (
          id serial NOT NULL,
          shot_code character varying(30),
          "type" character varying(100),
          "timestamp" timestamp without time zone DEFAULT now(),
          s_status character varying(30),
          description text,
          CONSTRAINT cut_sequence_pkey PRIMARY KEY (id),
          CONSTRAINT shot_code_fkey FOREIGN KEY (shot_code)
              REFERENCES shot (code) MATCH SIMPLE
              ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED
        ) 
        ''')

    def upgrade_20070622(my):
        my.run_sql('''
        CREATE TABLE naming (
            id serial PRIMARY KEY,
            search_type varchar(100),
            dir_naming text,
            file_naming text
        );
        ''')


    def upgrade_20070621(my):
        my.run_sql('''
        alter table shot add column scan_status varchar(256); 
        ''')
        my.run_sql('''
        alter table shot add column type varchar(256); 
        ''')

    def upgrade_20070605(my):
        my.run_sql('''
        ALTER TABLE submission ADD COLUMN status varchar(100);
        ''')


    def upgrade_20070526(my):
        my.run_sql('''
        ALTER TABLE plate add column description text;
        ''')

    def upgrade_20070522(my):
        my.run_sql('''
        ALTER TABLE shot_texture add column search_type varchar(256);
        ALTER TABLE shot_texture add column search_id int4;
        ''')



    def upgrade_20070522(my):
        my.run_sql('''
        CREATE TABLE shot_texture (
            id serial NOT NULL,
            description text,
            shot_code character varying(50),
            category character varying(200),
            "timestamp" timestamp without time zone DEFAULT now(),
            snapshot text,
            s_status character varying(32),
            code character varying(50),
            pipeline_code character varying(256),
            asset_context character varying(30)
        );
        ''')


    def upgrade_20070516(my):
        my.run_sql('''
        ALTER TABLE shot ADD COLUMN frame_in int2;
        ALTER TABLE shot ADD COLUMN frame_out int2;
        ALTER TABLE shot ADD COLUMN frame_note text;
        ''')


    def upgrade_20070430(my):
        my.run_sql('''
        ALTER TABLE art_reference ADD COLUMN "timestamp" timestamp DEFAULT now();
        ''')


    def upgrade_20070413(my):
        my.run_sql('''
        alter table prod_setting add constraint key_search_type_unique UNIQUE
        (key, search_type);
        ''')

    def upgrade_20070316(my):
        my.run_sql('''
        alter table submission add column artist varchar(256);
        ''')

    def upgrade_20070210(my):
        my.run_sql('''
        alter table texture add column asset_context varchar(30);
        ''')

    def upgrade_20070206(my):
        my.run_sql('''
insert into prod_setting (key, value, description, type, search_type) values ('bin_label', 'client|review', 'Types of bins', 'sequence', 'prod/bin');

insert into prod_setting (key, value, description, type, search_type) values ('notes_preprod_context', 'client kick off|internal kick off', 'Types of reproduction notes', 'sequence', 'prod/shot');

        ''')


    def upgrade_20070203(my):
        my.run_sql('''
        CREATE TABLE camera (
            id serial PRIMARY KEY,
            shot_code varchar(30),
            description text,
            "timestamp" timestamp default now(),
            s_status varchar(30)
        );
        ''')

        """
        my.run_sql('''
        CREATE TABLE camera (
            id serial PRIMARY KEY,
            shot_code varchar(30),
 
            lab_roll varchar(30),
            roll varchar(30),
            height varchar(30),
            distance varchar(30),
            aspect_ratio varchar(30),


            fps varchar(30),
            filter varchar(30),
            focus varchar(256),

            slate varchar(30),
            perf int2,
            take int2,

            "timestamp" timestamp default now(),
            s_status varchar(30)
        );
        ''')
        """


    def upgrade_20070129(my):
        my.run_sql('''
        ALTER TABLE storyboard ADD CONSTRAINT shot_code_fkey FOREIGN KEY (shot_code) REFERENCES shot(code) ON UPDATE CASCADE  ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;

        ALTER TABLE instance DROP constraint "$1";
        ALTER TABLE instance DROP constraint "$2";
        ALTER TABLE instance ADD CONSTRAINT asset_code_fkey FOREIGN KEY (asset_code) REFERENCES asset(code) ON UPDATE CASCADE  ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;
        ALTER TABLE instance ADD CONSTRAINT shot_code_fkey FOREIGN KEY (shot_code) REFERENCES shot(code) ON UPDATE CASCADE  ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;

        ALTER TABLE plate ADD CONSTRAINT shot_code_fkey FOREIGN KEY (shot_code) REFERENCES shot(code) ON UPDATE CASCADE  ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;
        ''')


    def upgrade_20070126(my):
        my.run_sql('''
        alter table bin add column label varchar(100);
        ''')

    def upgrade_20070123(my):
        my.run_sql('''
        INSERT INTO prod_setting (key,value,type,search_type, description) values ('texture/category','texture|mattepainting|concept', 'sequence', 'prod/texture', 'Various Types of 2D Assets')
        ''')

    def upgrade_20070117(my):
        my.run_sql('''
        ALTER TABLE shot ADD COLUMN complexity int2;

        INSERT INTO prod_setting (key, value, description, type, search_type)
        VALUES ('bin_type', 'anim|tech|review|final|client', 'The different type of bins', 'sequence', 'prod/bin');
        ''')

    def upgrade_20070114(my):
        my.run_sql('''

        CREATE TABLE plate (
            id serial PRIMARY KEY,
            shot_code varchar(30),
            type varchar(30),
            "timestamp" timestamp default now(),
            s_status varchar(30)
        );


        ''')



    def upgrade_20070112(my):
        my.run_sql('''
        ALTER TABLE script DROP COLUMN episode_code;
        ALTER TABLE script DROP COLUMN artist;

        ALTER TABLE script ADD COLUMN code varchar(30);
        ALTER TABLE script ADD COLUMN description text;
        ''')


    def upgrade_20061222(my):
        my.run_sql('''
        -- add some columns to the prod_setting table
        ALTER TABLE prod_setting ADD COLUMN description text;
        ALTER TABLE prod_setting ADD COLUMN type varchar(30);
        ALTER TABLE prod_setting ADD COLUMN search_type varchar(200);
         ''')


    def upgrade_20061219(my):
        my.run_sql('''
         -- add a sort order to shot
         ALTER TABLE shot ADD COLUMN sort_order int2;
         ''')


    def upgrade_20061207(my):
        my.run_sql('''
         -- add a submission table for editorial purpose
        CREATE TABLE submission (
            id serial PRIMARY KEY,
            search_type varchar(200),
            search_id int4,
            snapshot_code varchar(30),
            context varchar(100),
            version int4,
            description text,
            login varchar(30),
            "timestamp" timestamp default now(),
            s_status varchar(30)
        );

        CREATE TABLE bin (
            id serial PRIMARY KEY,
            code varchar(256),
            description text,
            type varchar(100),
            s_status varchar(30)
        );

        CREATE TABLE submission_in_bin
        (
          id serial PRIMARY KEY,
          submission_id int4 NOT NULL,
          bin_id int4 NOT NULL,
          CONSTRAINT submission_in_bin_bin_id_fkey FOREIGN KEY (bin_id)
              REFERENCES bin (id) 
              ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
          CONSTRAINT submission_in_bin_submission_id_fkey FOREIGN KEY (submission_id)
              REFERENCES submission (id) 
              ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
        ); 
        alter table submission_in_bin add constraint submission_id_bin_id_key 
            UNIQUE (submission_id, bin_id);   
        ''')

    def upgrade_20061123(my):

        my.run_sql('''
        -- add a sort order to sequences
        alter table sequence add column sort_order int2;

        -- drop the episode and artist constraint to storyboards
        alter table storyboard drop column episode_code;
        alter table storyboard drop column artist;

        alter table storyboard add column code varchar(30);
        alter table storyboard add column shot_code varchar(30);
        alter table storyboard add column description text;
        '''
         )

    def upgrade_20061122(my):
        my.run_sql('''
        -- now centralised in sthpw database
        drop table timecard;

        -- change to pipeline code
        alter table asset rename column pipeline to pipeline_code;
        ''')   


    def upgrade_20061110(my):
        my.run_sql('''
        alter table asset rename column pipeline to pipeline_code;
        ''')   

    def upgrade_20061109(my):
        my.run_sql('''
        alter table shot add column sequence_code varchar(30);
        ''')

    def upgrade_20061102(my):
        my.run_sql('''
        -- add a keywords column to the art_reference table --
        alter table art_reference add column keywords text;
        ''')

    def upgrade_20061025(my):
        my.run_sql('''
        -- add a must-have entry set_item to asset_type
        INSERT INTO asset_type (code, description) VALUES('set_item', 
        'an item in a set');
        ''')


    def upgrade_20060907(my):
        my.run_sql('''
        ALTER TABLE texture ADD COLUMN pipeline varchar(30);
        ''')






