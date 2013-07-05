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

__all__ = ['SthpwUpgrade']


from base_upgrade import *


class SthpwUpgrade(BaseUpgrade):

    def upgrade_v3_6_0_v07_MSQL_002(my):
        my.run_sql('''CREATE unique INDEX ticket_unique ON transaction_state(ticket);
''')
    def upgrade_v3_6_0_v07_MSQL_001(my):
        my.run_sql('''CREATE unique INDEX ticket_unique ON ticket(ticket);''')


    def upgrade_v3_6_0_rc02_001(my):
        my.run_sql('''ALTER TABLE wdg_settings alter column login varchar(100);''')


    #
    # 3.6.0.b02
    #
    def upgrade_v3_6_0_b02_003(my):
        my.run_sql('''CREATE UNIQUE INDEX "login_code_idx" ON [login] ("code");''')

    def upgrade_v3_6_0_b02_002(my):
        my.run_sql('''   UPDATE [login] set code = login where code is NULL;''')

    def upgrade_v3_6_0_b02_001(my):
        my.run_sql('''ALTER TABLE login ADD code varchar(512);''')


    #
    # 3.6.0.b01
    #
    def upgrade_v3_6_0_b01_016(my):
        my.run_sql('''UPDATE search_object set class_name = 'pyasm.biz.Milestone' where search_type = 'sthpw/milestone';''')


    def upgrade_v3_6_0_b01_015(my):
        my.run_sql('''
        ALTER TABLE search_object ADD color varchar(32);
        ''')

    def upgrade_v3_6_0_b01_014(my):
        my.run_sql('''ALTER TABLE ticket ADD category varchar(256);''')


    def upgrade_v3_6_0_b01_013(my):
        my.run_sql('''ALTER TABLE work_hour ADD status varchar(256);''')

    def upgrade_v3_6_0_b01_012(my):
        my.run_sql('''ALTER TABLE task ALTER column pipeline_code varchar(256);''')

    def upgrade_v3_6_0_b01_011(my):
        my.run_sql('''
        UPDATE search_object SET title = 'Preference List' WHERE search_type = 'sthpw/pref_list';
        ''')


    def upgrade_v3_6_0_b01_010(my):
        my.run_sql('''
        UPDATE search_object SET title = 'Notification Log' WHERE search_type = 'sthpw/notification_log';
        ''')


    def upgrade_v3_6_0_b01_009(my):
        my.run_sql('''
        UPDATE search_object SET title = 'Files' WHERE search_type = 'sthpw/file';
        ''')


    def upgrade_v3_6_0_b01_008(my):
        my.run_sql('''
        UPDATE search_object SET title = 'Access Rules' WHERE search_type = 'sthpw/access_rule';
        ''')



    def upgrade_v3_6_0_b01_007(my):
        my.run_sql('''
        UPDATE search_object SET title = 'SObject Cache' WHERE search_type = 'sthpw/cache';
        ''')


    def upgrade_v3_6_0_b01_006(my):
        my.run_sql('''DELETE FROM pref_list where "key" = 'skin';''')

    def upgrade_v3_6_0_b01_005(my):
        my.run_sql('''DELETE FROM pref_setting where "key" = 'skin';''')



    def upgrade_v3_6_0_b01_004(my):
        my.run_sql('''
        INSERT INTO pref_list ("key",description,options,"type",category,title) VALUES ('palette','Color Palette to determine the look and feel','Aqua|Dark|Silver|Bright|Origami|Bon Noche|Aviator','sequence','display','Color Palette');
        ''')


    def upgrade_v3_6_0_b01_003(my):
        my.run_sql('''UPDATE pref_list SET category = 'debug' where "key" = 'js_logging_level';''')

    def upgrade_v3_6_0_b01_002(my):
        my.run_sql('''UPDATE pref_list SET category = 'debug' where "key" = 'debug';''')




    def upgrade_v3_6_0_b01_001(my):
        my.run_sql('''ALTER TABLE "project" ADD "palette" varchar(256)''')


    #
    # 3.6.0.a02
    #
    def upgrade_v3_6_0_a02_001(my):
        my.run_sql('''ALTER TABLE work_hour ADD "task_code" varchar(256)''')


    #
    # 3.6.0.a01
    #
    def upgrade_v3_6_0_a01_007(my):
        my.run_sql('''ALTER TABLE "project" ADD "category" varchar(256)''')

    def upgrade_v3_6_0_a01_006(my):
        my.run_sql('''ALTER TABLE "project" ADD "is_template" BIT''')


    def upgrade_v3_6_0_a01_005(my):
        my.run_sql('''INSERT INTO "search_object" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('sthpw/sobject_list', 'sthpw', 'SObject List', 'sthpw', 'sobject_list', 'pyasm.search.SObject', 'SObject List', 'public');
        ''')



    def upgrade_v3_6_0_a01_004(my):
        my.run_sql('''
        CREATE TABLE sobject_list (
            id INT IDENTITY,
            search_type varchar(256),
            search_id integer,
            keywords text,
            [timestamp] datetime2(6) DEFAULT (getdate()),
            project_code varchar(256)
        );
        ''')



    def upgrade_v3_6_0_a01_003(my):
        my.run_sql('''INSERT INTO "search_object" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('config/ingest_session', 'config', 'Ingest Sessions', '{project}', 'spt_ingest_session', 'pyasm.search.SObject', 'Ingest Sessions', 'public');
        ''')
    


    def upgrade_v3_6_0_a01_002(my):
        my.run_sql('''INSERT INTO "search_object" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('sthpw/plugin', 'sthpw', 'Plugins', 'sthpw', 'spt_plugin', 'pyasm.search.SObject', 'Plugins', 'public');
        ''')



    def upgrade_v3_6_0_a01_001(my):
        my.run_sql('''INSERT INTO "search_object" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('config/ingest_rule', 'config', 'Ingest Rules', '{project}', 'spt_ingest_rule', 'pyasm.search.SObject', 'Ingest Rules', 'public');
        ''')

    #
    # 3.5.0.rc03
    #

    def upgrade_v3_5_0_v01_004(my):
        my.run_sql('''
        ALTER TABLE task drop constraint "pipeline_code_foreign";
        ''')


    def upgrade_v3_5_0_v01_003(my):
        my.run_sql('''
        CREATE INDEX "notification_log_timestamp_idx" ON notification_log (timestamp);
        ''')


    #
    # 3.5.0.rc03
    #
    def upgrade_v3_5_0_v01_003(my):
        my.run_sql('''
        CREATE INDEX "notification_log_timestamp_idx" ON notification_log (timestamp);
        ''')

    def upgrade_v3_5_0_v01_002(my):
        my.run_sql('''
        ALTER TABLE snapshot alter column lock_login DROP not null;
        ''')

    def upgrade_v3_5_0_v01_001(my):
        my.run_sql('''
        UPDATE search_object set class_name='pyasm.search.SObject' where search_type='prod/plate';
        ''')

    def upgrade_v3_5_0_rc03_004(my):
        my.run_sql('''
        UPDATE search_object set class_name='pyasm.biz.WorkHour' where search_type='sthpw/work_hour';
        ''')

    def upgrade_v3_5_0_rc03_003(my):
        my.run_sql('''
        ALTER TABLE pref_setting drop constraint pref_setting_login_fkey CASCADE;
        ''')


    def upgrade_v3_5_0_rc03_002(my):
        my.run_sql('''
        ALTER TABLE wdg_settings drop constraint wdg_settings_project_code_fkey CASCADE;
        ''')

    def upgrade_v3_5_0_rc03_001(my):
        my.run_sql('''
        ALTER TABLE wdg_settings drop constraint wdg_settings_login_fkey CASCADE;
        ''')
 

    #
    # 3.5.0.rc01
    #

    def upgrade_v3_5_0_rc01_001(my):
        my.run_sql('''
        UPDATE "note" set process = context where process is NULL;
        ''')



    def upgrade_v3_1_0_rc01_001(my):
        my.run_sql('''
        ALTER TABLE "notification" ADD "data" text;
        ''')


    #
    # 3.1.0.b09
    #
    def upgrade_v3_1_0_b09_001(my):
        my.run_sql('''
        ALTER TABLE "notification" ADD "listen_event" VARCHAR(256);
        ''')


    #
    # 3.1.0.b06
    #
    def upgrade_v3_1_0_b06_002(my):
        my.run_sql('''
        ALTER TABLE "wdg_settings" DROP constraint "wdg_settings_project_code_fkey";
        ''')

    def upgrade_v3_1_0_b06_001(my):
        my.run_sql('''
        ALTER TABLE "wdg_settings" DROP constraint "wdg_settings_login_fkey";
        ''')


    def upgrade_v3_1_0_b03_001(my):
        my.run_sql('''
        CREATE INDEX "status_log_search_type_search_id_idx" ON status_log (search_type, search_id)
        ''') 

    #
    # 3.1.0.b01
    #
    def upgrade_v3_1_0_b01_001(my):
        my.run_sql('''
        ALTER TABLE search_object ADD color varchar(32);
        ''')



    #
    # 3.1.0.a02
    #
    def upgrade_v3_1_0_a02_007(my):
        my.run_sql('''INSERT INTO "search_object" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('config/pipeline', 'config', 'Pipeline', '{project}', 'spt_pipeline', 'pyasm.biz.Pipeline', 'Pipeline', 'public');
        ''')


    def upgrade_v3_1_0_a02_006(my):
        my.run_sql('''
        ALTER TABLE notification ADD process varchar(256);
        ''')


    def upgrade_v3_1_0_a02_005(my):
        my.run_sql('''
        ALTER TABLE notification ADD title varchar(256);
        ''')


    def upgrade_v3_1_0_a02_004(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD process varchar(256);
        ''')




    def upgrade_v3_1_0_a02_003(my):
        my.run_sql('''
        ALTER TABLE pipeline ADD color varchar(32);
        ''')


    def upgrade_v3_1_0_a02_002(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD lock_date datetime2(6);
        ''')

    def upgrade_v3_1_0_a02_001(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD lock_login varchar(256);
        ''')




    #
    # 3.1.0.a01
    #
    def upgrade_v3_1_0_a01_001(my):
        my.run_sql('''
        ALTER TABLE queue ADD host varchar(256);
        ''')



    #
    # 3.0.0.rc03
    #
    def upgrade_v3_0_0_rc03_002(my):
        my.run_sql('''
        CREATE INDEX "note_search_type_search_id_idx" ON note (search_type, search_id)
        ''') 

    def upgrade_v3_0_0_rc03_001(my):
        my.run_sql('''
        ALTER TABLE "trigger" ALTER COLUMN event varchar(256);
        ''')

   
    #
    # 3.0.0.b01
    #
    # Commenting out for now
    #def upgrade_v3_0_0_b01_005(my):
    #    my.run_sql('''
    #    INSERT INTO "search_object" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('config/bid', 'config', 'Bidding', '{project}', 'spt_bid', 'pyasm.search.SObject', 'Bidding', 'public');
    #    ''')



    def upgrade_v3_0_0_b01_004(my):
        my.run_sql('''
        INSERT INTO "search_object" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('sthpw/work_hour', 'sthpw', 'Work Hours', 'sthpw', 'work_hour', 'pyasm.search.SObject', 'Work Hours', 'public');
        ''')



    def upgrade_v3_0_0_b01_003(my):
        my.run_sql('''
        CREATE TABLE work_hour (
            id INT IDENTITY,
            code varchar(256),
            project_code varchar(256),
            description text,
            category varchar(256),
            login varchar(256),
            day datetime2(6),
            start_time datetime2(6),
            end_time datetime2(6),
            straight_time float,
            over_time float,
            search_type varchar(256),
            search_id int4
        );
        ''')


 
    def upgrade_v3_0_0_b01_002(my):
        my.run_sql('''
        INSERT INTO "search_object" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('config/process', 'config', 'Processes', '{project}', 'spt_process', 'pyasm.search.SObject', 'Processes', 'public')
        ''')



    def upgrade_v3_0_0_b01_001(my):
        my.run_sql('''
        INSERT INTO "search_object" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('config/trigger', 'config', 'Triggers', '{project}', 'spt_trigger', 'pyasm.biz.TriggerSObj', 'Triggers', 'public')
        ''')


    #
    # 2.7.0.a02
    #
    def upgrade_v2_7_0_a01_002(my):
        my.run_sql('''
        CREATE INDEX "snapshot_search_type_search_id_idx" ON snapshot (search_type, search_id)
        ''')


    #
    # 2.7.0.a01
    #
    def upgrade_v2_7_0_a01_001(my):
        my.run_sql('''
        INSERT INTO "search_object" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('config/plugin', 'config', 'Plugin', '{project}', 'spt_plugin', 'pyasm.search.SObject', 'Plugin', 'public'); 
        ''')

    def upgrade_v2_6_0_v01_002(my):
        my.run_sql('''
        CREATE INDEX "task_search_type_search_id_idx" ON task (search_type, search_id);
        ''')


    def upgrade_v2_6_0_v01_001(my):
        my.run_sql('''
        CREATE INDEX "snapshot_search_type_search_id_idx" ON snapshot (search_type, search_id);
        ''')

    #
    # 2.6.0.rc01
    #
    def upgrade_v2_6_0_rc01_002(my):
        my.run_sql('''
        INSERT INTO pref_list ("key",description,options,"type",category,title) VALUES ('quick_text','Quick text for Note Sheet','','string','general','Quick Text');
        ''')


    def upgrade_v2_6_0_rc01_001(my):
        my.run_sql('''
        ALTER TABLE "trigger" ADD mode varchar(256);
        ''')

    #
    # 2.6.0.b05
    #
    def upgrade_v2_6_0_b05_002(my):
        my.run_sql('''
        ALTER TABLE "trigger" ALTER COLUMN class_name DROP NOT NULL;
        ''')



    def upgrade_v2_6_0_b05_001(my):
        my.run_sql('''
        ALTER TABLE "trigger" ADD script_path varchar(256);
        ''')




    #
    # 2.6.0.b03
    #
    def upgrade_v2_6_0_b03_002(my):
        my.run_sql('''
        UPDATE snapshot set is_synced = 't' where is_synced is NULL;
        ''')


    def upgrade_v2_6_0_b03_001(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD is_synced BIT;
        ''')


    #
    # 2.6.0.b02
    #
    def upgrade_v2_6_0_b02_001(my):
        my.run_sql('''UPDATE snapshot set revision=0 where revision is NULL''');

    #
    # 2.6.0.b01
    #
    def upgrade_v2_6_0_b01_002(my):
        my.run_sql('''
        INSERT INTO "search_object" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('config/client_trigger', 'config', 'Client Trigger', '{project}', 'spt_client_trigger', 'pyasm.search.SObject', 'Client Trigger', 'public'); 
        ''')

    def upgrade_v2_6_0_b01_001(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('config/prod_setting', 'config', 'Production Settings', '{project}', 'prod_setting', 'pyasm.prod.biz.ProdSetting', 'Production Settings', 'public');
        ''')

        
    #
    # 2.6.0.a01 again
    #

    def upgrade_v2_6_0_a01_001(my):
        my.run_sql('''
        INSERT INTO "search_object" ("search_type", "namespace", "description", [database], "table_name", "class_name", "title", [schema]) VALUES ('config/url', 'config', 'Custom URL', '{project}', 'spt_url', 'pyasm.search.SObject', 'Custom URL', 'public');
        '''
        )
    def upgrade_v2_5_0_v02_002(my):
        my.run_sql('''
        ALTER TABLE pipeline DROP CONSTRAINT project_code_foreign;
        ''')



    def upgrade_v2_5_0_v01_001(my):
        my.run_sql('''
        DELETE FROM pref_setting where "key"='use_java_maya';
        '''
        )

    def upgrade_v2_5_0_v01_002(my):
        my.run_sql('''
        DELETE FROM pref_list where "key"='use_java_maya';
        '''
        )

    def upgrade_v2_5_0_v01_003(my):
        my.run_sql('''
        ALTER TABLE widget_config ADD category varchar(256);
        '''
        )
    #
    # 2.5.0.rc20
    #
    def upgrade_v2_5_0_rc20_001(my):
        my.run_sql('''
        ALTER TABLE task ADD completion float;
        ''')

    def upgrade_v2_5_0_rc20_002(my):
        my.run_sql('''
        ALTER TABLE task ADD context varchar(256);
        ''')

    def upgrade_v2_5_0_rc20_003(my):
        my.run_sql('''
        CREATE TABLE cache (
            id INT IDENTITY,
            key varchar(256),
            mtime datetime2(6)
        );
        ''')

    def upgrade_v2_5_0_rc20_004(my):
        my.run_sql('''
        ALTER TABLE "notification" ADD "mail_to" text;
        ''')

    def upgrade_v2_5_0_rc20_005(my):
        my.run_sql('''
        ALTER TABLE "trigger" drop constraint trigger_class_name_event_unique CASCADE;
        ''')

    def upgrade_v2_5_0_rc20_006(my):
        my.run_sql('''
        ALTER TABLE "notification" ADD "mail_cc" text;
        ''')


    def upgrade_v2_5_0_rc20_007(my):
        my.run_sql('''
        ALTER TABLE "notification" ADD "mail_bcc" text;
        ''')




    def upgrade_v2_5_0_rc20_008(my):
        my.run_sql('''
        ALTER TABLE "trigger" ADD constraint trigger_class_name_event_project_unique UNIQUE(class_name, event, project_code);
        ''')

    #
    # 2.5.0.rc19
    #
 
    def upgrade_v2_5_0_rc19_001(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/cache', 'sthpw', 'Cache', 'sthpw', '{public}.cache', 'pyasm.search.SObject', '', 'public');        
        ''')

    def upgrade_v2_5_0_rc19_002(my):
        my.run_sql('''
        ALTER TABLE "trigger" drop constraint trigger_class_name_event_unique CASCADE;
        ''')


    def upgrade_v2_5_0_rc19_003(my):
        my.run_sql('''
        ALTER TABLE "trigger" ADD constraint trigger_class_name_event_project_unique UNIQUE(class_name, event, project_code);
        ''')

    #
    # 2.5.0.rc18
    #
    def upgrade_v2_5_0_rc18_001(my):
        my.run_sql('''
        ALTER TABLE [file] alter column file_name varchar(512) null; 
        ''')
    def upgrade_v2_5_0_rc18_002(my):
        my.run_sql('''
        ALTER TABLE file ADD base_type varchar(256); 
        ''')
    #
    # 2.5.0.rc16
    #
    def upgrade_v2_5_0_rc16_004(my):
        my.run_sql('''
        ALTER TABLE file ADD type varchar(256);
        ''')

    def upgrade_v2_5_0_rc16_003(my):
        my.run_sql('''
        ALTER TABLE login ADD license_type varchar(256);
        ''')


    def upgrade_v2_5_0_rc16_002(my):
        my.run_sql('''
        ALTER TABLE notification ADD subject text;
        ''')

    def upgrade_v2_5_0_rc16_001(my):
        my.run_sql('''
        ALTER TABLE notification alter column code DROP NOT NULL;
        ''')

    #
    # 2.5.0.rc12_001
    #
    def upgrade_v2_5_0_rc12_001(my):
        my.run_sql('''
        ALTER TABLE notification ADD event varchar(256);
        ''')

    def upgrade_v2_5_0_rc09_002(my):
        my.run_sql('''
        CREATE INDEX file_file_name_idx ON file(file_name);
        ''')

    def upgrade_v2_5_0_rc09_001(my):
        my.run_sql('''
        ALTER TABLE login ALTER COLUMN password DROP NOT NULL; 
        ''')

    def upgrade_v2_5_0_rc08_001(my):
        my.run_sql('''
        UPDATE search_object set class_name='pyasm.biz.TriggerSObj' where search_type ='sthpw/trigger';
        ''')

    # 2.5.0.rc06
    def upgrade_v2_5_0_rc06_001(my):
        my.run_sql('''
        ALTER TABLE note ADD access varchar(256);
        ''')



    # 2.5.0.rc05
    def upgrade_v2_5_0_rc05_002(my):
        my.run_sql('''
        ALTER TABLE login ADD "department" varchar(256);
        ''')


    def upgrade_v2_5_0_rc05_001(my):
        my.run_sql('''
        ALTER TABLE login ADD "phone_number" varchar(32);
        ''')

  
    # 2.5.0.rc01
    def upgrade_v2_5_0_rc02_002(my):
        my.run_sql('''
        ALTER TABLE note ADD "sort_order" integer;
        ''')

    def upgrade_v2_5_0_rc02_001(my):
        my.run_sql('''
        ALTER TABLE "trigger" ADD "s_status" varchar(256);
        ''')

    def upgrade_v2_5_0_rc01_003(my):
        my.run_sql('''
        UPDATE pref_list set options = 'true' where key='use_java_maya';
        ''')
   
    def upgrade_v2_5_0_rc01_002(my):
        my.run_sql('''
        DELETE FROM pref_list where key='select_filter';
        ''')
    def upgrade_v2_5_0_rc01_001(my):
        my.run_sql('''
        DELETE FROM pref_setting where key='select_filter';
        ''')

    def upgrade_v2_5_0_b05_001(my):
        # NOTE: this gives a warning:
        #WARNING:  nonstandard use of \\ in a string literal
        #LINE 1: ...hot set project_code = substring(search_type from '=(\\w+)$'...
        my.run_sql('''
        UPDATE snapshot set project_code = substring(search_type from '=(\\w+)$');
        ''')
    # 2.5.0.b03

    def upgrade_v2_5_0_b03_003(my):
        my.run_sql('''
        ALTER TABLE snapshot_type ADD CONSTRAINT snapshot_type_code_unique UNIQUE (code);
        ''')

    def upgrade_v2_5_0_b03_002(my):
        my.run_sql('''
        ALTER TABLE snapshot_type ADD CONSTRAINT snapshot_type_pkey ;
        ''')

    def upgrade_v2_5_0_b03_001(my):
        my.run_sql('''
        ALTER TABLE snapshot_type drop CONSTRAINT snapshot_type_pkey;
        ''')
    # 2.5.0.b02

    def upgrade_v2_5_0_b02_005(my):
        my.run_sql('''
        CREATE INDEX snapshot_search_code_idx ON snapshot(search_code);
        ''')


    def upgrade_v2_5_0_b02_004(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD search_code varchar(256);
        ''')


    

    def upgrade_v2_5_0_b02_002(my):
        my.run_sql('''
        CREATE INDEX snapshot_project_code_idx ON snapshot(project_code);
        ''')


    def upgrade_v2_5_0_b02_001(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD project_code varchar(256);
        ''')
    #
    # 2.5.0.a01
    # 
    def upgrade_v2_5_0_a01_005(my):
        my.run_sql('''
        UPDATE search_object SET class_name = 'pyasm.prod.biz.AssetLibrary' where search_type='prod/asset_library';
        ''') 
   
    def upgrade_v2_5_0_a01_004(my):
        my.run_sql('''
        ALTER TABLE template alter column search_type drop not null;
        ''')

    def upgrade_v2_5_0_a01_003(my):
        my.run_sql('''
        ALTER TABLE template alter column code drop not null;
        ''')


    def upgrade_v2_5_0_a01_002(my):
        my.run_sql('''
        INSERT INTO pref_list ("key",description,options,"type",category,title) VALUES ('js_logging_level','Determines logging level used by Web Client Output Console Pop-up','CRITICAL|ERROR|WARNING|INFO|DEBUG','sequence','general','Web Client Logging Level');
        ''')

    def upgrade_v2_5_0_a01_001(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('config/custom_script', 'config', 'Custom Script', '{project}', 'custom_script', 'pyasm.search.SObject', 'Custom Script', 'public');
        ''')


    #
    # 2.4.0.a01
    # 
    def upgrade_v2_4_0_a01_013(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('config/naming', 'config', 'Naming', '{project}', '{public}.naming', 'pyasm.biz.Naming', '', 'public');
        ''')

    def upgrade_v2_4_0_a01_012(my):
        my.run_sql('''
        CREATE UNIQUE INDEX ticket_id_idx ON ticket;
        ''')


    def upgrade_v2_4_0_a01_011(my):
        my.run_sql('''
        CREATE UNIQUE INDEX transaction_state_ticket_idx ON transaction_state(ticket);
        ''')

    def upgrade_v2_4_0_a01_010(my):
        my.run_sql('''
        ALTER TABLE transaction_state ADD ;
        ''')




    def upgrade_v2_4_0_a01_009(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('config/pipeline', 'config', 'Pipelines', '{project}', 'pipeline', 'pyasm.biz.Pipeline', 'Pipelines', 'public');
        ''')


    def upgrade_v2_4_0_a01_008(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('config/widget_config', 'config', 'Widget Config', '{project}', 'widget_config', 'pyasm.search.WidgetDbConfig', 'Widget Config', 'public');
        ''')

    def upgrade_v2_4_0_a01_007(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/custom_script', 'sthpw', 'Custom Script', '{project}', 'custom_script', 'pyasm.search.SObject', 'Custom Script', 'public');
        ''')


    def upgrade_v2_4_0_a01_006(my):
        my.run_sql('''
        CREATE TABLE custom_script (
            id INT IDENTITY,
            code varchar(256),
            script text,
            login varchar(256),
            [timestamp] datetime2(6),
            s_status varchar(256)
        );
        ''')



    def upgrade_v2_4_0_a01_005(my):
        my.run_sql('''
        ALTER TABLE widget_config ADD code varchar(256);
        ''')


    def upgrade_v2_4_0_a01_004(my):
        my.run_sql('''
        ALTER TABLE widget_config alter column search_type drop not null;
        ''')

    def upgrade_v2_4_0_a01_003(my):
        my.run_sql('''
        ALTER TABLE widget_config alter column search_type type varchar(256);
        ''')

    def upgrade_v2_4_0_a01_002(my):
        my.run_sql('''
        ALTER TABLE widget_config alter column view type varchar(256);
        ''')

    def upgrade_v2_4_0_a01_001(my):
        my.run_sql('''
        ALTER TABLE widget_config ADD project_code varchar(256);
        ''')

    def upgrade_v2_2_0_rc03_002(my):
        my.run_sql('''
        ALTER TABLE "trigger" ADD constraint trigger_class_name_event_unique UNIQUE(class_name, event);
        ''')

    def upgrade_v2_2_0_rc03_001(my):
        my.run_sql('''
        ALTER TABLE "trigger" drop constraint trigger_class_name_key CASCADE;
        ''')

    def upgrade_v2_2_0_rc02_001(my):
        my.run_sql('''
        UPDATE search_object SET class_name = 'pyasm.prod.biz.AssetLibrary' where search_type='prod/asset_library';
        ''')

    #
    # 2.2.0.rc01
    #
    def upgrade_v2_2_0_rc01_001(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/snapshot_type', 'prod', 'Snapshot Type', '{project}', 'snapshot_type', 'pyasm.biz.SnapshotType', 'Snapshot Type', 'public');
        ''')

    #
    # 2.2.0.b01
    #
    def upgrade_v2_2_0_b01_005(my):
        my.run_sql('''
        ALTER TABLE transaction_state ADD constraint "transaction_state_unique"
        unique(ticket);
        ''')
    
    def upgrade_v2_2_0_b01_004(my):
        my.run_sql('''
        drop index "transaction_state_ticket_idx";
        ''')

    def upgrade_v2_2_0_b01_003(my):
        my.run_sql('''
        ALTER TABLE ticket ADD constraint ticket_unique unique (ticket);
        ''')

    def upgrade_v2_2_0_b01_002(my):
        my.run_sql('''
        ALTER TABLE ticket ADD;
        ''')

    def upgrade_v2_2_0_b01_001(my):
        my.run_sql('''
        ALTER TABLE ticket drop constraint "ticket_pkey";
        ''')
  

    #
    # 2.1.0.b08
    #
    def upgrade_v2_1_0_b08_005(my):
        my.run_sql('''
        CREATE INDEX snapshot_search_code_idx ON snapshot(search_code);
        ''')


    def upgrade_v2_1_0_b08_004(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD search_code varchar(256);
        ''')


    def upgrade_v2_1_0_b08_003(my):
        # NOTE: this gives a warning:
        #WARNING:  nonstandard use of \\ in a string literal
        #LINE 1: ...hot set project_code = substring(search_type from '=(\\w+)$'...
        my.run_sql('''
        UPDATE snapshot set project_code = substring(search_type from '=(\\w+)$');
        ''')

    def upgrade_v2_1_0_b08_002(my):
        my.run_sql('''
        CREATE INDEX snapshot_project_code_idx ON snapshot(project_code);
        ''')


    def upgrade_v2_1_0_b08_001(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD project_code varchar(256);
        ''')

    #
    # 2.1.0.b05
    #
    def upgrade_v2_1_0_b05_003(my):
        my.run_sql('''
        CREATE UNIQUE INDEX ticket_id_idx ON ticket;
        ''')
 
    def upgrade_v2_1_0_b05_002(my):
        my.run_sql('''
        CREATE UNIQUE INDEX transaction_state_ticket_idx ON transaction_state(ticket);
        ''')

    def upgrade_v2_1_0_b05_001(my):
        my.run_sql('''
        ALTER TABLE transaction_state ADD ;
        ''')


    #
    # 2.1.0.a02
    #
    def upgrade_v2_1_0_a02_002(my):
        my.run_sql('''
        ALTER TABLE snapshot_type ADD relfile text;
        ''')

    # Repeating here so 2.1.0 users can also get this 
    def upgrade_v2_1_0_a02_001(my):
        
        my.run_sql('''
        ALTER TABLE transaction_log ADD title text;
        ''')


    """
    def upgrade_v2_1_0_a02_001(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/snapshot_type', 'prod', 'Snapshot Type', '{project}', 'snapshot_type', 'pyasm.biz.SnapshotType', 'Snapshot Type', 'public');
        ''')
    """


    #
    # 2.0.0.rc01
    #
    def upgrade_v2_0_0_rc01_001(my):
        
        my.run_sql('''
        ALTER TABLE transaction_log ADD title text;
        ''')

    #
    # 2.0.0.b03
    #
   

    def upgrade_v2_0_0_b03_001(my):
        
        my.run_sql('''
        UPDATE schema SET schema = '<schema>

<search_type name="prod/art_reference"/>
<search_type name="prod/script"/>
<search_type name="prod/storyboard"/>


<search_type name="prod/asset_library"/>
<search_type name="prod/asset"/>
<search_type name="prod/texture"/>

<search_type name="prod/episode"/>
<search_type name="prod/episode_instance"/>
<search_type name="prod/sequence"/>
<search_type name="prod/sequence_instance"/>
<search_type name="prod/shot"/>
<search_type name="prod/shot_instance"/>
<search_type name="prod/shot_texture"/>
<search_type name="prod/layer"/>
<search_type name="prod/composite"/>

<search_type name="prod/bin"/>
<search_type name="prod/submission_in_bin"/>
<search_type name="prod/submission"/>

<connect from="prod/asset_library" to="prod/asset" type="hierarchy"/>
<connect from="prod/asset" to="prod/texture" type="hierarchy"/>

<connect from="prod/episode" to="prod/sequence" type="hierarchy"/>
<connect from="prod/episode" to="prod/episode_instance" type="hierarchy"/>

<connect from="prod/sequence" to="prod/shot" type="hierarchy"/>
<connect from="prod/sequence" to="prod/sequence_instance" type="hierarchy"/>
<connect from="prod/shot" to="prod/shot_texture" type="hierarchy"/>
<connect from="prod/shot" to="prod/shot_instance" type="hierarchy"/>
<connect from="prod/shot" to="prod/layer" type="hierarchy"/>
<connect from="prod/shot" to="prod/composite" type="hierarchy"/>

<connect from="prod/bin" to="prod/submission_in_bin" type="hierarchy"/>
<connect from="prod/submission_in_bin" to="prod/submission" type="hierarchy"/>

</schema>' where code='prod';
        ''')

    def upgrade_v2_0_0_a01_002(my):
        my.run_sql('''
    INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/access_log', 'sthpw', 'Access Log', 'sthpw', 'access_log', 'pyasm.search.SObject', 'Access Log', 'public');
        ''')


    def upgrade_v2_0_0_a01_001(my):
        my.run_sql('''
        CREATE TABLE access_log (
            id INT IDENTITY,
            code varchar(256),
            url text,
            data text,
            start_time datetime2(6),
            end_time datetime2(6),
            duration float
        );
        ''')


    #
    # 1.9.1.a07
    #

    def upgrade_v1_9_1_a07_001(my):
        my.run_sql('''
        ALTER TABLE file ADD relative_dir text;
        ''')

    #
    # 1.9.1.a06
    #

    def upgrade_v1_9_1_a06_005(my):
        my.run_sql('''
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/search_type', 'sthpw', 'List of all the search objects', 'sthpw', 'search_object', 'pyasm.search.SearchType', 'Search Objects', 'public');
        ''')


    def upgrade_v1_9_1_a06_004(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/plate', 'prod', 'Production Plates', '{project}', 'plate', 'pyasm.effects.biz.Plate', 'Production plates', 'public');
        ''')


    def upgrade_v1_9_1_a06_003(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD status varchar(256)
        ''')

    def upgrade_v1_9_1_a06_002(my):
        '''set is_latest ON all snapshots'''
        from pyasm.search import Search, SearchException
        search = Search("sthpw/snapshot")
        search.add_order_by("search_type")
        search.add_order_by("search_id")
        search.add_order_by("context")
        search.add_order_by("version desc")
        snapshots = search.get_sobjects()
        print "found [%s] snapshots" % len(snapshots)

        current_search_type = None
        current_search_id = None
        current_context = None
        current_version = None
        for i, snapshot in enumerate(snapshots):
            search_type = snapshot.get_value("search_type")
            search_id = snapshot.get_value("search_id")
            context = snapshot.get_value("context")
            version = snapshot.get_value("version")

            print i, search_type, search_id, context, version

            if not (search_type == current_search_type and \
                    search_id == current_search_id and \
                    context == current_context):
                snapshot.set_latest()
                print "\t... is latest!!!"

            current_search_type = search_type
            current_search_id = search_id
            current_context = context
            current_version = version

            


    def upgrade_v1_9_1_a06_001(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD is_latest BIT;
        ''')




    def upgrade_v1_9_1_a04_003(my):
        my.run_sql('''
        UPDATE schema SET schema = '<schema>

<search_type name="prod/art_reference"/>
<search_type name="prod/script"/>
<search_type name="prod/storyboard"/>


<search_type name="prod/asset_library"/>
<search_type name="prod/asset"/>
<search_type name="prod/texture"/>

<search_type name="prod/sequence"/>
<search_type name="prod/sequence_instance"/>
<search_type name="prod/shot"/>
<search_type name="prod/shot_instance"/>
<search_type name="prod/shot_texture"/>
<search_type name="prod/layer"/>
<search_type name="prod/composite"/>

<search_type name="prod/bin"/>
<search_type name="prod/submission_in_bin"/>
<search_type name="prod/submission"/>

<connect from="prod/asset_library" to="prod/asset" type="hierarchy"/>
<connect from="prod/asset" to="prod/texture" type="hierarchy"/>

<connect from="prod/sequence" to="prod/shot" type="hierarchy"/>
<connect from="prod/sequence" to="prod/sequence_instance" type="hierarchy"/>
<connect from="prod/shot" to="prod/shot_texture" type="hierarchy"/>
<connect from="prod/shot" to="prod/shot_instance" type="hierarchy"/>
<connect from="prod/shot" to="prod/layer" type="hierarchy"/>
<connect from="prod/shot" to="prod/composite" type="hierarchy"/>

<connect from="prod/bin" to="prod/submission_in_bin" type="hierarchy"/>
<connect from="prod/submission_in_bin" to="prod/submission" type="hierarchy"/>

</schema>' where code='prod';
        ''')
        
    def upgrade_v1_9_1_a04_002(my):
        my.run_sql('''
        INSERT INTO schema (code, description) values ('prod', '3D Production Schema');
        ''')


    def upgrade_v1_9_1_a04_001(my):
        my.run_sql('''
        ALTER TABLE schema ADD CONSTRAINT schema_code_idx UNIQUE (code);
        ''')


    def upgrade_v1_9_1_a04_001(my):
        my.run_sql('''
        ALTER TABLE schema ADD CONSTRAINT schema_code_idx UNIQUE (code);
        ''')


    def upgrade_v1_9_1_a02_003(my):
        my.run_sql('''
        ALTER TABLE snapshot_type ADD snapshot_flavor text;
        ''')

    def upgrade_v1_9_1_a02_002(my):
        my.run_sql('''
        ALTER TABLE snapshot_type ADD subcontext text;
        ''')

    def upgrade_v1_9_1_a02_001(my):
        my.run_sql('''
        ALTER TABLE command ADD s_status varchar(256);
        ''')

    def upgrade_v1_9_1_a01_004(my):
        my.run_sql('''
        ALTER TABLE login_group ADD s_status varchar(256);
        ''')

    def upgrade_v1_9_1_a01_003(my):
        my.run_sql('''
UPDATE schema set schema = '<schema>
    <search_type name="unittest/country"/>
    <search_type name="unittest/city"/>
    <search_type name="unittest/person"/>

    <search_type name="unittest/car"/>

    <connect from="unittest/country" to="unittest/city" type="hierarchy"/>
    <connect from="unittest/city" to="unittest/person" type="hierarchy"/>

    <connect from="unittest/car" to="unittest/person" type="many_to_many" instance_type="unittest/person_car_instance"/>
</schema>' where code = 'unittest';
        ''')


    def upgrade_v1_9_1_a01_002(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD metadata text;
        ''')


    def upgrade_v1_9_1_a01_001(my):
        my.run_sql('''
        INSERT INTO project_type (code, type) values ('unittest', 'unittest');
        ''')


    def upgrade_v1_9_0_a9_005(my):
        my.run_sql('''
        UPDATE search_object set title='Triggers',description='Triggers' where search_type = 'sthpw/trigger';
        ''')


    def upgrade_v1_9_0_a9_004(my):
        my.run_sql('''
        UPDATE search_object set title='Users' where search_type = 'sthpw/login';
        ''')


    def upgrade_v1_9_0_a9_003(my):
        my.run_sql('''
        UPDATE search_object set title='Textures',description='Textures' where search_type = 'prod/texture';
        ''')


    def upgrade_v1_9_0_a9_002(my):
        my.run_sql('''
        UPDATE search_object set title='Composites',description='Composites' where search_type = 'prod/composite';
        ''')


    def upgrade_v1_9_0_a9_001(my):
        my.run_sql('''
        UPDATE project set type = 'unittest' where code = 'unittest';
        ''')


    def upgrade_v1_9_0_a8_011(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD level_id int4;
        ''')


    def upgrade_v1_9_0_a8_010(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD level_type varchar(256);
        ''')


    def upgrade_v1_9_0_a8_009(my):
        my.run_sql('''
INSERT INTO schema (code, description, schema) values ('unittest', 'Unittest Schema', '<schema>
    <search_type search_type="unittest/country"/>
    <search_type search_type="unittest/city"/>
    <search_type search_type="unittest/person"/>

    <connect from="unittest/country" to="unittest/city" type="hierarchy"/>
    <connect from="unittest/city" to="unittest/person" type="hierarchy"/>
</schema>');
        ''')



    def upgrade_v1_9_0_a8_008(my):
        my.run_sql('''
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('unittest/country', 'unittest', 'Unittest Country', 'unittest', 'country', 'pyasm.search.SObject', 'Unittest Country', 'public');
        ''')


    def upgrade_v1_9_0_a8_007(my):
        my.run_sql('''
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('unittest/city', 'unittest', 'Unittest City', 'unittest', 'city', 'pyasm.search.SObject', 'Unittest City', 'public');
        ''')


    def upgrade_v1_9_0_a8_006(my):
        my.run_sql('''
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('unittest/person', 'unittest', 'Unittest Person', 'unittest', 'person', 'pyasm.search.SObject', 'Unittest Person', 'public');
        ''')

    def upgrade_v1_9_0_a8_005(my):
        my.run_sql('''
        ALTER TABLE schema ADD constraint schema_code_unique UNIQUE (code);
        ''')

    def upgrade_v1_9_0_a8_004(my):
        my.run_sql('''
        ALTER TABLE widget_config ADD s_status varchar(32);
        ''')

    def upgrade_v1_9_0_a8_003(my):
        my.run_sql('''
        ALTER TABLE file ADD source_path text;
        ''')


    def upgrade_v1_9_0_a8_002(my):
        my.run_sql('''
        ALTER TABLE file ADD checkin_dir text;
        ''')

    def upgrade_v1_9_0_a8_001(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('unittest/person', 'unittest', 'Unittest Person', 'unittest', 'person', 'pyasm.search.SObject', 'Unittest Person', 'public');
        ''')

    def upgrade_v1_9_0_a7_003(my):
        my.run_sql('''
        ALTER TABLE "trigger" ADD project_code varchar(256);
        ''')


    def upgrade_v1_9_0_a7_002(my):
        my.run_sql('''
        ALTER TABLE snapshot_type ADD project_code varchar(256);
        ''')

    def upgrade_v1_9_0_a7_001(my):
        my.run_sql('''
        ALTER TABLE snapshot_type ADD relpath text;
        ''')



    def upgrade_v1_9_0_a6_001(my):
        my.run_sql('''
        ALTER TABLE snapshot_type ADD constraint snapshot_type_code_unique UNIQUE (code);
        ''')

    def upgrade_v1_9_0_a1_014(my):
        my.run_sql('''
        UPDATE search_object SET class_name = 'pyasm.biz.CustomProperty' where search_type = 'prod/custom_property';
        ''')

    def upgrade_v1_9_0_a1_013(my):
        my.run_sql('''
        CREATE TABLE schema (
            id INT IDENTITY,
            code varchar(256),
            description text,
            schema text,
            [timestamp] datetime2(6) DEFAULT (getdate()),
            login varchar(256),
            s_status varchar(30)
        );
        ''')


    def upgrade_v1_9_0_a1_012(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/schema', 'sthpw', 'Schema', 'sthpw', 'schema', 'pyasm.biz.Schema', 'Schema', 'public');
        ''')


    def upgrade_v1_9_0_a1_011(my):
        my.run_sql('''
        ALTER TABLE widget_config ALTER COLUMN login DROP NOT NULL;
        ''')

    def upgrade_v1_9_0_a1_010(my):
        my.run_sql('''
        CREATE TABLE debug_log (
            id INT IDENTITY,
            category varchar(256),
            level varchar(256),
            message text,
            [timestamp] datetime2(6) DEFAULT (getdate()),
            login varchar(256),
            s_status varchar(30)
        );
        ''')


    def upgrade_v1_9_0_a1_009(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/debug_log', 'sthpw', 'Debug Log', 'sthpw', 'debug_log', 'pyasm.biz.DebugLog', 'Debug Log', 'public');
        ''')


    def upgrade_v1_9_0_a1_008(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/custom_property', 'sthpw', 'Custom Property', '{project}', 'custom_property', 'pyasm.search.SObject', 'Custom Property', 'public');
        ''')


    def upgrade_v1_9_0_a1_007(my):
        my.run_sql('''
        UPDATE search_object SET class_name = 'pyasm.search.WidgetDbConfig' where search_type = 'sthpw/widget_config';
        ''')


    def upgrade_v1_9_0_a1_006(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('game/take', 'game', 'Take', '{project}', 'take', 'pyasm.search.SObject', 'Take', 'public');
        ''')

    def upgrade_v1_9_0_a1_005(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('game/beat', 'game', 'Beat', '{project}', 'beat', 'pyasm.search.SObject', 'Beat', 'public');
        ''')


    def upgrade_v1_9_0_a1_004(my):
        my.run_sql('''
        ALTER TABLE login_group ADD project_code text;
        ''')

    def upgrade_v1_9_0_a1_003(my):
        my.run_sql('''
        ALTER TABLE [login] ADD project_code text;
        ''')


    def upgrade_v1_9_0_a1_002(my):
        my.run_sql('''
        CREATE TABLE snapshot_type (
            id INT IDENTITY,
            code varchar(256),
            pipeline_code text,
            [timestamp] datetime2(6) DEFAULT (getdate()),
            login varchar(256),
            s_status varchar(30)
        );
        ''')


    def upgrade_v1_9_0_a1_001(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/snapshot_type', 'sthpw', 'Snapshot Type', 'sthpw', 'snapshot_type', 'pyasm.biz.SnapshotType', 'Snapshot Type', 'public');
        ''')




    def upgrade_v1_6_1_s2_001(my):
        my.run_sql('''
        ALTER TABLE connection ALTER datetime2(6) set DEFAULT (getdate());
        ''')

    def upgrade_v1_6_0_rc2_003(my):
        from pyasm.search import Search
        from pyasm.biz import Project
        search = Search("sthpw/task")
        search.set_show_retired(True)
        tasks = search.get_sobjects()
        for task in tasks:
            project_code = task.get_value("project_code")
            if not project_code:
                project_code = 'sthpw'
            project = Project.get_by_code(project_code)
            if not project:
                initials = "STHPW"
            else:
                initials = project.get_initials()
            id = task.get_id()
            code = "%s%s" % (id, initials)
            task.set_value("code", code)
            task.commit()

    def upgrade_v1_6_0_rc2_002(my):
        my.run_sql('''
        ALTER TABLE task ADD code varchar(256);
        ''')
    

   

    def upgrade_v1_6_0_rc2_001(my):
        my.run_sql('''
        ALTER TABLE milestone DROP CONSTRAINT milestone_project_code_fkey;
        ''')

    def upgrade_v1_6_0_rc1_001(my):
        my.run_sql('''
        ALTER TABLE pipeline DROP CONSTRAINT project_code_foreign;
        ''')
    def upgrade_v1_6_0_rc1_002(my):
        my.run_sql('''
        ALTER TABLE pipeline ALTER COLUMN project_code text;
        ''')
    def upgrade_v1_6_0_rc1_003(my):
        '''new preference for showing multi-select'''
        my.run_sql('''
        INSERT INTO pref_list ("key", description, options, "type", category, [timestamp], title) VALUES ( 'select_filter', 'Determines whether to show some filters as multi-select', 'single|multi', 'sequence', 'general', '2008-03-01 11:18:26.894318', 'Select Filter');
        ''')


    def upgrade_v1_6_0_rc1_003(my):
        '''new preference for showing multi-select'''
        my.run_sql('''
        INSERT INTO pref_list ("key", description, options, "type", category, [timestamp], title) VALUES ( 'select_filter', 'Determines whether to show some filters as multi-select', 'single|multi', 'sequence', 'general', '2008-03-01 11:18:26.894318', 'Select Filter');
        ''')


    def upgrade_v1_6_0_rc1_004(my):
        my.run_sql('''
        INSERT INTO pref_list ("key", description, options, "type", category, [timestamp], title) VALUES ( 'use_java_maya', 'Determines whether to use the java applet Maya connector', 'false|true', 'sequence', 'general', '2008-03-01 11:18:26.894318', 'Java Maya Connector');
        ''')

 
    def upgrade_v1_6_0_b2_001(my):
        my.run_sql('''
        ALTER TABLE project ADD last_version_UPDATE varchar(256);
        ''')
    def upgrade_v1_6_0_b2_002(my):
        my.run_sql('''
        CREATE TABLE widget_extend (
            id INT IDENTITY NOT NULL,
            key varchar(256),
            parent varchar(256),
            data text,
            project_code varchar(256),
            login varchar(32),
            [timestamp] datetime2(6),
            s_status varchar(32)
        );
        ''')

    def upgrade_v1_6_0_b2_003(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/widget_extend', 'sthpw', 'Extend Widget', 'sthpw', 'widget_extend', 'pyasm.search.SObject', 'widget_extend', 'public');
        ''')

    def upgrade_v1_6_0_b2_004(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/sequence_instance', 'prod', 'Sequence Instance', '{project}', 'sequence_instance', 'pyasm.prod.biz.SequenceInstance', 'Sequence Instance', 'public');
        ''')

    def upgrade_v1_6_0_b2_005(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('flash/episode_instance', 'prod', 'Episode Instance', '{project}', 'episode_instance', 'pyasm.flash.FlashEpisodeInstance', 'Episode Instance', 'public');
        ''')

    def upgrade_v1_6_0_b2_006(my):
        my.run_sql('''
        DELETE FROM project_type where code = 'default';
        ''')

    def upgrade_v1_6_0_b2_007(my):
        my.run_sql('''
        ALTER TABLE project_type ADD s_status varchar(32);
        ''')


    def upgrade_v1_6_0_b2_008(my):
        my.run_sql('''
        ALTER TABLE widget_extend ADD description text;
        ''')
    def upgrade_v1_6_0_b2_009(my):
        my.run_sql('''
        ALTER TABLE widget_extend rename column parent to type;
        ''')
    def upgrade_v1_6_0_b2_010(my):
        # put this in for now.  It breaks if this is not there .  we don't have
        # an admin database, so things mess up a bit, so we use sthpw as
        # a placeholder.
        my.run_sql('''
        INSERT INTO project (code, title, type) values ('admin', 'Admin', 'sthpw')
        ''')

    def upgrade_v1_6_0_b2_011(my):
        # put this in for now.  It breaks if this is not there .  we don't have
        # an admin database, so things mess up a bit, so we use sthpw as
        # a placeholder.
        my.run_sql('''
        ALTER TABLE project_type ADD type varchar(100);
        ''')

    def upgrade_v1_6_0_b2_012(my):
        # put the code in type 'cuz we need to set NOT NULL
        from pyasm.search import Search
        search = Search('sthpw/project_type')
        project_types = search.get_sobjects()
        for type in project_types:
            if not type.get_value('type'):
                type.set_value('type', type.get_code())
                type.commit()
        
    def upgrade_v1_6_0_b2_013(my):
        my.run_sql('''
        ALTER TABLE project_type ALTER COLUMN type SET NOT NULL;
        ''')

        

    



    def upgrade_v1_5_3_010(my):
        my.run_sql('''
        CREATE TABLE transaction_state (
            id INT IDENTITY NOT NULL,
            ticket varchar(100),
            [timestamp] datetime2(6),
            data text
        );
        ''')



    def upgrade_v1_5_3_009(my):
        my.run_sql('''
        ALTER TABLE task ADD supervisor character varying(100);
        ''')

    def upgrade_v1_5_3_008(my):
        my.run_sql('''
        CREATE TABLE transaction_state (
            id INT IDENTITY NOT NULL,
            ticket varchar(100),
            [timestamp] datetime2(6),
            data text
        );
        ''')

        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/transaction_state', 'sthpw', 'XMLRPC State', 'sthpw', 'transaction_state', 'pyasm.search.TransactionState', 'Transaction State', 'public');
        ''')


    
    
    def upgrade_v1_5_3_007(my):
        my.run_sql('''
        INSERT INTO access_rule (project_code, code, description, "rule", [timestamp])
         VALUES ( NULL, 'hide_task_status', 
        'Hide the Complete or Approved status from the Task Status dropdown', 
        '<rules>
        <rule access=''deny'' key=''Complete'' category=''process_select''/>
        <rule access=''deny'' key=''Approved'' category=''process_select''/>
        </rules>', '2007-10-25 18:32:37.609');
        ''')


    def upgrade_v1_5_3_006(my):
        my.run_sql('''
        UPDATE search_object SET search_type='flash/shot_instance', class_name='pyasm.flash.FlashShotInstance' where search_type='flash/instance';
        ''')

    def upgrade_v1_5_3_005(my):
        my.run_sql('''
        ALTER TABLE pipeline ADD s_status varchar(30);
        ''')
    def upgrade_v1_5_3_004(my):
        my.run_sql('''
        ALTER TABLE project_type ADD repo_handler_cls varchar(200);
        ''')

    def upgrade_v1_5_3_003(my):
        my.run_sql('''
        INSERT INTO project (code, title, initials, type) values ('example', 'Example', 'EX', 'default');
        ''')

    def upgrade_v1_5_3_002(my):
        my.run_sql('''
        INSERT INTO project_type (code, type) values ('default', 'simple');
        ''')
   

    def upgrade_v1_5_3_001(my):
        my.run_sql('''
        ALTER TABLE "trigger" ADD event varchar(32);
        ''')

    def upgrade_20071003(my):
        my.run_sql('''
        INSERT INTO access_rule ( project_code, code, description, "rule", [timestamp]) VALUES ( NULL, 'client', 'Deny all tabs but the client tab. Allow to see the project named [bar]', '<rules>  
<rule group=''project'' default=''deny''/>  
<rule group=''project'' key=''bar'' access=''view''/>  
<rule group=''project'' key=''default'' access=''view''/>  
  
<rule group="tab" default=''deny''/>  
<rule group="tab" key="Client" access=''view''/>  
<rule group="tab" key="Review" access=''view''/>  
</rules> ', '2007-05-29 22:50:16.937');
        ''')
        my.run_sql('''
INSERT INTO access_rule ( project_code, code, description, "rule", [timestamp]) VALUES ( NULL, 'show_user_assign_wdg', 'right to see User Assign Widget in Supe tabs for Asset/Shot pipeline', '<rules>
<rule access=''view'' key=''UserAssignWdg'' category=''secure_wdg''/>
</rules>', '2007-10-02 18:47:06.39');
        ''')
        my.run_sql('''
INSERT INTO access_rule ( project_code, code, description, "rule", [timestamp]) VALUES ( NULL, 'show_user_filter', 'right to see the User Filter', '<rules>
<rule access=''view'' key=''UserFilterWdg'' category=''secure_wdg''/>
<rule category=''prod/shot'' key=''s_status'' value=''retired'' access=''allow''/>
</rules>', '2007-05-31 12:13:03.015');
        ''')
        my.run_sql('''INSERT INTO access_rule ( project_code, code, description, "rule", [timestamp]) VALUES ( NULL, 'hide_user_filter', 'Hide the User Filter in Artist area', '<rules>
<rule access=''deny'' key=''UserFilterWdg'' category=''public_wdg''/>
</rules>', '2007-09-29 11:48:48.718');
        ''')

    def upgrade_20071002(my):
        my.run_sql('''
        ALTER TABLE queue ADD policy_code varchar(30);
        ''')
        my.run_sql('''
        ALTER TABLE queue ADD search_type varchar(256);
        ''')
        my.run_sql('''
        ALTER TABLE queue ADD search_id int4;
        ''')
 
    
    def upgrade_20070925(my):
        my.run_sql('''
            INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('flash/pickup_request', 'flash', 'Pickup Request', '{project}', 'pickup_request', 'pyasm.search.SObject', 'Pickup Request', 'public');
        ''')

 
    def upgrade_20070924(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('flash/final_wave', 'flash', 'Final Wave', '{project}', 'final_wave', 'pyasm.flash.FinalWave', 'Final Wave', 'public');

        UPDATE search_object set class_name='pyasm.flash.NatPause' where search_type='flash/nat_pause';
        ''')

    def upgrade_20070922(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/render_policy', 'prod', 'Render Policy', '{project}', 'render_policy', 'pyasm.prod.biz.RenderPolicy', 'Render Policy', 'public');
        ''')     

    def upgrade_20070912(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/shot_audio', 'prod', 'Shot Audio', '{project}', 'shot_audio', 'pyasm.prod.biz.ShotAudio', 'Shot Audio', 'public');
        ''')
        
    def upgrade_20070910(my):
        my.run_sql('''
        ALTER TABLE queue ADD dispatcher_id int4;
        '''
        )

    def upgrade_20070904(my):
        my.run_sql('''
        UPDATE snapshot SET snapshot_type = 'flash' WHERE search_type like 'flash/%';
        ''')


    def upgrade_20070904(my):
        my.run_sql('''
        UPDATE search_object SET class_name = 'pyasm.search.WidgetDbConfig' WHERE search_type = 'sthpw/widget_config';

        ''')


    def upgrade_20070828(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD revision int2;
        ''')


    def upgrade_20070823(my):
        my.run_sql('''
        ALTER TABLE task ADD project_code character varying(100);
        ALTER TABLE task ADD CONSTRAINT project_code_fkey foreign key 
        (project_code) references project (code) on
        UPDATE cascade ON delete restrict deferrable initially deferred; 
        ''')

    def upgrade_20070822(my):
        my.run_sql('''
        INSERT INTO pref_list ("key", description, options, "type", category, [timestamp], 
        title) VALUES ('debug', 'Determines whether to show debug information'
        , 'false|true', 'sequence', 'general', '2007-08-21 11:18:26.894318', 'Debug');

        ''')


    def upgrade_20070821(my):
        my.run_sql('''
        ALTER TABLE file ADD md5 varchar(32);
        ''')


    def upgrade_20070812(my):
        my.run_sql('''
        UPDATE search_object set class_name='pyasm.biz.RemoteRepo'
        where search_type='sthpw/remote_repo';
        ''')

    def upgrade_20070725(my):
        my.run_sql('''
        ALTER TABLE file ADD project_code character varying(100);
        ALTER TABLE file ADD CONSTRAINT project_code_fkey foreign key 
        (project_code) references project (code) on
        UPDATE cascade ON delete restrict deferrable initially deferred; 
        ''')

    def upgrade_20070723(my):
        my.run_sql('''
        ALTER TABLE remote_repo ADD login character varying(100);
        ALTER TABLE remote_repo ADD CONSTRAINT login_fkey foreign key 
        (login) references login (login) on
        UPDATE cascade ON delete restrict deferrable initially deferred; 
        ''')

    def upgrade_20070630(my):
        my.run_sql('''
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/naming', 'prod', 'Naming', '{project}', '{public}.naming', 'pyasm.biz.Naming', '', 'public');
        ''')

    def upgrade_20070628(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/cut_sequence', 'prod', 'Cut Sequences', '{project}', 'cut_sequence', 'pyasm.prod.biz.CutSequence', 'Cut Sequences', 'public');
        ''')



    """
    def upgrade_20070627(my):
        my.run_sql('''
        CREATE TABLE folder (
            id INT IDENTITY NOT NULL,
            path text,
            parent_id int4,
            parent_dir varchar(256),
            search_type varchar(256),
            search_id int4,
        );
        ''')

        my.run_sql('''
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/folder', 'sthpw', 'Folder', '{project}', '{public}.folder', 'pyasm.biz.Folder', '', 'public');
        ''')
    """

    def upgrade_20070616(my):
        my.run_sql('''
        CREATE TABLE translation (
            id INT IDENTITY,
            language varchar(32),
            msgid text,
            msgstr text,
            line text,
            login varchar(256),
            [timestamp] datetime2(6) DEFAULT (getdate())
        );
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/translation', 'sthpw', 'Locale Translations', 'sthpw', '{public}.translation', 'pyasm.search.SObject', '', 'public');
        ''')



    def upgrade_20070611(my):
        my.run_sql('''
        ALTER TABLE clipboard ADD category varchar(256);

        ALTER TABLE sobject_log ADD transaction_log_id int4;
        ALTER TABLE sobject_log ADD CONSTRAINT transaction_log_fkey foreign key 
        (transaction_log_id) references transaction_log  on
        UPDATE cascade ON delete cascade deferrable initially deferred;

        ''')

    def upgrade_20070607(my):
        my.run_sql('''
        ALTER TABLE project ADD s_status varchar(30);
        ALTER TABLE project ADD status varchar(256);

        ALTER TABLE pref_list ADD CONSTRAINT pref_list_key_idx UNIQUE (key);

        ALTER TABLE pref_setting ADD CONSTRAINT pref_setting_key_fkey foreign key 
        (key) references pref_list (key) on
        UPDATE cascade ON delete restrict deferrable initially deferred;

        ALTER TABLE pref_setting ADD CONSTRAINT pref_setting_login_fkey foreign key 
        (login) references login (login) on
        UPDATE cascade ON delete restrict deferrable initially deferred;

        ''')

    def upgrade_20070605(my):
        my.run_sql('''
          CREATE TABLE pref_setting (
            id INT IDENTITY,
            project_code varchar(256),
            login varchar(256),
            key varchar(256),
            value text,
            [timestamp] datetime2(6) DEFAULT (getdate())
        );

INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/pref_setting', 'sthpw', 'Preference Setting', 'sthpw', '{public}.pref_setting', 'pyasm.biz.PrefSetting', '', 'public');
        ''')


        my.run_sql('''
        CREATE TABLE pref_list (
            id INT IDENTITY,
            key varchar(256),
            title text,
            description text,
            options text,
            type varchar(256),
            category varchar(256),
            [timestamp] datetime2(6) DEFAULT (getdate())
        );
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/pref_list', 'sthpw', 'Preferences List', 'sthpw', '{public}.pref_list', 'pyasm.biz.PrefList', '', 'public');
        ''')





    def upgrade_20070530(my):
        my.run_sql('''
        ALTER TABLE timecard ADD constraint timecard_task_unique UNIQUE(search_type, search_id, week, year, project_code, login); 
        ALTER TABLE timecard ADD constraint timecard_general_unique UNIQUE(description, week, year, project_code, login); 
        CREATE TABLE special_day
        (
          id INT IDENTITY NOT NULL,
          week smallint,
          mon real,
          tue real,
          wed real,
          thu real,
          fri real,
          sat real,
          sun real,
          "year" integer,
          [login] character varying(100),
          "description" text, 
          "type" character varying(100),
          project_code character varying(30),
          CONSTRAINT special_day_pkey ,
          
          CONSTRAINT project_code_foreign FOREIGN KEY (project_code)
              REFERENCES project (code) MATCH SIMPLE
              ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED
        ); 

        ''')

    def upgrade_20070529(my):
        my.run_sql('''
         CREATE TABLE access_rule (
            id INT IDENTITY,
            project_code varchar(256),
            code varchar(256),
            description text,
            [rule] text,
            [timestamp] datetime2(6) DEFAULT (getdate())
        );

INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/access_rule', 'sthpw', 'Access Rules', 'sthpw', '{public}.access_rule', 'pyasm.security.AccessRule', '', 'public');

         CREATE TABLE access_rule_in_group (
            id INT IDENTITY,
            login_group varchar(256),
            access_rule_code varchar(256),
            [timestamp] datetime2(6) DEFAULT (getdate())
        );
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/access_rule_in_group', 'sthpw', 'Access Rules In Group', 'sthpw', '{public}.access_rule_in_group', 'pyasm.security.AccessRuleInGroup', '', 'public');

        ALTER TABLE access_rule ADD CONSTRAINT access_rule_code_key unique (code);


        ALTER TABLE access_rule_in_group ADD constraint access_rule_fkey1 foreign key 
        (login_group) references login_group (login_group) on
        UPDATE cascade ON delete restrict deferrable initially deferred;

        ALTER TABLE access_rule_in_group ADD constraint access_rule_fkey2 foreign key 
        (access_rule_code) references access_rule (code) on
        UPDATE cascade ON delete restrict deferrable initially deferred;

        ''')


    def upgrade_20070528(my):
        my.run_sql('''
         CREATE TABLE clipboard (
            id INT IDENTITY,
            project_code varchar(256),
            login varchar(256),
            search_type varchar(256),
            search_id int4,
            [timestamp] datetime2(6) DEFAULT (getdate())
        );
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/clipboard', 'sthpw', 'Clipboard', 'sthpw', '{public}.clipboard', 'pyasm.biz.Clipboard', '', 'public');
        ''')

    def upgrade_20070525(my):
        my.run_sql('''
        ALTER TABLE status_log ADD project_code varchar(256);
        ''')


    def upgrade_20070523(my):
        my.run_sql('''
        ALTER TABLE project alter column reg_hours numeric;
        ''')


    def upgrade_20070522(my):
        my.run_sql('''
        CREATE TABLE notification_log (
            id INT IDENTITY,
            project_code varchar(256),
            login varchar(256),
            command_cls varchar(256),
            subject text,
            message text,
            [timestamp] datetime2(6) DEFAULT (getdate())
        );

        CREATE TABLE notification_login (
            id INT IDENTITY,
            notification_log_id int4,
            project_code varchar(256),
            login varchar(256),
            type varchar(256),
            [timestamp] datetime2(6) DEFAULT (getdate())
        );

INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/notification_log', 'sthpw', 'Notification Log', 'sthpw', '{public}.notification_log', 'pyasm.search.SObject', '', 'public');
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/notification_login', 'sthpw', 'Notification Login', 'sthpw', '{public}.notification_login', 'pyasm.search.SObject', '', 'public');
        ''')


    def upgrade_20070520(my):
        my.run_sql('''
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/shot_texture', 'prod', 'Shot Texture maps', '{project}', '{public}.shot_texture', 'pyasm.prod.biz.ShotTexture', '', 'public');

INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('flash/leica', 'flash', 'Leica', '{project}', '{public}.leica', 'pyasm.search.SObject', '', 'public');
        ''')

    def upgrade_20070520(my):
        my.run_sql('''
        ALTER TABLE status_log ADD to_status varchar(256);
        ALTER TABLE status_log ADD from_status varchar(256);
        ''')


    def upgrade_20070518(my):
        my.run_sql('''
        ALTER TABLE timecard ADD year integer;
        ''')

    def upgrade_20070514(my):
        my.run_sql('''
        ALTER TABLE project_type ADD CONSTRAINT code_key unique (code);
        ''')

    def upgrade_20070511(my):
        my.run_sql('''
        ALTER TABLE TASK ADD depend_id int4;
        ''')



    def upgrade_20070430(my):
        my.run_sql('''
        CREATE TABLE project_type (
            id INT IDENTITY,
            code varchar(30),
            dir_naming_cls varchar(200),
            file_naming_cls varchar(200),
            code_naming_cls varchar(200),
            node_naming_cls varchar(200),
            sobject_mapping_cls varchar(200)
        );

        -- create a 3D production type
        INSERT INTO project_type (code, dir_naming_cls, file_naming_cls, code_naming_cls, node_naming_cls, sobject_mapping_cls )
        VALUES ('prod', 'pyasm.prod.biz.ProdDirNaming', 'pyasm.prod.biz.ProdFileNaming', '', '', '');
        INSERT INTO project_type (code, dir_naming_cls, file_naming_cls, code_naming_cls, node_naming_cls, sobject_mapping_cls )
        VALUES ('flash', 'pyasm.flash.FlashDirNaming', '', 'pyasm.flash.FlashCodeNaming', '', 'pyasm.flash.biz.FlashMapping');

        -- register the search type
        INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('sthpw/project_type', 'sthpw', 'Project Type', 'sthpw', 'project_type', 'pyasm.biz.ProjectType', 'Project Type', 'public');
        ''')


    def upgrade_20070425(my):
        my.run_sql('''
        CREATE INDEX task_search_type_idx ON task(search_type);
        CREATE INDEX transaction_log_idx2 ON transaction_log (login,namespace,type);
        ''')



    def upgrade_20070419(my):
        my.run_sql('''
            UPDATE search_object set class_name = 'pyasm.biz.SObjectConnection' where search_type = 'sthpw/connection';
        ''')


    def upgrade_20070413(my):
        my.run_sql('''
        ALTER TABLE note ADD title varchar(1024);
        ALTER TABLE note ADD parent_id int8;
        ALTER TABLE note ADD status varchar(256);
        ALTER TABLE note ADD label varchar(256);
        ''')

    def upgrade_20070319(my):
        my.run_sql('''
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('flash/nat_pause', 'flash', 'Nat Pause', '{project}', 'nat_pause', 'pyasm.search.SObject', 'Nat Pause', 'public');
        ''')


    def upgrade_20070318(my):
        my.run_sql('''
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('flash/script', 'flash', 'Scripts', '{project}', 'script', 'pyasm.search.SObject', 'Scripts', 'public');
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('flash/storyboard', 'flash', 'Storyboards', '{project}', 'storyboard', 'pyasm.search.SObject', 'Storyboards', 'public');
        ''')


    def upgrade_20070309(my):
        from pyasm.security import LoginGroup
        from pyasm.search import SObject
        from pyasm.common import Xml

        group = LoginGroup.get_by_code('admin')
        rules = group.get_xml_value('access_rules', root='rules')

        new_rule = '''
        <rules>
            <group type='UserAssignWdg' default='deny'>
               <rule key='supe' access='view'/>
               <rule key='admin' access='view'/>
            </group>
        </rules>
        '''
        new_xml = Xml()
        new_xml.read_string(new_rule)
        new_node = new_xml.get_node('rules/group')

        top_node = rules.get_node('rules')
        top_node.appendChild(new_node)

        group.set_value('access_rules', rules.to_string())
        group.commit()

        my.run_sql('''
        
        INSERT INTO login_group (login_group, description, access_rules) 
            VALUES ('supe', 'Supervisor', NULL);
        ''')

    def upgrade_20070208(my):
        my.run_sql('''
        ALTER TABLE notification ADD email_handler_cls varchar(200);
        ''')

    def upgrade_20070203(my):
        my.run_sql('''
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/camera', 'prod', 'Camera Information', '{project}', 'camera', 'pyasm.search.SObject', 'Camera Infomartion', 'public');
        ''')


    def upgrade_20070129(my):
        my.run_sql('''
INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('prod/prod_setting', 'prod', 'Production Settings', '{project}', 'prod_setting', 'pyasm.prod.biz.ProdSetting', 'Production Settings', 'public');
        ''')

    def upgrade_20070125(my):

        my.run_sql('''
        ALTER TABLE project ADD node_naming_cls varchar(200);
        ''')

    def upgrade_20070118(my):

        my.run_sql('''

INSERT INTO search_object (search_type, namespace, description, [database], table_name, class_name, title, [schema]) VALUES ('effects/plate', 'effects', 'Production Plates', '{project}', 'plate', 'pyasm.effects.biz.Plate', 'Production plates', 'public');


        CREATE INDEX transaction_log_idx ON transaction_log USING btree ([timestamp]);

        UPDATE search_object SET title = description;
        UPDATE search_object SET title = '3D Asset' where search_type='prod/asset';
        UPDATE search_object SET title = 'Sequence' where search_type='prod/sequence';
        UPDATE search_object SET title = 'Session Contents' where search_type='prod/session_contents';
        UPDATE search_object SET title = 'Shot' where search_type='prod/shot';
        UPDATE search_object SET title = 'Shot Instance' where search_type='prod/shot_instance';
        UPDATE search_object SET title = 'Submission' where search_type='prod/submission';
        UPDATE search_object SET title = 'Template' where search_type='prod/template';
        UPDATE search_object SET title = 'Render Stage' where search_type='prod/render_stage';
        UPDATE search_object SET title = 'Command Log' where search_type='sthpw/command_log';
        UPDATE search_object SET title = 'Render Stage' where search_type='sthpw/render_stage';
        UPDATE search_object SET title = 'File' where search_type='sthpw/file';
        UPDATE search_object SET title = 'Groups' where search_type='sthpw/login_group';
        UPDATE search_object SET title = 'Notes' where search_type='sthpw/note';
        UPDATE search_object SET title = 'Pipelines' where search_type='sthpw/pipeline';
        UPDATE search_object SET title = 'Status Log' where search_type='sthpw/status_log';
        UPDATE search_object SET title = 'Notification' where search_type='sthpw/notification';
        UPDATE search_object SET title = 'Group Notification' where search_type='sthpw/group_notification';
        UPDATE search_object SET title = 'Snapshot' where search_type='sthpw/snapshot';
        UPDATE search_object SET title = 'Ticket' where search_type='sthpw/ticket';
        UPDATE search_object SET title = 'Search Objects' where search_type='sthpw/search_object';
        UPDATE search_object SET title = 'Timecard' where search_type='sthpw/timecard';
        UPDATE search_object SET title = 'Widget Settings' where search_type='sthpw/wdg_settings';
        UPDATE search_object SET title = 'Transaction Log' where search_type='sthpw/transaction_log';
        UPDATE search_object SET title = 'Command Triggers' where search_type='sthpw/trigger_in_command';
        UPDATE search_object SET title = 'SObject Log' where search_type='sthpw/sobject_log';

        ''')


    def upgrade_20070117(my):
        my.run_sql('''
        -- ADD a description column 
        ALTER TABLE pipeline ADD description text;
        ''')
        
    def upgrade_20070102(my):
        my.run_sql('''
        ALTER TABLE snapshot ADD label varchar(100);
        ''')
        
    def upgrade_20061209(my):
        my.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, 
        database, table_name, class_name ) VALUES(
        'prod/submission', 'prod', 'Submission of quicktime for an asset', '{project}',
        'submission','pyasm.prod.biz.Submission'); 

        INSERT INTO search_object (search_type, namespace, description, 
        database, table_name, class_name ) VALUES(
        'prod/bin', 'prod', 'Bin for submissions', '{project}',
        'bin','pyasm.prod.biz.Bin'); 

        INSERT INTO search_object (search_type, namespace, description, 
        database, table_name, class_name ) VALUES(
        'prod/submission_in_bin', 'prod', 'Submissions in Bins', '{project}',
        'submission_in_bin','pyasm.prod.biz.SubmissionInBin'); 
        ''')

    def upgrade_20061208(my):
        my.run_sql('''
        -- ADD an sobject that connects sobjects together
        CREATE TABLE connection (
            id INT IDENTITY,
            context varchar(60),
            project_code varchar(30),
            src_search_type varchar(200),
            src_search_id int4,
            dst_search_type varchar(200),
            dst_search_id int4,
            login varchar(30),
            [timestamp] datetime2(6)
        );
        INSERT INTO search_object (search_type, namespace, description, 
        database, table_name, class_name, title ) VALUES(
        'sthpw/connection', 'sthpw', 'SObject Connections', 'sthpw',
        'connection','pyasm.search.SObject', 'SObject Connection'); 
        ''') 


    def upgrade_20061207(my):
        my.run_sql('''
        -- rename a column in remote_repo
         ALTER TABLE remote_repo rename column workup_base_di 
            to sandbox_base_dir;
         ''')
        

    def upgrade_20061201(my):
        my.run_sql('''
        -- ADD a notes table for all notes
        CREATE TABLE note (
            id INT IDENTITY,
            project_code varchar(30),
            search_type varchar(200),
            search_id int4,
            login varchar(30),
            context varchar(60),
            [timestamp] datetime2(6) DEFAULT (getdate()),
            note text
        );
        INSERT INTO search_object (search_type, namespace, description, 
        database, table_name, class_name ) VALUES(
        'sthpw/note', 'sthpw', 'Notes for all Assets', 'sthpw',
        'note','pyasm.biz.Note'); 
        ''')




 
    def upgrade_20061129(my):
        my.run_sql('''
        -- ADD a remote_repo table
        CREATE TABLE remote_repo (
            id INT IDENTITY,
            code varchar(30),
            ip_address varchar(30),
            ip_mask varchar(30),
            repo_base_dir varchar(200),
            workup_base_di varchar(200)
        );
        INSERT INTO search_object (search_type, namespace, description, 
        database, table_name, class_name ) VALUES(
        'sthpw/remote_repo', 'sthpw', 'Remote Repositories', 'sthpw',
        'remote_repo','pyasm.search.SObject'); 
        ''')


   
   
    def upgrade_20061126(my):
        my.run_sql('''
        -- ADD a project_code column in pipeline
        ALTER TABLE pipeline ADD project_code varchar(30);
        -- ADD foreign key
        ALTER TABLE pipeline ADD constraint project_code_foreign foreign key 
        (project_code) references project (code) on
        UPDATE cascade ON delete restrict deferrable initially deferred;
        ''')

        
    def upgrade_20061122(my):
        my.run_sql('''
        -- ADD a file naming handler
        ALTER TABLE project ADD file_naming_cls varchar(200);

        -- unique index for project_code
        CREATE UNIQUE INDEX project_code_idx ON project USING btree (code);

        -- unique index for snapshot code
        CREATE UNIQUE INDEX snapshot_code_idx ON snapshot USING btree (code);
        ''')

    def upgrade_20061115(my):
        my.run_sql('''
        -- ADD a reg_hours column to project
        ALTER TABLE project ADD reg_hours float;
        -- create a timecard table
        CREATE TABLE timecard
        (
          id INT IDENTITY NOT NULL,
          search_type varchar(100),
          search_id int4,
          week int2,
          mon float4,
          tue float4,
          wed float4,
          thu float4,
          fri float4,
          sat float4,
          sun float4,
          [login] varchar(100),
          project_code varchar(30),
          CONSTRAINT timecard_pkey ,
          CONSTRAINT login_foreign FOREIGN KEY ([login])
              REFERENCES [login] ([login]) MATCH SIMPLE
              ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED,
          CONSTRAINT project_code_foreign FOREIGN KEY (project_code)
              REFERENCES project (code) MATCH SIMPLE
              ON UPDATE CASCADE ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED
        ); 
        
        
        ''')

    def upgrade_20061112(my):
        my.run_sql('''
        -- make some changes to the notification table
        ALTER TABLE notification ADD project_code varchar(30);
        ALTER TABLE notification ADD rules text;
        ALTER TABLE notification ADD message text;
        ALTER TABLE notification drop column context;

        -- ADD initials to the project
        ALTER TABLE project ADD initials VARCHAR(30);

        -- ADD s_status to login
        ALTER TABLE login ADD s_status VARCHAR(30);
        ''')
 
    def upgrade_20061110(my):
        my.run_sql('''
        -- rename pipeline name to pipeline code
        ALTER TABLE pipeline rename column name to code;
        -- rename to pipeline_code in task
        ALTER TABLE task rename column pipeline to pipeline_code;

        ALTER TABLE 
        -- ADD foreign key
        ALTER TABLE task ADD constraint pipeline_code_foreign foreign key 
        (pipeline_code) references pipeline (code) on
        UPDATE cascade ON delete restrict deferrable initially deferred;
        ''')
        
    def upgrade_20061109(my):
        my.run_sql('''
        -- ADD a description to project
        ALTER TABLE project ADD description text;
        ''')
 
    def upgrade_20061108(my):
        my.run_sql('''
        ALTER TABLE queue ADD s_status varchar(30);
        CREATE UNIQUE INDEX snapshot_code_idx ON snapshot USING btree (code);`

        ALTER TABLE task ADD pipeline varchar(30);
        ''')

    def upgrade_20061017(my):
        my.run_sql('''
        -- ADD the milestone_code column in task
        ALTER TABLE task ADD milestone_code varchar(200);
        -- ADD constraints
        ALTER TABLE milestone ADD constraint milestone_unique UNIQUE(code);
        ALTER TABLE task ADD constraint milestone_code_foreign FOREIGN 
            KEY(milestone_code) references milestone(code) on
            UPDATE cascade ON delete restrict deferrable initially deferred;

        -- ADD a pipeline to tasks
        ALTER TABLE task ADD pipeline_code varchar(30);
        UPDATE table task set pipeline = 'task';
        ''')
        
    def upgrade_20061004(my):
        my.run_sql('''
        -- ADD a milestone table with a foreign key
        CREATE TABLE milestone (
            id              INT IDENTITY,
            code            varchar(200),
            project_code    varchar(30),
            description     text,
            due_date        datetime2(6),
                
        );
        ALTER TABLE milestone ADD foreign key (project_code)
            references project(code) ON UPDATE cascade ON delete restrict
            deferrable initially deferred;

        -- register the sobject
        INSERT INTO search_object (search_type, namespace, description, 
        database, table_name, class_name ) VALUES(
        'sthpw/milestone', 'sthpw', 'Project Milestones', 'sthpw',
        'milestone','pyasm.search.SObject'); 
        ''')



    def upgrade_20061001(my):
        my.run_sql('''
        -- ADD project_code column to wdg_settings with foreign key
        ALTER TABLE wdg_settings ADD project_code varchar(30);
        ALTER TABLE wdg_settings ADD foreign key (project_code)
            references project(code) ON UPDATE cascade ON delete restrict
            deferrable initially deferred;

        -- make key, login, project_code unique
        ALTER TABLE wdg_settings drop constraint "wdg_settings_key_idx";
        ALTER TABLE wdg_settings ADD constraint "wdg_settings_unique" unique(key, login, project_code);
        ''')
        
    def upgrade_20060918(my):
        my.run_sql('''
        -- change from name to id
        -- ADD unique key to name
        ALTER TABLE pipeline drop constraint pipeline_pkey;
        ALTER TABLE pipeline ADD unique (name);
        ALTER TABLE pipeline ADD ;

        -- insert ea/asset_library
        INSERT INTO search_object (search_type, namespace, description, 
        database, table_name, class_name, title, schema) VALUES(
        'ea/asset_library', 'game', 'Game Asset library', '{project}',
        'asset_library','pyasm.search.SObject', 'Asset Library', 'public'); 
       
        -- UPDATE class_name for project
        UPDATE search_object SET class_name = 'pyasm.biz.Project' where 
        search_type = 'sthpw/project';
        
        ''')

    def upgrade_20060906(my):
        my.run_sql('''
        -- keep track of users
        ALTER TABLE project ADD last_db_UPDATE datetime2(6);
        ALTER TABLE project ADD type varchar(30);

        -- allow pictures of users to be uploaded
        ALTER TABLE login ADD snapshot text;


        -- search optimization for snapshots
        CREATE UNIQUE INDEX snapshot_code_idx ON snapshot USING btree (code);

        -- search optimization for the queue
        CREATE INDEX queue_idx ON queue USING btree (queue, state);

        -- change from id to code
        ALTER TABLE project DROP CONSTRAINT project_pkey;
        ALTER TABLE ONLY project ADD CONSTRAINT project_pkey (code);

        -- search optimization for wdg_settings
        ALTER TABLE ONLY wdg_settings ADD CONSTRAINT wdg_settings_key_idx UNIQUE ([login], "key");
        ''')

        





