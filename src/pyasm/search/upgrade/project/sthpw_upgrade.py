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


from pyasm.search.upgrade.project import *

class SthpwUpgrade(BaseUpgrade):


    #
    # 4.6.0.a03
    #
    def upgrade_v4_6_0_a03_007(self):
       self.run_sql('''
       ALTER TABLE "login_group" ADD COLUMN data jsonb;
       ''')


    def upgrade_v4_6_0_a03_006(self):
       self.run_sql('''
       ALTER TABLE "login" ADD COLUMN data jsonb;
       ''')


    def upgrade_v4_6_0_a03_005(self):
       self.run_sql('''
       ALTER TABLE "login" ADD COLUMN keywords_data jsonb;
       ''')

    def upgrade_v4_6_0_a03_004(self):
       self.run_sql('''
       ALTER TABLE "login" ADD COLUMN keywords text;
       ''')

    def upgrade_v4_6_0_a03_003(self):
       self.run_sql('''
       ALTER TABLE "notification_login" ADD COLUMN status varchar(256);
       ''')

    def upgrade_v4_6_0_a03_002(self):
       self.run_sql('''
       ALTER TABLE "watch_folder" ADD COLUMN file_handler_cls varchar(256);
       ''')

    def upgrade_v4_6_0_a03_001(self):
       self.run_sql('''
       ALTER TABLE "note" ADD COLUMN parent_code varchar(256);
       ''')

    #
    # 4.6.0.a02
    #

    def upgrade_v4_6_0_a02_002(self):
        self.run_sql('''
        ALTER TABLE "pipeline" ADD COLUMN category varchar(256);
        ''')




    def upgrade_v4_6_0_a02_001(self):
        self.run_sql('''
        ALTER TABLE "retire_log" ADD COLUMN search_code varchar(256);
        ''')


    #
    # 4.6.0.a01
    #
    def upgrade_v4_6_0_a01_008(self):
        self.run_sql('''
        ALTER TABLE "connection" ALTER COLUMN login TYPE varchar(256);
        ''')

    def upgrade_v4_6_0_a01_007(self):
        self.run_sql('''
        ALTER TABLE "connection" ALTER COLUMN project_code TYPE varchar(256);
        ''')


    def upgrade_v4_6_0_a01_006(self):
        self.run_sql('''
        ALTER TABLE "connection" ALTER COLUMN context TYPE varchar(256);
        ''')


    def upgrade_v4_6_0_a01_005(self):
        self.run_sql('''
        ALTER TABLE "connection" ADD COLUMN dst_search_code varchar(256);
        ''')


    def upgrade_v4_6_0_a01_004(self):
        self.run_sql('''
        ALTER TABLE "connection" ADD COLUMN src_search_code varchar(256);
        ''')

    def upgrade_v4_6_0_a01_003(self):
        self.run_sql('''
        ALTER TABLE "task" ADD COLUMN "task_type" varchar(256);
        ''')


    def upgrade_v4_6_0_a01_002(self):
        self.run_sql('''
        ALTER TABLE "pipeline" ADD COLUMN "type" varchar(256);
        ''')


    def upgrade_v4_6_0_a01_001(self):
        self.run_sql('''
        ALTER TABLE "sync_server" ADD COLUMN "site" varchar(256);
        ''')



    #
    # 4.5.0.v02
    #
    def upgrade_v4_5_0_v02_001(self):
        self.run_sql('''
        ALTER TABLE "pref_list" ALTER COLUMN "options" TYPE text;
        ''')

    #
    # 4.5.0.b01
    #
    def upgrade_v4_5_0_b01_001(self):
        self.run_sql(''' 
        UPDATE search_object set description = 'Task', "title" = 'Task' where code = 'sthpw/task';
        ''') 



    #
    # 4.5.0.a01
    #
    def upgrade_v4_5_0_a01_012(self):
        self.run_sql(''' 
        CREATE INDEX "change_timestamp_stype_idx" ON change_timestamp (search_type);
        ''') 

    def upgrade_v4_5_0_a01_011(self):
        self.run_sql(''' 
        ALTER TABLE "login_group" ADD "name" text; 
        ''') 




    def upgrade_v4_5_0_a01_010(self):
        self.run_sql(''' 
        ALTER TABLE "login_group" ADD "is_default" boolean; 
        ''') 




    def upgrade_v4_5_0_a01_009(self):
        self.run_sql(''' 
        CREATE INDEX "sobject_log_stype_idx" ON sobject_log (search_type);
        ''') 

    def upgrade_v4_5_0_a01_008(self):

        def get_timezone_names():
            import os
            import tarfile
            import dateutil.zoneinfo

            zi_path = os.path.abspath(os.path.dirname(dateutil.zoneinfo.__file__))
            zonesfile = tarfile.TarFile.open(os.path.join(zi_path, 'zoneinfo-2008e.tar.gz'))
            zonenames = zonesfile.getnames()
            return zonenames

        # add time zone names to timezone prefernce if it does not exist
        from dateutil import tz
        from pyasm.search import Search
        pref_list_id = Search.eval("@GET(sthpw/pref_list['key','timezone'].id)")
        if not pref_list_id:
            names = get_timezone_names()
            timezones = []
            for name in names:
                try:
                    tz.gettz(name)
                    timezones.append(name)
                except:
                    continue
            timezones = sorted(timezones)
            timezone_str = '|'.join(timezones)
            timezone_str = '|%s'%timezone_str
            self.run_sql('''
                INSERT INTO pref_list ("key",description,options,"type",category,title) VALUES ('timezone','Your local time zone.', '%s','sequence','general','Time Zone');
            '''%timezone_str)

    def upgrade_v4_5_0_a01_007(self):
        self.run_sql('''
        ALTER TABLE "pref_list" ALTER COLUMN "options" TYPE text;
        ''')


    def critical_v4_5_0_a01_006(self):
        self.run_sql('''
        ALTER TABLE change_timestamp ADD COLUMN "timestamp" timestamp;
        ''')


    def upgrade_v4_5_0_a01_005(self):
        self.run_sql('''
        CREATE INDEX "sobject_log_timestamp_idx" on sobject_log(timestamp);
        ''')

    def upgrade_v4_5_0_a01_004(self):
        self.run_sql('''
        ALTER TABLE sobject_log ADD COLUMN action varchar(128);
        ''')

    def upgrade_v4_5_0_a01_003(self):
        self.run_sql('''
        ALTER TABLE sobject_log ADD COLUMN parent_code varchar(256);
        ''')


    def upgrade_v4_5_0_a01_002(self):
        self.run_sql('''
        ALTER TABLE sobject_log ADD COLUMN parent_type varchar(256);
        ''')


 

    def upgrade_v4_5_0_a01_001(self):
        self.run_sql('''
        CREATE INDEX "change_timestamp_timestamp_idx" on change_timestamp(timestamp);
        ''')


    def upgrade_v4_4_0_v01_006(self):

        if self.get_database_type() == 'MySQL':
            self.run_sql('''
            ALTER table "file" MODIFY "code" varchar(256) NULL;
            ''')
        elif self.get_database_type() == 'SQLServer':
            self.run_sql('''
            ALTER TABLE "file" alter COLUMN "code" varchar(256) NULL;
            ''')
        else:
            self.run_sql('''
            ALTER TABLE "file" alter COLUMN "code" DROP not NULL;
            ''')

    def upgrade_v4_4_0_v01_005(self):
        self.run_sql(''' 

        INSERT INTO search_object (code, search_type, "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/department','sthpw/department','sthpw','Department','sthpw','department','pyasm.search.SObject','Department','public');

        ''')


    def upgrade_v4_4_0_v01_004(self):
        self.run_sql(''' 
        CREATE TABLE department (
        id serial PRIMARY KEY,
        code varchar(256),
        name varchar(256),
        login varchar(256),
        ou text,
        CONSTRAINT "department_code_idx" UNIQUE (code),
        CONSTRAINT "department_name_idx" UNIQUE (name)
        );
        ''') 

    def upgrade_v4_4_0_v01_003(self):
        self.run_sql(''' 

        ALTER TABLE login add constraint "login_upn_idx" UNIQUE (upn);
        ''') 
    def upgrade_v4_4_0_v01_002(self):
        self.run_sql(''' 
        UPDATE login set upn = login where upn is NULL;
        ''')

    def upgrade_v4_4_0_v01_001(self):
        self.run_sql(''' 
        ALTER TABLE "login" ADD "upn" varchar(256) NULL; 
        ''') 
        
    def upgrade_v4_4_0_b01_007(self):
        self.run_sql(''' 
        ALTER TABLE "login" ADD "location" text NULL; 
        ''') 

    #
    # 4.4.0.a01
    #
   


    def upgrade_v4_4_0_a01_006(self):
        self.run_sql('''
        ALTER TABLE pipeline ADD COLUMN "parent_process" varchar(256);
        ''')


    def upgrade_v4_4_0_a01_005(self):
        self.run_sql('''
        INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/interaction', 'sthpw/interaction', 'sthpw', 'User Interaction', 'sthpw', 'interaction', 'pyasm.search.SObject', 'User Interaction', 'public');
        ''')
 


    def upgrade_v4_4_0_a01_004(self):
        self.run_sql('''
        ALTER TABLE pipeline ADD COLUMN "name" varchar(256);
        ''')


    def upgrade_v4_4_0_a01_003(self):
        self.run_sql('''
        ALTER TABLE search_object ADD COLUMN "type" varchar(128);
        ''')



    def upgrade_v4_4_0_a01_002(self):
        self.run_sql('''
        CREATE INDEX "interaction_key_idx" on interaction (key);
        ''')



    def upgrade_v4_4_0_a01_001(self):
        self.run_sql('''
        CREATE TABLE interaction (
            id serial PRIMARY KEY,
            code varchar(256),
            project_code varchar(256),
            login varchar(256),
            key varchar(1024),
            data text,
            "timestamp" timestamp default now()
        );
        ''')





    def upgrade_v4_3_0_v02_001(self):

        if self.get_database_type() == 'MySQL':
            self.run_sql('''
            ALTER table pipeline MODIFY code varchar(128) NULL;
            ''')
        elif self.get_database_type() == 'SQLServer':
            self.run_sql('''
            ALTER table pipeline ALTER COLUMN code varchar(128) NULL;
            ''')
        else:
            self.run_sql('''
            ALTER TABLE pipeline ALTER COLUMN code DROP NOT NULL;
            ''')


    
    #
    # 4.2.0.a01
    #
    def upgrade_v4_2_0_a01_017(self):
       self.run_sql(''' 
        ALTER TABLE "login" ADD "location" text NULL; 
        ''') 

    def upgrade_v4_2_0_a01_016(self):
        self.run_sql('''
        ALTER TABLE login ADD  "login_attempt" INT;
        ''')

    def upgrade_v4_2_0_a01_015(self):
        self.run_sql('''
        INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/custom_script', 'sthpw/custom_script', 'sthpw', 'Central Custom Script', 'sthpw', 'custom_script', 'pyasm.search.SObject', 'Custom Script', 'public');
        ''')
            

    def upgrade_v4_2_0_a01_014(self):
        if self.get_database_type() == 'MySQL':
            self.run_sql('''
            ALTER table queue MODIFY serialized varchar(256) NULL;
            ''')
        elif self.get_database_type() == 'SQLServer':
            self.run_sql('''
            ALTER table queue ALTER COLUMN serialized varchar(256) NULL;
            ''')
        else:
            self.run_sql('''
            ALTER table queue ALTER COLUMN serialized DROP NOT NULL;
            ''')


    def upgrade_v4_2_0_a01_013(self):
        self.run_sql('''ALTER TABLE sync_server ADD COLUMN file_mode varchar(256);''')

    def upgrade_v4_2_0_a01_012(self):
        self.run_sql('''
        ALTER TABLE "watch_folder" ADD "script_path" varchar(1024);
        ''')


    def upgrade_v4_2_0_a01_011(self):
        self.run_sql('''
        CREATE TABLE translation (
            id serial PRIMARY KEY,
            code character varying(256),
            name character varying(256),
            en text,
            fr text,
            ja text,
            es text,
            login character varying(256),
            "timestamp" timestamp without time zone DEFAULT now(),
            CONSTRAINT "translation_code_idx" UNIQUE (code),
            CONSTRAINT "translation_name_idx" UNIQUE (name)
        );
        ''')


    def upgrade_v4_2_0_a01_010(self):
        self.run_sql('''
        DROP TABLE "translation";
        ''')




    def upgrade_v4_2_0_a01_008(self):
        self.run_sql('''INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/translation', 'config/translation', 'config', 'Translation', '{project}', 'spt_translation', 'pyasm.search.SObject', 'Translation', 'public');
        ''')

 

    def upgrade_v4_2_0_a01_007(self):
        self.run_sql('''INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/watch_folder', 'sthpw/watch_folder', 'sthpw', 'Watch Folder', 'sthpw', 'watch_folder', 'pyasm.search.SObject', 'Watch Folder', 'public');
        ''')

    def upgrade_v4_2_0_a01_006(self):
        self.run_sql('''
        CREATE TABLE watch_folder (
            id serial PRIMARY KEY,
            code varchar(256),
            name varchar(256),
            project_code varchar(256),
            base_dir text,
            search_type varchar(256),
            process varchar(256),
            "timestamp" timestamp
        );
        ''') 



    def upgrade_v4_2_0_a01_005(self):
        self.run_sql('''
        ALTER TABLE "search_object" ADD "metadata_parser" varchar(256);
        ''')


    def upgrade_v4_2_0_a01_004(self):
        self.run_sql('''
        CREATE INDEX "queue_state_idx" on queue (state);
        ''')

    def upgrade_v4_2_0_a01_003(self):
        self.run_sql('''
        ALTER TABLE "queue" ADD "message_code" varchar(256);
        ''')


    def upgrade_v4_2_0_a01_002(self):
        self.run_sql('''
        ALTER TABLE "queue" ADD "data" text;
        ''')



    def upgrade_v4_2_0_a01_001(self):
        self.run_sql('''
        ALTER TABLE "search_object" ADD "message_event" varchar(256);
        ''')

    
    def upgrade_v4_1_0_v04_001(self):
        self.run_sql('''
        INSERT INTO pref_list ("key",description,options,"type",category,title) VALUES ('subscription_bar','Determine whether to show the Subscription Bar','|true|false','sequence','display','Subscription Bar');
        ''')


    #
    # 4.1.0.v03
    #
    def upgrade_v4_1_0_v03_001(self):
        self.run_sql('''
          ALTER TABLE "search_object" ADD "message_event" varchar(256);
        ''')
  


    def upgrade_v4_1_0_v01_001(self):
        self.run_sql('''UPDATE "search_object" SET code = search_type;''')

    #
    # 4.1.0.b03
    #


    def upgrade_v4_1_0_b03_002(self):
        self.run_sql('''INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/department', 'sthpw/department', 'sthpw', 'Department', 'sthpw', 'department', 'pyasm.search.SObject', 'Department', 'public');
        ''')


    def upgrade_v4_1_0_b03_001(self):
        self.run_sql('''
        CREATE TABLE department (
            id serial PRIMARY KEY,
            code varchar(256),
            name varchar(256),
            "timestamp" timestamp
        );
        ''') 



    #
    # 4.1.0.b02
    #


    def upgrade_v4_1_0_b02_002(self):
        self.run_sql('''
        UPDATE search_object SET table_name = 'spt_pipeline', class_name = 'pyasm.biz.ProjectPipeline', code = 'config/pipeline'  where search_type = 'config/pipeline';
        ''')




    def upgrade_v4_1_0_b02_001(self):
        self.run_sql('''
        ALTER TABLE "schema" ADD "project_code" varchar(256);
        ''')


   
    #
    # 4.1.0.a01
    #

    def upgrade_v4_1_0_a01_013(self):
        if self.get_database_type() == 'MySQL':
            self.run_sql(''' ALTER TABLE "snapshot" MODIFY "search_id" integer NULL;''')
        elif self.get_database_type() == 'SQLServer':
            self.run_sql(''' ALTER TABLE "snapshot" ALTER COLUMN "search_id" integer NULL;''');
        else:
            self.run_sql('''
            ALTER TABLE "snapshot" ALTER COLUMN "search_id" DROP NOT NULL;
            ''')


    def upgrade_v4_1_0_a01_012(self):
        if self.get_database_type() == 'MySQL':
            self.run_sql(''' ALTER TABLE  "sobject_log" MODIFY "search_id" integer NULL;''')
        elif self.get_database_type() == 'SQLServer':
            self.run_sql(''' ALTER TABLE "sobject_log" ALTER COLUMN "search_id" integer NULL;''');
        else:
            self.run_sql('''
            ALTER TABLE "sobject_log" ALTER COLUMN "search_id" DROP NOT NULL;
            ''')



    def upgrade_v4_1_0_a01_011(self):
        self.run_sql('''
        ALTER TABLE "search_object" ADD "id_column" varchar(256);
        ''')


    def upgrade_v4_1_0_a01_010(self):
        if self.get_database_type() == 'MySQL':
            self.run_sql(''' ALTER TABLE "file" MODIFY "file_name" varchar(512) NULL;''')
        elif self.get_database_type() == 'SQLServer':
            self.run_sql(''' ALTER TABLE "file" ALTER COLUMN "file_name" varchar(512) NULL;''');
        else:
            self.run_sql('''
        ALTER TABLE "file" ALTER COLUMN "file_name" DROP NOT NULL;
        ''')




    def upgrade_v4_1_0_a01_009(self):
        self.run_sql('''
        ALTER TABLE search_object ADD "default_layout" VARCHAR(32);
        ''')




    def upgrade_v4_1_0_a01_008(self):
        self.run_sql('''INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/message_log', 'sthpw/message_log', 'sthpw', 'Message Log', 'sthpw', 'message_log', 'pyasm.search.SObject', 'Message Log', 'public');
        ''')


    def upgrade_v4_1_0_a01_007(self):
        self.run_sql('''
        CREATE TABLE message_log (
            id serial PRIMARY KEY,
            code varchar(256),
            message_code varchar(256),
            category varchar(256),
            message text,
            status varchar(32),
            login varchar(256),
            project_code varchar(32),
            "timestamp" timestamp
        );
        ''') 




    def upgrade_v4_1_0_a01_006(self):
        self.run_sql('''INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/plugin_content', 'config/plugin_content', 'config', 'Plugin Contents', '{project}', 'spt_plugin_content', 'pyasm.search.SObject', 'Plugin Contents', 'public');
        ''')


    def upgrade_v4_1_0_a01_005(self):
        self.run_sql('''INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/subscription', 'sthpw/subscription', 'sthpw', 'Subscription', 'sthpw', 'subscription', 'pyasm.search.SObject', 'Subscription', 'public');
        ''')


    def upgrade_v4_1_0_a01_004(self):
        self.run_sql('''
        CREATE INDEX "subscription_message_code_idx" on subscription (message_code);
        ''')



    def upgrade_v4_1_0_a01_003(self):
        self.run_sql('''
        CREATE TABLE subscription (
            id serial PRIMARY KEY,
            code varchar(256),
            category varchar(256),
            message_code varchar(256),
            login varchar(256),
            project_code varchar(32),
            status varchar(32),
            last_cleared timestamp,
            "timestamp" timestamp,
            CONSTRAINT "subscription_code_idx" UNIQUE (code)
        );
        ''') 




    def upgrade_v4_1_0_a01_002(self):
        self.run_sql('''INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/message', 'sthpw/message', 'sthpw', 'Messages', 'sthpw', 'message', 'pyasm.search.SObject', 'Message', 'public');
        ''')


    def upgrade_v4_1_0_a01_001(self):
        self.run_sql('''
        CREATE TABLE message (
            id serial PRIMARY KEY,
            code varchar(256),
            category varchar(256),
            message text,
            status varchar(32),
            login varchar(256),
            project_code varchar(32),
            "timestamp" timestamp,
            CONSTRAINT "message_code_idx" UNIQUE (code)
        );
        ''') 



    
    def upgrade_v4_0_0_rc02_002(self):
        self.run_sql('''
        ALTER TABLE sobject_log ADD "code" VARCHAR(256);
        ''')   


    def upgrade_v4_0_0_rc02_001(self):
        self.run_sql('''
        ALTER TABLE debug_log ADD "code" VARCHAR(256);
        ''')   

    def upgrade_v4_0_0_rc01_001(self):
        self.run_sql('''
        ALTER TABLE trigger add "code" VARCHAR(256);
        ''')

    #
    # 4.0.0.b03
    #
    def upgrade_v4_0_0_b03_002(self):

        if self.is_confirmed not in [True, 'true']:
            print '''

IMPORTANT NOTICE:
        
        
        You are upgrading from an earlier version to 4.0.  TACTIC version 4.0 has made some important changes, particularly in the way that some tables are related to each other.  Previously, TACTIC would relate such items as snapshots, tasks and notes by the column "search_id".  In 4.0, this has been changed to "search_code".  The "search_id" will still exists, but wil not be used to relate tables.
        
        In order to upgrade, TACTIC needs to fill in the "search_code" column of various tables.  This is a heavy process if you have a lot of data.  It is a non-destructive script and will only add data.  It will not change any current existing data.  You may wish to run this separately if you have large projects with lots of data.

        You can run this script now or you can run it manually by:

        python <TACTIC_INSTALL_DIR>/src/bin/fixes/fix_search_code.py

            '''

            confirm = raw_input("Run now? (y/n):")
            if not confirm in ['y', 'Y', 'yes', 'Yes']:
                return



        from pyasm.common import Config, Environment, Container
        import os, sys
        python = sys.executable

        install_dir = Environment.get_install_dir()
        path = '"%s/src/bin/fixes/fix_search_code.py"' % install_dir

        print "Running ..."
        print
        cmd = "%s %s" % (python, path)
        print "cmd: ", cmd
        print
        os.system(cmd)
        print
            





    def upgrade_v4_0_0_b03_001(self):
        self.run_sql('''
        ALTER TABLE project ADD "database" VARCHAR(256);
        ''')




    #
    # 4.0.0.b03
    #
    def upgrade_v4_0_0_b03_001(self):
        self.run_sql('''
        ALTER TABLE project ADD "database" VARCHAR(256);
        ''')



    #
    # 4.0.0.b01
    #
    def upgrade_v4_0_0_b01_003(self):
        self.run_sql('''
        ALTER TABLE sync_job ADD transaction_code VARCHAR(256);
        ''')


    def upgrade_v4_0_0_b01_002(self):
        self.run_sql('''
        ALTER TABLE clipboard ADD search_code varchar(256);
        ''')

    def upgrade_v4_0_0_b01_001(self):
        self.run_sql('''
        CREATE UNIQUE INDEX "sync_server_code_idx" on sync_server (code);
        ''')
    #
    # 4.0.0.a09
    #
    def upgrade_v4_0_0_a09_002(self):
        if self.get_database_type() == 'MySQL':
            self.run_sql('''ALTER TABLE file MODIFY search_id integer NULL;''')
        elif self.get_database_type() == 'SQLServer':
            self.run_sql('''ALTER TABLE file ALTER COLUMN search_id integer NULL;''')
        else:
            self.run_sql('''
            ALTER TABLE file ALTER COLUMN search_id DROP NOT NULL;
            ''')
   
  

    def upgrade_v4_0_0_a09_001(self):
        self.run_sql('''
        ALTER TABLE task ADD data text;
        ''')


    #
    # 4.0.0.a03
    #
    def critical_v4_0_0_a03_006(self):
        self.run_sql('''
        CREATE UNIQUE INDEX change_timestamp_code_idx ON change_timestamp (code)
        ''')



    def upgrade_v4_0_0_a03_005(self):
        self.run_sql('''
        CREATE UNIQUE INDEX sync_job_code_idx ON sync_job (code)
        ''')




    def upgrade_v4_0_0_a03_004(self):
        self.run_sql('''
        CREATE UNIQUE INDEX sync_log_transaction_idx ON sync_log (transaction_code)
        ''')

    def upgrade_v4_0_0_a03_003(self):
        self.run_sql('''ALTER TABLE wdg_settings ADD COLUMN code varchar(256);''')



    def upgrade_v4_0_0_a03_002(self):
        self.run_sql('''INSERT INTO search_object (code, search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/sync_log', 'sthpw/sync_log', 'sthpw', 'List of all processed incoming sync jobs', 'sthpw', 'sync_log', 'pyasm.search.SObject', 'Sync Log', 'public');
        ''')

    def upgrade_v4_0_0_a03_001(self):
        self.run_sql('''
        CREATE TABLE sync_log (
            id serial PRIMARY KEY,
            code varchar(256),
            transaction_code varchar(256),
            status varchar(256),
            error varchar(256),
            login varchar(256),
            "timestamp" timestamp,
            project_code varchar(256)
        );
        ''')


    #
    # 4.0.0.a02
    #

    def critical_v4_0_0_a02_008(self):
        self.run_sql('''
        CREATE UNIQUE INDEX change_timestamp_idx ON change_timestamp (search_type, search_code)
        ''')


    def upgrade_v4_0_0_a02_007(self):
        self.run_sql('''
        ALTER TABLE prod_setting add CONSTRAINT prod_setting_code_unique UNIQUE (code);
        ''')

    def upgrade_v4_0_0_a02_006(self):
        self.run_sql('''ALTER TABLE prod_setting ADD COLUMN code varchar(256);''')

    def upgrade_v4_0_0_a02_005(self):
        self.run_sql('''ALTER TABLE sync_server ADD COLUMN base_dir text;''')

    def upgrade_v4_0_0_a02_004(self):
        self.run_sql('''ALTER TABLE sync_server ADD COLUMN sync_mode varchar(256);''')

 

    def upgrade_v4_0_0_a02_003(self):
        self.run_sql('''ALTER TABLE sync_server ADD COLUMN description text;''')

 
    def upgrade_v4_0_0_a02_002(self):
        self.run_sql('''ALTER TABLE sync_server ADD COLUMN access_rules text;''')



    def upgrade_v4_0_0_a02_001(self):
        self.run_sql('''ALTER TABLE sobject_list ADD COLUMN search_code VARCHAR(256);''')



    #
    # 4.0.0.a01
    #

    """
    def upgrade_v4_0_0_a01_041(self):
        self.run_sql('''ALTER TABLE task alter column "bid_start_date" type timestamp with time zone;
                       ALTER TABLE task alter column "bid_end_date" type timestamp with time zone;
                       ALTER TABLE task alter column "actual_start_date" type timestamp with time zone;
                       ALTER TABLE task alter column "actual_end_date" type timestamp with time zone;
                       ''')

    def upgrade_v4_0_0_a01_040(self):
        self.run_sql('''
                       ALTER TABLE file alter column "timestamp" type timestamp with time zone;
                       ALTER TABLE notification_log alter column "timestamp" type timestamp with time zone;
                       ALTER TABLE note alter column "timestamp" type timestamp with time zone;
                       ALTER TABLE snapshot alter column "timestamp" type timestamp with time zone;
                       ALTER TABLE status_log alter column "timestamp" type timestamp with time zone;
                       ALTER TABLE task alter column "timestamp" type timestamp with time zone;
                       ALTER TABLE transaction_log alter column "timestamp" type timestamp with time zone;
                       ''')
    """


    def upgrade_v4_0_0_a01_039(self):
        self.run_sql('''ALTER TABLE login_group ADD COLUMN code VARCHAR(256);''')

    def upgrade_v4_0_0_a01_038(self):
        self.run_sql('''CREATE INDEX "work_hour_task_idx" on work_hour (task_code);''')

    def upgrade_v4_0_0_a01_037(self):
        self.run_sql('''CREATE INDEX "work_hour_search_type_search_code_idx" on work_hour (search_type, search_code);''')

    def upgrade_v4_0_0_a01_036(self):
        self.run_sql('''CREATE INDEX "sync_job_state_idx" on sync_job (state);''')

    def upgrade_v4_0_0_a01_035(self):
        self.run_sql('''CREATE INDEX "task_search_type_search_code_idx" on task (search_type, search_code);''')

    def upgrade_v4_0_0_a01_034(self):
        self.run_sql('''CREATE INDEX "note_search_type_search_code_idx" on note (search_type, search_code);''')


    def upgrade_v4_0_0_a01_033(self):
        self.run_sql('''CREATE INDEX "snapshot_search_type_search_code_idx" on snapshot (search_type, search_code);''')





    def upgrade_v4_0_0_a01_032(self):
        self.run_sql('''ALTER TABLE sync_job ADD COLUMN server_code varchar(256);''')




   

    def upgrade_v4_0_0_a01_030(self):
        self.run_sql('''ALTER TABLE sync_job ADD COLUMN error_log text;''')


    def upgrade_v4_0_0_a01_029(self):
        self.run_sql('''ALTER TABLE snapshot ADD COLUMN server varchar(256);''')



    def upgrade_v4_0_0_a01_028(self):
        self.run_sql('''ALTER TABLE custom_property ADD COLUMN code varchar(256);''')


    def upgrade_v4_0_0_a01_027(self):
        self.run_sql('''ALTER TABLE work_hour ADD COLUMN search_code varchar(256);''')



    def upgrade_v4_0_0_a01_026(self):
        if self.get_database_type() == 'MySQL':
            self.run_sql('''ALTER TABLE snapshot MODIFY column_name varchar(100) NULL;''')
        elif self.get_database_type() == 'SQLServer':
            self.run_sql('''ALTER TABLE snapshot ALTER COLUMN column_name varchar(100) NULL;''')
        else:
            self.run_sql('''ALTER TABLE snapshot ALTER COLUMN column_name DROP NOT NULL;''')




    def upgrade_v4_0_0_a01_025(self):
        self.run_sql('''ALTER TABLE ticket ADD COLUMN code varchar(256);''')



    def upgrade_v4_0_0_a01_024(self):
        self.run_sql('''ALTER TABLE transaction_log ADD COLUMN description text;''')



    def upgrade_v4_0_0_a01_023(self):
        self.run_sql('''ALTER TABLE transaction_log ADD COLUMN description text;''')



    def upgrade_v4_0_0_a01_022(self):
        self.run_sql('''ALTER TABLE transaction_log ADD COLUMN server_code varchar(256);''')



    def upgrade_v4_0_0_a01_021(self):
        self.run_sql('''ALTER TABLE sync_server ADD COLUMN ticket varchar(256);''')



    def upgrade_v4_0_0_a01_020(self):
        self.run_sql('''ALTER TABLE clipboard ADD COLUMN code varchar(256);''')


    def upgrade_v4_0_0_a01_019(self):
        self.run_sql('''ALTER TABLE transaction_log ADD COLUMN state varchar(256);''')





    def upgrade_v4_0_0_a01_018(self):
        self.run_sql('''ALTER TABLE transaction_log ADD COLUMN ticket varchar(256);''')





    def upgrade_v4_0_0_a01_017(self):
        self.run_sql('''INSERT INTO "search_object" ("code","search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/sync_server', 'sthpw/sync_server', 'sthpw', 'Sync Server', 'sthpw', 'sync_server', 'pyasm.search.SObject', 'Sync Server', 'public');
        ''')

    def upgrade_v4_0_0_a01_016(self):
        self.run_sql('''
        CREATE TABLE sync_server (
            id serial PRIMARY KEY,
            code varchar(256),
            host varchar(256),
            login varchar(256),
            "timestamp" timestamp,
            state varchar(256)
        );
        ''')


    def upgrade_v4_0_0_a01_015(self):
        self.run_sql('''INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/sync_job','sthpw/sync_job', 'sthpw', 'Sync Job', 'sthpw', 'sync_job', 'pyasm.search.SObject', 'Sync Job', 'public');
        ''')

    def upgrade_v4_0_0_a01_014(self):
        self.run_sql('''
        CREATE TABLE sync_job (
            id serial PRIMARY KEY,
            code varchar(256),
            login varchar(256),
            "timestamp" timestamp,
            command text,
            data text,
            state varchar(256),
            host varchar(256),
            project_code varchar(256)
        );
        ''')


    def upgrade_v4_0_0_a01_013(self):
        self.run_sql('''CREATE UNIQUE INDEX transaction_log_code_idx on transaction_log(code);''')


    def upgrade_v4_0_0_a01_012(self):
        self.run_sql('''ALTER TABLE transaction_log ADD COLUMN code VARCHAR(256);''')




    def upgrade_v4_0_0_a01_011(self):
        self.run_sql('''ALTER TABLE note ADD COLUMN search_code VARCHAR(256);''')





    def upgrade_v4_0_0_a01_010(self):
        self.run_sql('''ALTER TABLE retire_log ADD COLUMN code VARCHAR(256);''')



    def upgrade_v4_0_0_a01_009(self):
        self.run_sql('''ALTER TABLE note ADD COLUMN code VARCHAR(256);''')



    def upgrade_v4_0_0_a01_008(self):
        self.run_sql('''ALTER TABLE status_log ADD COLUMN code VARCHAR(256);''')




    def upgrade_v4_0_0_a01_007(self):
        self.run_sql('''ALTER TABLE status_log ADD COLUMN search_code VARCHAR(256);''')



    def upgrade_v4_0_0_a01_006(self):
        self.run_sql('''ALTER TABLE sobject_log ADD COLUMN search_code VARCHAR(256);''')



    def upgrade_v4_0_0_a01_005(self):
        self.run_sql('''ALTER TABLE task ADD COLUMN search_code VARCHAR(256);''')


    def upgrade_v4_0_0_a01_004(self):
        self.run_sql('''ALTER TABLE snapshot ADD COLUMN search_code VARCHAR(256);''')


    def upgrade_v4_0_0_a01_003(self):
        self.run_sql('''ALTER TABLE file ADD COLUMN search_code VARCHAR(256);''')




    def upgrade_v4_0_0_a01_002(self):
        self.run_sql('''ALTER TABLE queue ADD COLUMN interval INTEGER;''')

    def upgrade_v4_0_0_a01_001(self):
        self.run_sql('''ALTER TABLE queue ADD COLUMN code VARCHAR(256);''')




    def critical_v4_0_0_a01_000c(self):
        self.run_sql('''INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/change_timestamp', 'sthpw/change_timestamp', 'sthpw', 'Change Timestamp', 'sthpw', 'change_timestamp', 'pyasm.search.SObject', 'Change Timestamp', 'public');
        ''')

    def critical_v4_0_0_a01_000b(self):
        self.run_sql('''ALTER TABLE search_object ADD COLUMN code varchar(256);''')

    def critical_v4_0_0_a01_000a(self):
        self.run_sql('''
        CREATE TABLE change_timestamp (
            id serial PRIMARY KEY,
            code varchar(256),
            search_type varchar(256),
            search_code varchar(256),
            changed_on text,
            changed_by text,
            project_code varchar(256),
            transaction_code varchar(256)
        );
        ''')

    def upgrade_v3_9_0_v05_001(self):
        self.run_sql('''CREATE INDEX "connection_src_search_type_src_search_id_idx" on connection (src_search_type, src_search_id);''')

    def upgrade_v3_9_0_v03_003(self):
        self.run_sql('''
            CREATE INDEX "task_process_idx" on task USING btree (process);
        ''')

    def upgrade_v3_9_0_v03_002(self):
        self.run_sql('''
            CREATE INDEX "task_status_idx" on task USING btree (status);
        ''')

   
    def upgrade_v3_9_0_v03_001(self):
        self.run_sql('''CREATE INDEX "connection_dst_search_type_dst_search_id_context_idx" on connection (dst_search_type, dst_search_id, context);''')

    def upgrade_v3_9_0_v02_001(self):
        self.run_sql('''ALTER TABLE task add login varchar(256)''')


    def upgrade_v3_9_0_rc05_001(self):
        self.run_sql('''ALTER TABLE spt_plugin add rel_dir text''')

 

    def upgrade_v3_9_0_rc03_005(self):
        self.run_sql('''ALTER TABLE ticket add constraint "ticket_code_idx" UNIQUE (code);''')

    def upgrade_v3_9_0_rc03_004(self):
        self.run_sql('''ALTER TABLE ticket ADD "code" varchar(256);''')

    def upgrade_v3_9_0_rc03_003(self):
        self.run_sql('''  
            UPDATE login set display_name = last_name || ', ' || first_name where display_name is NULL;
        ''')

    def upgrade_v3_9_0_rc03_002(self):
        self.run_sql('''  
            UPDATE login set first_name = '' where first_name is NULL;
        ''')

    def upgrade_v3_9_0_rc03_001(self):
        self.run_sql('''  
            UPDATE login set last_name = '' where last_name is NULL;
        ''')

    def upgrade_v3_9_0_rc02_002(self):
        self.run_sql('''  
            UPDATE "work_hour" set category='regular' where category is NULL;
        ''')
    #
    # 3.9.0.b06
    #
    def upgrade_v3_9_0_b06_020(self):
        self.run_sql('''  
            CREATE INDEX "note_search_type_search_id_idx" on note (search_type, search_id);
        ''')

    def upgrade_v3_9_0_b06_019(self):
        self.run_sql('''  
            CREATE INDEX "snapshot_search_type_search_id_idx" on snapshot (search_type, search_id);
        ''')

    def upgrade_v3_9_0_b06_018(self):
        self.run_sql('''  
            CREATE INDEX "sobject_list_search_type_search_id_idx" on sobject_list (search_type, search_id);
        ''')

    def upgrade_v3_9_0_b06_017(self):
        self.run_sql('''  
            CREATE INDEX "status_log_search_type_search_id_idx" on status_log (search_type, search_id);
        ''')

    def upgrade_v3_9_0_b06_016(self):
        self.run_sql('''  
            CREATE INDEX "task_search_type_search_id_idx" on task (search_type, search_id);
        ''')

    def upgrade_v3_9_0_b06_015(self):
        self.run_sql('''  
            ALTER TABLE sobject_list add constraint "sobject_list_code_idx" UNIQUE (code);
        ''')


    def upgrade_v3_9_0_b06_013(self):
        self.run_sql('''
        CREATE TABLE special_day (
    id serial PRIMARY KEY,
    code character varying(256),
    week integer,
    mon float, 
    tue float, 
    wed float, 
    thu float, 
    fri float, 
    sat float, 
    sun float, 
    year integer, 
    login character varying(256),
    description character varying(256),
    "type" character varying(256),
    project_code character varying(256)
);
    ''')

    def upgrade_v3_9_0_b06_012(self):
        self.run_sql('''
        ALTER TABLE search_object add constraint search_object_search_type_idx UNIQUE(search_type);
        ''')

    def upgrade_v3_9_0_b06_011(self):
        self.run_sql('''
    CREATE TABLE repo (
    id serial PRIMARY KEY,
    code character varying(256) NOT NULL,
    description character varying(256) NOT NULL,
    handler character varying(100) NOT NULL,
    web_dir character varying(256) NOT NULL,
    lib_dir character varying(256) NOT NULL
);
    ''')

    def upgrade_v3_9_0_b06_010(self):
        self.run_sql(''' 
    CREATE TABLE queue (
    id serial PRIMARY KEY,
    code character varying(256),
    queue character varying(30) NOT NULL,
    priority character varying(10) NOT NULL,
    description character varying(256),
    state character varying(30) NOT NULL DEFAULT 'pending',
    login character varying(30) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    command character varying(200) NOT NULL,
    serialized character varying(256) NOT NULL,
    s_status character varying(30),
    project_code character varying(100),
    search_id integer,
    search_type character varying(100),
    dispatcher_id integer,
    policy_code character varying(30),
    host character varying(256)
);
    ''')

    def upgrade_v3_9_0_b06_009(self):
        self.run_sql(''' 
    CREATE TABLE pref_list (
    id serial PRIMARY KEY,
    code character varying(256),
    "key" character varying(256),
    description character varying(256),
    options character varying(256),
    "type" character varying(256),
    category character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    title character varying(256),
    CONSTRAINT "pref_list_key_idx" UNIQUE ("key")
);
    ''')

    def upgrade_v3_9_0_b06_008(self):
        self.run_sql(''' 
    CREATE TABLE file_access (
    id serial PRIMARY KEY,
    code character varying(256),
    file_code integer NOT NULL,
    login character varying(100),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);
    ''')

    def upgrade_v3_9_0_b06_007(self):
        self.run_sql('''
    CREATE TABLE custom_property (
    id serial PRIMARY KEY,
    code character varying(256),
    search_type character varying(256),
    name character varying(256),
    description character varying(256),
    login character varying(256)
);
    ''')
    def upgrade_v3_9_0_b06_006(self):
        self.run_sql('''
        CREATE TABLE connection (
    id serial PRIMARY KEY,
    code character varying(256),
    context character varying(60),
    project_code character varying(30),
    src_search_type character varying(200),
    src_search_id integer,
    dst_search_type character varying(200),
    dst_search_id integer,
    login character varying(30),
    "timestamp" timestamp without time zone DEFAULT now()
);
    ''')

    def upgrade_v3_9_0_b06_005(self):
        self.run_sql('''
    CREATE TABLE snapshot_type (
    id serial PRIMARY KEY,
    code character varying(256),
    pipeline_code character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    login character varying(256),
    s_status character varying(256),
    relpath character varying(256),
    project_code character varying(256),
    subcontext character varying(256),
    snapshot_flavor character varying(256),
    relfile character varying(256),
    CONSTRAINT "snapshot_type_code_unique" UNIQUE (code)
);
    ''')

    def upgrade_v3_9_0_b06_004(self):
        self.run_sql('''
        CREATE TABLE retire_log (
            id serial PRIMARY KEY,
            code character varying(256),
            search_type character varying(100),
            search_id character varying(100),
            login character varying(100) NOT NULL,
            "timestamp" timestamp without time zone DEFAULT now(),
            CONSTRAINT "retire_log_code_idx" UNIQUE (code)

    );
    ''')

    def upgrade_v3_9_0_b06_003(self):
        self.run_sql('''
        CREATE TABLE db_resource (
    id serial PRIMARY KEY,
    code character varying(256),
    host text,
    port integer,
    vendor character varying(256),
    login character varying(256),
    password text,
    CONSTRAINT "db_resource_code_idx" UNIQUE (code)
);
    ''')

    def upgrade_v3_9_0_b06_002(self):
        self.run_sql('''
    CREATE TABLE access_log (
    id serial PRIMARY KEY,
    code character varying(256),
    url character varying(256),
    data character varying(256),
    "start_time" timestamp without time zone,
    "end_time" timestamp without time zone,
    duration double precision,
    CONSTRAINT "access_log_code_idx" UNIQUE (code)
);
    ''')

    def upgrade_v3_9_0_b06_001(self):
        self.run_sql('''
    CREATE TABLE command_log (
    id serial PRIMARY KEY,
    code character varying(256),
    class_name character varying(100) NOT NULL,
    paramaters character varying(256),
    login character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT "command_log_code_idx" UNIQUE (code)
);
        ''')    
    
  


    def upgrade_v3_9_0_rc02_002(self):
        self.run_sql('''  
            UPDATE login set display_name = last_name || ', ' || first_name;
        ''')


    def upgrade_v3_9_0_rc02_001(self):
        self.run_sql('''  
            ALTER TABLE login ADD display_name varchar(256);
        ''')



    def upgrade_v3_9_0_b09_003(self):
        self.run_sql('''  
            ALTER TABLE task ADD actual_duration float;
        ''')

    def upgrade_v3_9_0_b09_002(self):
        self.run_sql('''  
            ALTER TABLE task ADD actual_quantity float;
        ''')


    def upgrade_v3_9_0_b09_001(self):
        self.run_sql('''  
            ALTER TABLE task ADD bid_quantity float;
        ''')


    def upgrade_v3_9_0_b07_001(self):
        self.run_sql('''  
            UPDATE "work_hour" set category='regular' where category is NULL;
        ''')




    #
    # 3.8.0.v05
    #
    def upgrade_v3_8_0_v05_021(self):
        self.run_sql('''  
            UPDATE "work_hour" set category='regular' where category is NULL;
        ''')

    def upgrade_v3_8_0_v05_020(self):
        self.run_sql('''  
            CREATE INDEX "note_search_type_search_id_idx" on note (search_type, search_id);
        ''')

    def upgrade_v3_8_0_v05_019(self):
        self.run_sql('''  
            CREATE INDEX "snapshot_search_type_search_id_idx" on snapshot (search_type, search_id);
        ''')

    def upgrade_v3_8_0_v05_018(self):
        self.run_sql('''  
            CREATE INDEX "sobject_list_search_type_search_id_idx" on sobject_list (search_type, search_id);
        ''')

    def upgrade_v3_8_0_v05_017(self):
        self.run_sql('''  
            CREATE INDEX "status_log_search_type_search_id_idx" on status_log (search_type, search_id);
        ''')

    def upgrade_v3_8_0_v05_016(self):
        self.run_sql('''  
            CREATE INDEX "task_search_type_search_id_idx" on task (search_type, search_id);
        ''')

    def upgrade_v3_8_0_v05_015(self):
        self.run_sql('''  
            ALTER TABLE sobject_list add constraint "sobject_list_code_idx" UNIQUE (code);
        ''')


    def upgrade_v3_8_0_v05_013(self):
        self.run_sql('''
        CREATE TABLE special_day (
    id serial PRIMARY KEY,
    code character varying(256),
    week integer,
    mon float, 
    tue float, 
    wed float, 
    thu float, 
    fri float, 
    sat float, 
    sun float, 
    year integer, 
    login character varying(256),
    description character varying(256),
    "type" character varying(256),
    project_code character varying(256)
);
    ''')

    def upgrade_v3_8_0_v05_012(self):
        self.run_sql('''
        ALTER TABLE search_object add constraint search_object_search_type_idx UNIQUE(search_type);
        ''')

    def upgrade_v3_8_0_v05_011(self):
        self.run_sql('''
    CREATE TABLE repo (
    id serial PRIMARY KEY,
    code character varying(256) NOT NULL,
    description character varying(256) NOT NULL,
    handler character varying(100) NOT NULL,
    web_dir character varying(256) NOT NULL,
    lib_dir character varying(256) NOT NULL
);
    ''')

    def upgrade_v3_8_0_v05_010(self):
        self.run_sql(''' 
    CREATE TABLE queue (
    id serial PRIMARY KEY,
    code character varying(256),
    queue character varying(30) NOT NULL,
    priority character varying(10) NOT NULL,
    description character varying(256),
    state character varying(30) NOT NULL DEFAULT 'pending',
    login character varying(30) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    command character varying(200) NOT NULL,
    serialized character varying(256) NOT NULL,
    s_status character varying(30),
    project_code character varying(100),
    search_id integer,
    search_type character varying(100),
    dispatcher_id integer,
    policy_code character varying(30),
    host character varying(256)
);
    ''')

    def upgrade_v3_8_0_v05_009(self):
        self.run_sql(''' 
    CREATE TABLE pref_list (
    id serial PRIMARY KEY,
    code character varying(256),
    "key" character varying(256),
    description character varying(256),
    options character varying(256),
    "type" character varying(256),
    category character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    title character varying(256),
    CONSTRAINT "pref_list_key_idx" UNIQUE ("key")
);
    ''')

    def upgrade_v3_8_0_v05_008(self):
        self.run_sql(''' 
    CREATE TABLE file_access (
    id serial PRIMARY KEY,
    code character varying(256),
    file_code integer NOT NULL,
    login character varying(100),
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);
    ''')

    def upgrade_v3_8_0_v05_007(self):
        self.run_sql('''
    CREATE TABLE custom_property (
    id serial PRIMARY KEY,
    code character varying(256),
    search_type character varying(256),
    name character varying(256),
    description character varying(256),
    login character varying(256)
);
    ''')
    def upgrade_v3_8_0_v05_006(self):
        self.run_sql('''
        CREATE TABLE connection (
    id serial PRIMARY KEY,
    code character varying(256),
    context character varying(60),
    project_code character varying(30),
    src_search_type character varying(200),
    src_search_id integer,
    dst_search_type character varying(200),
    dst_search_id integer,
    login character varying(30),
    "timestamp" timestamp without time zone DEFAULT now()
);
    ''')

    def upgrade_v3_8_0_v05_005(self):
        self.run_sql('''
    CREATE TABLE snapshot_type (
    id serial PRIMARY KEY,
    code character varying(256),
    pipeline_code character varying(256),
    "timestamp" timestamp without time zone DEFAULT now(),
    login character varying(256),
    s_status character varying(256),
    relpath character varying(256),
    project_code character varying(256),
    subcontext character varying(256),
    snapshot_flavor character varying(256),
    relfile character varying(256),
    CONSTRAINT "snapshot_type_code_unique" UNIQUE (code)
);
    ''')

    def upgrade_v3_8_0_v05_004(self):
        self.run_sql('''
        CREATE TABLE retire_log (
            id serial PRIMARY KEY,
            code character varying(256),
            search_type character varying(100),
            search_id character varying(100),
            login character varying(100) NOT NULL,
            "timestamp" timestamp without time zone DEFAULT now(),
            CONSTRAINT "retire_log_code_idx" UNIQUE (code)

    );
    ''')

    def upgrade_v3_8_0_v05_003(self):
        self.run_sql('''
        CREATE TABLE db_resource (
    id serial PRIMARY KEY,
    code character varying(256),
    host text,
    port integer,
    vendor character varying(256),
    login character varying(256),
    password text,
    CONSTRAINT "db_resource_code_idx" UNIQUE (code)
);
    ''')

    def upgrade_v3_8_0_v05_002(self):
        self.run_sql('''
    CREATE TABLE access_log (
    id serial PRIMARY KEY,
    code character varying(256),
    url character varying(256),
    data character varying(256),
    "start_time" timestamp without time zone,
    "end_time" timestamp without time zone,
    duration double precision,
    CONSTRAINT "access_log_code_idx" UNIQUE (code)
);
    ''')

    def upgrade_v3_8_0_v05_001(self):
        self.run_sql('''
    CREATE TABLE command_log (
    id serial PRIMARY KEY,
    code character varying(256),
    class_name character varying(100) NOT NULL,
    paramaters character varying(256),
    login character varying(100) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT "command_log_code_idx" UNIQUE (code)
);
        ''')    
    
    #
    # 3.8.0.v04
    #
    def upgrade_v3_8_0_v04_001(self):
        self.run_sql('''
        ALTER TABLE login_in_group ADD "code" varchar(256);
        ''')

    
    #
    # 3.8.0.rc04
    #
    def upgrade_v3_8_0_rc04_001(self):
        self.run_sql('''
INSERT INTO "search_object" ("code", "search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('prod/session_contents','prod/session_contents', 'prod', 'Introspection Contents of a users session', '{project}', 'session_contents', 'pyasm.prod.biz.SessionContents', 'Session Contents', 'public')
        ''')



    def upgrade_v3_8_0_rc03_004(self):
        self.run_sql('''
INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('prod/session_contents', 'prod', 'Introspection Contents of a users session', '{project}', 'session_contents', 'pyasm.prod.biz.SessionContents', 'Session Contents', 'public')
        ''')

    def upgrade_v3_8_0_rc03_003(self):
        self.run_sql('''
        ALTER TABLE work_hour ADD "task_code" varchar(256);
        ''')




    def upgrade_v3_8_0_rc03_002(self):
        self.run_sql('''
        ALTER TABLE work_hour ADD "process" varchar(256);
        ''')
    

    def upgrade_v3_8_0_rc03_001(self):
        self.run_sql('''
        ALTER TABLE work_hour ADD "task_code" varchar(256);
        ''')

    def upgrade_v3_8_0_rc01_001(self):
        self.run_sql('''
        ALTER TABLE "file" ADD "base_dir_alias" varchar(256);
        ''')
 
    #
    # 3.8.0.b06
    #
    def upgrade_v3_8_0_b06_003(self):
        self.run_sql('''
        DELETE FROM search_object where search_type in ('flash/pickup_request','flash/series');
        ''') 

   
    def upgrade_v3_8_0_b06_002(self):
        self.run_sql('''
        DELETE FROM search_object where search_type in ('flash/episode_instance','flash/asset','flash/design_pack','flash/funpack','flash/shot_instance','flash/shot','flash/layer','flash/script','flash/storyboard','flash/leica','flash/nat_pause','prod/series');
        ''') 


    def upgrade_v3_8_0_b06_001(self):
        self.run_sql('''
        DELETE FROM project_type where code = 'flash';
        ''') 
   

    #
    # 3.8.0.b08
    #
    def upgrade_v3_8_0_b08_006(self):
        self.run_sql('''
        DELETE from search_object where search_type='prod/prod_setting';
        ''')

    def upgrade_v3_8_0_b08_005(self):
        self.run_sql('''
        UPDATE "pipeline" SET code='task(DEPRECATED)' where code = 'task';
        ''')

    def upgrade_v3_8_0_b08_004(self):
        self.run_sql('''
        UPDATE "login_group" SET code ="login_group";
        ''')
    def upgrade_v3_8_0_b08_003(self):
        self.run_sql('''
        ALTER TABLE login_group add constraint login_group_code_unique UNIQUE(code);
        ''')

    def upgrade_v3_8_0_b08_002(self):
        self.run_sql('''
        UPDATE "login_group" SET code ="login_group";
        ''')

    def upgrade_v3_8_0_b08_001(self):
        self.run_sql('''
        ALTER TABLE login_group ADD COLUMN code varchar(256);
        ''')


    #
    # 3.8.0.b07
    #
    def upgrade_v3_8_0_b07_001(self):
        self.run_sql('''
        alter table task drop constraint "pipeline_code_foreign";
        ''')
    #
    # 3.8.0.b06
    #
    def upgrade_v3_8_0_b06_003(self):
        self.run_sql('''
        DELETE FROM search_object where search_type in ('flash/pickup_request','flash/series');
        ''') 

    def upgrade_v3_8_0_b06_002(self):
        self.run_sql('''
        DELETE FROM search_object where search_type in ('flash/episode_instance','flash/asset','flash/design_pack','flash/funpack','flash/shot_instance','flash/shot','flash/layer','flash/script','flash/storyboard','flash/leica','flash/nat_pause','prod/series');
        ''') 


    def upgrade_v3_8_0_b06_001(self):
        self.run_sql('''
        DELETE FROM project_type where code = 'flash';
        ''') 


    #
    # 3.8.0.b05
    #
    def upgrade_v3_8_0_b05_001(self):
        self.run_sql('''
        ALTER TABLE "file" ADD COLUMN repo_type varchar(256);
        ''') 

   
    #
    # 3.8.0.b04
    #
    def upgrade_v3_8_0_b04_002(self):
        self.run_sql('''
        ALTER TABLE login_group ADD COLUMN access_level varchar(32);
        ''') 

    
    def upgrade_v3_8_0_b04_001(self):
        self.run_sql('''
        ALTER TABLE sobject_list ADD COLUMN code varchar(256);
        ''') 


    #
    # 3.8.0.b03
    #



    def upgrade_v3_8_0_b03_001(self):
        self.run_sql('''
        UPDATE search_object set title='Tasks', description='Tasks' where search_type='sthpw/task';
        ''') 


    #
    # 3.8.0.b02
    #

    def upgrade_v3_8_0_b02_005(self):
        self.run_sql('''
        ALTER TABLE "file" ADD COLUMN metadata_search text;
        ''') 


    def upgrade_v3_8_0_b02_004(self):
        self.run_sql('''
        ALTER TABLE "file" ADD COLUMN metadata text;
        ''') 


    def upgrade_v3_8_0_b02_003(self):
        self.run_sql('''
        ALTER TABLE login ADD COLUMN hourly_wage float;
        ''') 



    def upgrade_v3_8_0_b02_002(self):
        self.run_sql('''
        ALTER TABLE login_group ADD COLUMN start_link text;
        ''') 

 

    def upgrade_v3_8_0_b02_001(self):
        self.run_sql('''
        CREATE INDEX "sobject_list_search_type_search_id_idx" on sobject_list (search_type, search_id);
        ''') 


    #
    # 3.8.0.a01
    #
    def upgrade_v3_8_0_a01_005(self):
        self.run_sql('''
        ALTER TABLE trigger add column "process" varchar(256);
        ''')

    def upgrade_v3_8_0_a01_004(self):
		# The pipeline table wass added in 3.1, the search_type was character varying(100)
        self.run_sql('''ALTER TABLE pipeline ALTER COLUMN search_type TYPE varchar(256);''')
 

    def upgrade_v3_8_0_a01_003(self):
        self.run_sql('''INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/db_resource', 'sthpw', 'Database Resource', 'sthpw', 'db_resource', 'pyasm.search.SObject', 'Database Resource', 'public');
        ''')

    def upgrade_v3_8_0_a01_002(self):
        self.run_sql('''
        CREATE TABLE db_resource (
            id serial PRIMARY KEY,
            code varchar(256),
            host text,
            port integer,
            vendor varchar(256),
            login varchar(256),
            password text
        );
        ''')

    def upgrade_v3_8_0_a01_001(self):
        self.run_sql('''ALTER TABLE "project" ADD COLUMN "db_resource" text;''')

    #
    # 3.7.0.v04
    #


    def upgrade_v3_7_0_v04_002(self):
        self.run_sql('''ALTER TABLE project ALTER column "type" type varchar(256);''')

    def upgrade_v3_7_0_v04_001(self):
        self.run_sql('''ALTER TABLE project_type ALTER column code type varchar(256);''')

    #
    # 3.7.0.v03
    #


    def upgrade_v3_7_0_v03_001(self):
        self.run_sql('''INSERT INTO search_object (search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/search_type', 'sthpw', 'List of all the search objects', 'sthpw', 'search_object', 'pyasm.search.SearchType', 'Search Objects', 'public');
        ''')

    def upgrade_v3_7_0_v01_006(self):
        self.run_sql('''ALTER TABLE work_hour ADD column process varchar(256);''')

    def upgrade_v3_7_0_v01_005(self):
        self.run_sql('''
        ALTER TABLE work_hour add constraint work_hour_code_unique UNIQUE(code);
        ''')

    def upgrade_v3_7_0_v01_004(self):
        self.run_sql('''
        ALTER TABLE note add constraint note_code_unique UNIQUE(code);
        ''')

    def upgrade_v3_7_0_v01_003(self):
        self.run_sql('''
        ALTER TABLE note ADD COLUMN "code" varchar(256);
        ''')


    def critical_v3_7_0_v01_002(self):
        self.run_sql('''
        ALTER TABLE task add constraint task_code_unique UNIQUE(code);
        ''')


    def upgrade_v3_7_0_v01_001(self):

        # update the task code based on its id
        from pyasm.search import Search, SObject
        search = Search('sthpw/task')
        search.add_column('code')
        search.add_group_by('code')

        search.add_having('count(code) > 1')
        search.select.order_bys = []
        sobjects = search.get_sobjects()
        
        duplicated_codes = SObject.get_values(sobjects, 'code')

        search = Search('sthpw/task')
        search.add_filters('code', duplicated_codes)
        sobjects = search.get_sobjects()

        padding = 8
        prefix = 'TASK'

        change_dict = {}

        for sobject in sobjects:
            id = sobject.get_id()
            code_expr = "%%s%%0.%dd" % padding
            new_code = code_expr % (prefix, id)
            old_code = sobject.get_code()
            change_dict[old_code] = new_code
            print "Updating task id [%s] with new code [%s]"%(id ,new_code)
            sobject.set_value("code", new_code )
            sobject.commit(triggers=False)
        
        for key, value in change_dict.items():
            search = Search('sthpw/work_hour')
            search.add_filter('task_code', key)
            work_hours = search.get_sobjects()
            for work_hour in work_hours:
                id = work_hour.get_id()
                print "Updating work_hour id [%s] with new task_code [%s]"%(id , value)
                work_hour.set_value('task_code', value)
                work_hour.commit(triggers=False)

        


    #
    # 3.7.0.rc04
    #
    def upgrade_v3_7_0_rc04_003(self):
        self.run_sql('''
        ALTER TABLE "pipeline" ADD COLUMN "autocreate_tasks" boolean
        ''')


    def upgrade_v3_7_0_rc04_002(self):
        self.run_sql('''
        INSERT INTO pref_list ("key",description,options,"type",category,title) VALUES ('sandbox_base_dir','Determines the base sandbox folder for this project.  This can be customized for each project','','text','check-in','Sandbox Base Folder');
        ''')
 




    def upgrade_v3_7_0_rc04_001(self):
        self.run_sql('''
        UPDATE pref_list set options = 'en_US' where key = 'language';
        ''')
 

  
    #
    # 3.7.0.rc03
    #
    def upgrade_v3_7_0_rc03_001(self):
        # remove the {public}. schema in table_name
        from pyasm.search import Search
        search = Search('sthpw/search_object')
        sobjects = search.get_sobjects()
        for i, sobj in enumerate(sobjects):
            table_name = sobj.get_value('table_name')
            if table_name.find('{public}.') != -1:
                table_name = table_name.replace('{public}.', '')
                sobj.set_value('table_name', table_name)
                sobj.commit()

    #
    # 3.7.0.rc01
    #
    def upgrade_v3_7_0_rc01_002(self):
        self.run_sql('''UPDATE "search_object" SET code = search_type''');

  
    def upgrade_v3_7_0_rc01_001(self):
        self.run_sql('''ALTER TABLE "search_object" ADD COLUMN "code" varchar(256);''')


    #
    # 3.7.0.a01
    #
    def upgrade_v3_7_0_a01_002(self):
        self.run_sql('''INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/doc', 'sthpw', 'Documentation', 'sthpw', 'doc', 'pyasm.search.SObject', 'Documentation', 'public');
        ''')




    def upgrade_v3_7_0_a01_001(self):
        self.run_sql('''
        CREATE TABLE doc (
            id serial PRIMARY KEY,
            code varchar(256),
            alias varchar(1024),
            rel_path text
        );
        ''')



    #
    # 3.6.0.rc01
    #
    def upgrade_v3_6_0_v03_001(self):
        from pyasm.security import AccessRuleBuilder
        from pyasm.search import Search
        rule_group = "side_bar"

        # get all of the groups
        search = Search("sthpw/login_group")
        login_groups = search.get_sobjects()

        # add project = "*" if the attr does not exist as an upgrade
        for login_group in login_groups:

            code = login_group.get_value("login_group")
            access_rules = login_group.get_xml_value("access_rules")

            # add the rule to each group
            builder = AccessRuleBuilder(access_rules)

            xpath = "rules/rule[@group='%s' and not(@project) and not(@default)]" %rule_group
            update_dict ={'project': '*'}
            builder.update_rule(xpath, update_dict)

            login_group.set_value("access_rules", builder.to_string())
            login_group.commit(triggers=False)


    def upgrade_v3_6_0_rc03_001(self):
        self.run_sql('''ALTER TABLE login_group ADD COlUMN code varchar(256)''')

    def upgrade_v3_6_0_rc02_001(self):
        self.run_sql('''ALTER TABLE wdg_settings alter column login TYPE varchar(100);''')


    #
    # 3.6.0.b02
    #
    def upgrade_v3_6_0_b02_003(self):
        self.run_sql('''CREATE unique index "login_code_idx" ON "login" ("code");''')

    def upgrade_v3_6_0_b02_002(self):
        self.run_sql('''   UPDATE "login" set code = login where code is NULL;''')

    def upgrade_v3_6_0_b02_001(self):
        self.run_sql('''ALTER TABLE login add column code varchar(512);''')


    #
    # 3.6.0.b01
    #
    def upgrade_v3_6_0_b01_016(self):
        self.run_sql('''UPDATE search_object set class_name = 'pyasm.biz.Milestone' where search_type = 'sthpw/milestone';''')


    def upgrade_v3_6_0_b01_015(self):
        self.run_sql('''
        ALTER TABLE search_object ADD COLUMN color varchar(32);
        ''')

    def upgrade_v3_6_0_b01_014(self):
        self.run_sql('''ALTER TABLE ticket ADD column category varchar(256);''')


    def upgrade_v3_6_0_b01_013(self):
        self.run_sql('''ALTER TABLE work_hour ADD column status varchar(256);''')

    def upgrade_v3_6_0_b01_012(self):
        self.run_sql('''ALTER TABLE task ALTER column pipeline_code TYPE varchar(256);''')

    def upgrade_v3_6_0_b01_011(self):
        self.run_sql('''
        UPDATE search_object SET title = 'Preference List' WHERE search_type = 'sthpw/pref_list';
        ''')


    def upgrade_v3_6_0_b01_010(self):
        self.run_sql('''
        UPDATE search_object SET title = 'Notification Log' WHERE search_type = 'sthpw/notification_log';
        ''')


    def upgrade_v3_6_0_b01_009(self):
        self.run_sql('''
        UPDATE search_object SET title = 'Files' WHERE search_type = 'sthpw/file';
        ''')


    def upgrade_v3_6_0_b01_008(self):
        self.run_sql('''
        UPDATE search_object SET title = 'Access Rules' WHERE search_type = 'sthpw/access_rule';
        ''')



    def upgrade_v3_6_0_b01_007(self):
        self.run_sql('''
        UPDATE search_object SET title = 'SObject Cache' WHERE search_type = 'sthpw/cache';
        ''')


    def upgrade_v3_6_0_b01_006(self):
        self.run_sql('''DELETE FROM pref_list where key = 'skin';''')

    def upgrade_v3_6_0_b01_005(self):
        self.run_sql('''DELETE FROM pref_setting where key = 'skin';''')



    def upgrade_v3_6_0_b01_004(self):
        self.run_sql('''
        INSERT INTO pref_list ("key",description,options,"type",category,title) VALUES ('palette','Color Palette to determine the look and feel','Aqua|Dark|Silver|Bright|Origami|Bon Noche|Aviator','sequence','display','Color Palette');
        ''')


    def upgrade_v3_6_0_b01_003(self):
        self.run_sql('''UPDATE pref_list SET category = 'debug' where key = 'js_logging_level';''')

    def upgrade_v3_6_0_b01_002(self):
        self.run_sql('''UPDATE pref_list SET category = 'debug' where key = 'debug';''')




    def upgrade_v3_6_0_b01_001(self):
        self.run_sql('''ALTER TABLE "project" ADD COLUMN "palette" varchar(256)''')


    #
    # 3.6.0.a02
    #
    def upgrade_v3_6_0_a02_001(self):
        self.run_sql('''ALTER TABLE work_hour ADD COLUMN "task_code" varchar(256)''')


    #
    # 3.6.0.a01
    #
    def upgrade_v3_6_0_a01_007(self):
        self.run_sql('''ALTER TABLE "project" ADD COLUMN "category" varchar(256)''')

    def upgrade_v3_6_0_a01_006(self):
        self.run_sql('''ALTER TABLE "project" ADD COLUMN "is_template" boolean''')


    def upgrade_v3_6_0_a01_005(self):
        self.run_sql('''INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/sobject_list', 'sthpw', 'SObject List', 'sthpw', 'sobject_list', 'pyasm.search.SObject', 'SObject List', 'public');
        ''')



    def upgrade_v3_6_0_a01_004(self):
        self.run_sql('''
        CREATE TABLE sobject_list (
            id serial PRIMARY KEY,
            search_type varchar(256),
            search_id integer,
            keywords text,
            "timestamp" timestamp default now(),
            project_code varchar(256)
        );
        ''')



    def upgrade_v3_6_0_a01_003(self):
        self.run_sql('''INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/ingest_session', 'config', 'Ingest Sessions', '{project}', 'spt_ingest_session', 'pyasm.search.SObject', 'Ingest Sessions', 'public');
        ''')
    


    def upgrade_v3_6_0_a01_002(self):
        self.run_sql('''INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/plugin', 'sthpw', 'Plugins', 'sthpw', 'spt_plugin', 'pyasm.search.SObject', 'Plugins', 'public');
        ''')



    def upgrade_v3_6_0_a01_001(self):
        self.run_sql('''INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/ingest_rule', 'config', 'Ingest Rules', '{project}', 'spt_ingest_rule', 'pyasm.search.SObject', 'Ingest Rules', 'public');
        ''')

    #
    # 3.5.0.rc03
    #

    def upgrade_v3_5_0_v01_004(self):
        self.run_sql('''
        alter table task drop constraint "pipeline_code_foreign";
        ''')


    def upgrade_v3_5_0_v01_003(self):
        self.run_sql('''
        CREATE INDEX "notification_log_timestamp_idx" on notification_log (timestamp);
        ''')


    #
    # 3.5.0.rc03
    #
    def upgrade_v3_5_0_v01_003(self):
        self.run_sql('''
        CREATE INDEX "notification_log_timestamp_idx" on notification_log (timestamp);
        ''')

    def upgrade_v3_5_0_v01_002(self):
        if self.get_database_type() == 'MySQL':
            self.run_sql('''
            ALTER table snapshot modify lock_login varchar(100) NULL;
            ''')
        elif self.get_database_type() == 'SQLServer':
            self.run_sql('''
            ALTER table snapshot alter column lock_login varchar(100) NULL;
            ''')
        else:
            self.run_sql('''
            ALTER table snapshot alter column lock_login DROP NOT NULL;
            ''')

    def upgrade_v3_5_0_v01_001(self):
        self.run_sql('''
        UPDATE search_object set class_name='pyasm.search.SObject' where search_type='prod/plate';
        ''')

    def upgrade_v3_5_0_rc03_004(self):
        self.run_sql('''
        UPDATE search_object set class_name='pyasm.biz.WorkHour' where search_type='sthpw/work_hour';
        ''')

    def upgrade_v3_5_0_rc03_003(self):
        self.run_sql('''
        ALTER TABLE pref_setting drop constraint pref_setting_login_fkey CASCADE;
        ''')


    def upgrade_v3_5_0_rc03_002(self):
        self.run_sql('''
        ALTER TABLE wdg_settings drop constraint wdg_settings_project_code_fkey CASCADE;
        ''')

    def upgrade_v3_5_0_rc03_001(self):
        self.run_sql('''
        ALTER TABLE wdg_settings drop constraint wdg_settings_login_fkey CASCADE;
        ''')
 

    #
    # 3.5.0.rc01
    #

    def upgrade_v3_5_0_rc01_001(self):
        self.run_sql('''
        UPDATE "note" set process = context where process is NULL;
        ''')



    def upgrade_v3_1_0_rc01_001(self):
        self.run_sql('''
        ALTER TABLE "notification" ADD COLUMN "data" text;
        ''')


    #
    # 3.1.0.b09
    #
    def upgrade_v3_1_0_b09_001(self):
        self.run_sql('''
        ALTER TABLE "notification" ADD COLUMN "listen_event" VARCHAR(256);
        ''')


    #
    # 3.1.0.b06
    #
    def upgrade_v3_1_0_b06_002(self):
        self.run_sql('''
        ALTER TABLE "wdg_settings" DROP constraint "wdg_settings_project_code_fkey";
        ''')

    def upgrade_v3_1_0_b06_001(self):
        self.run_sql('''
        ALTER TABLE "wdg_settings" DROP constraint "wdg_settings_login_fkey";
        ''')


    def upgrade_v3_1_0_b03_001(self):
        self.run_sql('''
        CREATE INDEX "status_log_search_type_search_id_idx" on status_log (search_type, search_id)
        ''') 

    #
    # 3.1.0.b01
    #
    def upgrade_v3_1_0_b01_001(self):
        self.run_sql('''
        ALTER TABLE search_object ADD COLUMN color varchar(256);
        ''')



    #
    # 3.1.0.a02
    #
    def upgrade_v3_1_0_a02_007(self):
        self.run_sql('''INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/pipeline', 'config', 'Pipeline', '{project}', 'spt_pipeline', 'pyasm.biz.Pipeline', 'Pipeline', 'public');
        ''')


    def upgrade_v3_1_0_a02_006(self):
        self.run_sql('''
        ALTER TABLE notification ADD COLUMN process varchar(256);
        ''')


    def upgrade_v3_1_0_a02_005(self):
        self.run_sql('''
        ALTER TABLE notification ADD COLUMN title varchar(256);
        ''')


    def upgrade_v3_1_0_a02_004(self):
        self.run_sql('''
        ALTER TABLE snapshot ADD COLUMN process varchar(256);
        ''')




    def upgrade_v3_1_0_a02_003(self):
        self.run_sql('''
        ALTER TABLE pipeline ADD COLUMN color varchar(32);
        ''')


    def upgrade_v3_1_0_a02_002(self):
        self.run_sql('''
        ALTER TABLE snapshot ADD COLUMN lock_date timestamp;
        ''')

    def upgrade_v3_1_0_a02_001(self):
        self.run_sql('''
        ALTER TABLE snapshot ADD COLUMN lock_login varchar(256);
        ''')




    #
    # 3.1.0.a01
    #
    def upgrade_v3_1_0_a01_001(self):
        self.run_sql('''
        ALTER TABLE queue ADD COLUMN host varchar(256);
        ''')



    #
    # 3.0.0.rc03
    #
    def upgrade_v3_0_0_rc03_002(self):
        self.run_sql('''
        CREATE INDEX "note_search_type_search_id_idx" on note (search_type, search_id)
        ''') 

    def upgrade_v3_0_0_rc03_001(self):
        self.run_sql('''
        ALTER TABLE trigger ALTER COLUMN event TYPE varchar(256);
        ''')

   
    #
    # 3.0.0.b01
    #
    # Commenting out for now
    #def upgrade_v3_0_0_b01_005(self):
    #    self.run_sql('''
    #    INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/bid', 'config', 'Bidding', '{project}', 'spt_bid', 'pyasm.search.SObject', 'Bidding', 'public');
    #    ''')



    def upgrade_v3_0_0_b01_004(self):
        self.run_sql('''
        INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('sthpw/work_hour', 'sthpw', 'Work Hours', 'sthpw', 'work_hour', 'pyasm.search.SObject', 'Work Hours', 'public');
        ''')



    def upgrade_v3_0_0_b01_003(self):
        self.run_sql('''
        CREATE TABLE work_hour (
            id serial PRIMARY KEY,
            code varchar(256),
            project_code varchar(256),
            description text,
            category varchar(256),
            login varchar(256),
            day timestamp,
            start_time timestamp,
            end_time timestamp,
            straight_time float,
            over_time float,
            search_type varchar(256),
            search_id int4
        );
        ''')


 
    def upgrade_v3_0_0_b01_002(self):
        self.run_sql('''
        INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/process', 'config', 'Processes', '{project}', 'spt_process', 'pyasm.search.SObject', 'Processes', 'public')
        ''')



    def upgrade_v3_0_0_b01_001(self):
        self.run_sql('''
        INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/trigger', 'config', 'Triggers', '{project}', 'spt_trigger', 'pyasm.biz.TriggerSObj', 'Triggers', 'public')
        ''')


    #
    # 2.7.0.a02
    #
    def upgrade_v2_7_0_a01_002(self):
        self.run_sql('''
        CREATE INDEX "snapshot_search_type_search_id_idx" on snapshot (search_type, search_id)
        ''')


    #
    # 2.7.0.a01
    #
    def upgrade_v2_7_0_a01_001(self):
        self.run_sql('''
        INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/plugin', 'config', 'Plugin', '{project}', 'spt_plugin', 'pyasm.search.SObject', 'Plugin', 'public'); 
        ''')

    def upgrade_v2_6_0_v01_002(self):
        self.run_sql('''
        CREATE INDEX "task_search_type_search_id_idx" on task (search_type, search_id);
        ''')


    def upgrade_v2_6_0_v01_001(self):
        self.run_sql('''
        CREATE INDEX "snapshot_search_type_search_id_idx" on snapshot (search_type, search_id);
        ''')

    #
    # 2.6.0.rc01
    #
    def upgrade_v2_6_0_rc01_002(self):
        self.run_sql('''
        INSERT INTO pref_list ("key",description,options,"type",category,title) VALUES ('quick_text','Quick text for Note Sheet','','string','general','Quick Text');
        ''')


    def upgrade_v2_6_0_rc01_001(self):
        self.run_sql('''
        ALTER TABLE trigger ADD COLUMN mode varchar(256);
        ''')

    #
    # 2.6.0.b05
    #
    def upgrade_v2_6_0_b05_002(self):
        self.run_sql('''
        ALTER TABLE trigger ALTER COLUMN class_name DROP NOT NULL;
        ''')



    def upgrade_v2_6_0_b05_001(self):
        self.run_sql('''
        ALTER TABLE trigger ADD COLUMN script_path varchar(256);
        ''')




    #
    # 2.6.0.b03
    #
    def upgrade_v2_6_0_b03_002(self):
        self.run_sql('''
        UPDATE snapshot set is_synced = 't' where is_synced is NULL;
        ''')


    def upgrade_v2_6_0_b03_001(self):
        self.run_sql('''
        ALTER TABLE snapshot ADD COLUMN is_synced boolean;
        ''')


    #
    # 2.6.0.b02
    #
    def upgrade_v2_6_0_b02_001(self):
        self.run_sql('''update snapshot set revision=0 where revision is NULL''');

    #
    # 2.6.0.b01
    #
    def upgrade_v2_6_0_b01_002(self):
        self.run_sql('''
        INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/client_trigger', 'config', 'Client Trigger', '{project}', 'spt_client_trigger', 'pyasm.search.SObject', 'Client Trigger', 'public'); 
        ''')

    def upgrade_v2_6_0_b01_001(self):
        self.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/prod_setting', 'config', 'Production Settings', '{project}', 'prod_setting', 'pyasm.prod.biz.ProdSetting', 'Production Settings', 'public');
        ''')

        
    #
    # 2.6.0.a01 again
    #

    def upgrade_v2_6_0_a01_001(self):
        self.run_sql('''
        INSERT INTO "search_object" ("search_type", "namespace", "description", "database", "table_name", "class_name", "title", "schema") VALUES ('config/url', 'config', 'Custom URL', '{project}', 'spt_url', 'pyasm.search.SObject', 'Custom URL', 'public');
        '''
        )
    def upgrade_v2_5_0_v02_002(self):
        self.run_sql('''
        ALTER TABLE pipeline DROP CONSTRAINT project_code_foreign;
        ''')



    def upgrade_v2_5_0_v01_001(self):
        self.run_sql('''
        DELETE from pref_setting where key='use_java_maya';
        '''
        )

    def upgrade_v2_5_0_v01_002(self):
        self.run_sql('''
        DELETE from pref_list where key='use_java_maya';
        '''
        )

    def upgrade_v2_5_0_v01_003(self):
        self.run_sql('''
        ALTER table widget_config add column category varchar(256);
        '''
        )
    #
    # 2.5.0.rc20
    #
    def upgrade_v2_5_0_rc20_001(self):
        self.run_sql('''
        alter table task add column completion float;
        ''')

    def upgrade_v2_5_0_rc20_002(self):
        self.run_sql('''
        alter table task add column context varchar(256);
        ''')

    def upgrade_v2_5_0_rc20_003(self):
        self.run_sql('''
        CREATE TABLE cache (
            id serial PRIMARY KEY,
            key varchar(256),
            mtime timestamp
        );
        ''')

    def upgrade_v2_5_0_rc20_004(self):
        self.run_sql('''
        ALTER TABLE "notification" ADD COLUMN "mail_to" text;
        ''')

    def upgrade_v2_5_0_rc20_005(self):
        self.run_sql('''
        ALTER TABLE trigger drop constraint trigger_class_name_event_unique CASCADE;
        ''')

    def upgrade_v2_5_0_rc20_006(self):
        self.run_sql('''
        ALTER TABLE "notification" ADD COLUMN "mail_cc" text;
        ''')


    def upgrade_v2_5_0_rc20_007(self):
        self.run_sql('''
        ALTER TABLE "notification" ADD COLUMN "mail_bcc" text;
        ''')




    def upgrade_v2_5_0_rc20_008(self):
        self.run_sql('''
        ALTER TABLE trigger add constraint trigger_class_name_event_project_unique UNIQUE(class_name, event, project_code);
        ''')

    #
    # 2.5.0.rc19
    #
 
    def upgrade_v2_5_0_rc19_001(self):
        self.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/cache', 'sthpw', 'Cache', 'sthpw', '{public}.cache', 'pyasm.search.SObject', '', 'public');        
        ''')

    def upgrade_v2_5_0_rc19_002(self):
        self.run_sql('''
        ALTER TABLE trigger drop constraint trigger_class_name_event_unique CASCADE;
        ''')


    def upgrade_v2_5_0_rc19_003(self):
        self.run_sql('''
        ALTER TABLE trigger add constraint trigger_class_name_event_project_unique UNIQUE(class_name, event, project_code);
        ''')

    #
    # 2.5.0.rc18
    #
    def upgrade_v2_5_0_rc18_001(self):
        if self.get_database_type() == 'MySQL':
            self.run_sql('''ALTER TABLE file MODIFY file_name varchar(512) NULL;''')
        else:
            self.run_sql('''
            ALTER TABLE "file" alter column file_name drop NOT NULL; 
            ''')
    def upgrade_v2_5_0_rc18_002(self):
        self.run_sql('''
        ALTER TABLE "file" add column base_type varchar(256); 
        ''')
    #
    # 2.5.0.rc16
    #
    def upgrade_v2_5_0_rc16_004(self):
        self.run_sql('''
        ALTER TABLE "file" add column type varchar(256);
        ''')

    def upgrade_v2_5_0_rc16_003(self):
        self.run_sql('''
        ALTER TABLE login add column license_type varchar(256);
        ''')


    def upgrade_v2_5_0_rc16_002(self):
        self.run_sql('''
        ALTER TABLE notification add column subject text;
        ''')

    def upgrade_v2_5_0_rc16_001(self):
        self.run_sql('''
        ALTER TABLE notification alter column code DROP NOT NULL;
        ''')

    #
    # 2.5.0.rc12_001
    #
    def upgrade_v2_5_0_rc12_001(self):
        self.run_sql('''
        ALTER TABLE notification add COLUMN event varchar(256);
        ''')

    def upgrade_v2_5_0_rc09_002(self):
        self.run_sql('''
        CREATE INDEX file_file_name_idx ON file(file_name);
        ''')

    def upgrade_v2_5_0_rc09_001(self):
        self.run_sql('''
        ALTER TABLE login ALTER COLUMN password DROP NOT NULL; 
        ''')

    def upgrade_v2_5_0_rc08_001(self):
        self.run_sql('''
        update search_object set class_name='pyasm.biz.TriggerSObj' where search_type ='sthpw/trigger';
        ''')

    # 2.5.0.rc06
    def upgrade_v2_5_0_rc06_001(self):
        self.run_sql('''
        ALTER TABLE note add column access varchar(256);
        ''')



    # 2.5.0.rc05
    def upgrade_v2_5_0_rc05_002(self):
        self.run_sql('''
        ALTER TABLE login add column "department" varchar(256);
        ''')


    def upgrade_v2_5_0_rc05_001(self):
        self.run_sql('''
        ALTER TABLE login add column "phone_number" varchar(32);
        ''')

  
    # 2.5.0.rc01
    def upgrade_v2_5_0_rc02_002(self):
        self.run_sql('''
        ALTER TABLE note add column "sort_order" integer;
        ''')

    def upgrade_v2_5_0_rc02_001(self):
        self.run_sql('''
        ALTER TABLE trigger add column "s_status" varchar(256);
        ''')

    def upgrade_v2_5_0_rc01_003(self):
        self.run_sql('''
        update pref_list set options = 'true' where key='use_java_maya';
        ''')
   
    def upgrade_v2_5_0_rc01_002(self):
        self.run_sql('''
        delete from pref_list where key='select_filter';
        ''')
    def upgrade_v2_5_0_rc01_001(self):
        self.run_sql('''
        delete from pref_setting where key='select_filter';
        ''')

    def upgrade_v2_5_0_b05_001(self):
        # NOTE: this gives a warning:
        #WARNING:  nonstandard use of \\ in a string literal
        #LINE 1: ...hot set project_code = substring(search_type from '=(\\w+)$'...
        self.run_sql('''
        update snapshot set project_code = substring(search_type from '=(\\w+)$');
        ''')
    # 2.5.0.b03

    def upgrade_v2_5_0_b03_003(self):
        self.run_sql('''
        ALTER TABLE snapshot_type add CONSTRAINT snapshot_type_code_unique UNIQUE (code);
        ''')

    def upgrade_v2_5_0_b03_002(self):
        self.run_sql('''
        ALTER TABLE snapshot_type add CONSTRAINT snapshot_type_pkey primary key (id);
        ''')

    def upgrade_v2_5_0_b03_001(self):
        self.run_sql('''
        ALTER TABLE snapshot_type drop CONSTRAINT snapshot_type_pkey;
        ''')
    # 2.5.0.b02

    def upgrade_v2_5_0_b02_005(self):
        self.run_sql('''
        CREATE INDEX snapshot_search_code_idx on snapshot(search_code);
        ''')


    def upgrade_v2_5_0_b02_004(self):
        self.run_sql('''
        ALTER TABLE snapshot ADD COLUMN search_code varchar(256);
        ''')


    

    def upgrade_v2_5_0_b02_002(self):
        self.run_sql('''
        CREATE INDEX snapshot_project_code_idx on snapshot(project_code);
        ''')


    def upgrade_v2_5_0_b02_001(self):
        self.run_sql('''
        ALTER TABLE snapshot ADD COLUMN project_code varchar(256);
        ''')
    #
    # 2.5.0.a01
    # 
    def upgrade_v2_5_0_a01_005(self):
        self.run_sql('''
        UPDATE search_object SET class_name = 'pyasm.prod.biz.AssetLibrary' where search_type='prod/asset_library';
        ''') 
   
    def upgrade_v2_5_0_a01_004(self):
        self.run_sql('''
        alter table template alter column search_type drop NOT NULL;
        ''')

    def upgrade_v2_5_0_a01_003(self):
        self.run_sql('''
        alter table template alter column code drop NOT NULL;
        ''')


    def upgrade_v2_5_0_a01_002(self):
        self.run_sql('''
        INSERT INTO pref_list ("key",description,options,"type",category,title) VALUES ('js_logging_level','Determines logging level used by Web Client Output Console Pop-up','CRITICAL|ERROR|WARNING|INFO|DEBUG','sequence','general','Web Client Logging Level');
        ''')

    def upgrade_v2_5_0_a01_001(self):
        self.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/custom_script', 'config', 'Custom Script', '{project}', 'custom_script', 'pyasm.search.SObject', 'Custom Script', 'public');
        ''')




    # DEPRECATED
    """



    #
    # 2.4.0.a01
    # 
    def upgrade_v2_4_0_a01_013(self):
        self.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/naming', 'config', 'Naming', '{project}', '{public}.naming', 'pyasm.biz.Naming', '', 'public');
        ''')

    def upgrade_v2_4_0_a01_012(self):
        self.run_sql('''
        CREATE UNIQUE INDEX ticket_id_idx on ticket(id);
        ''')


    def upgrade_v2_4_0_a01_011(self):
        self.run_sql('''
        CREATE UNIQUE INDEX transaction_state_ticket_idx on transaction_state(ticket);
        ''')

    def upgrade_v2_4_0_a01_010(self):
        self.run_sql('''
        ALTER TABLE transaction_state ADD PRIMARY KEY (id);
        ''')




    def upgrade_v2_4_0_a01_009(self):
        self.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/pipeline', 'config', 'Pipelines', '{project}', 'pipeline', 'pyasm.biz.Pipeline', 'Pipelines', 'public');
        ''')


    def upgrade_v2_4_0_a01_008(self):
        self.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('config/widget_config', 'config', 'Widget Config', '{project}', 'widget_config', 'pyasm.search.WidgetDbConfig', 'Widget Config', 'public');
        ''')

    def upgrade_v2_4_0_a01_007(self):
        self.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/custom_script', 'sthpw', 'Custom Script', '{project}', 'custom_script', 'pyasm.search.SObject', 'Custom Script', 'public');
        ''')


    def upgrade_v2_4_0_a01_006(self):
        self.run_sql('''
        CREATE TABLE custom_script (
            id serial PRIMARY KEY,
            code varchar(256),
            script text,
            login varchar(256),
            "timestamp" timestamp,
            s_status varchar(256)
        );
        ''')



    def upgrade_v2_4_0_a01_005(self):
        self.run_sql('''
        alter table widget_config add column code varchar(256);
        ''')


    def upgrade_v2_4_0_a01_004(self):
        self.run_sql('''
        alter table widget_config alter column search_type drop not null;
        ''')

    def upgrade_v2_4_0_a01_003(self):
        self.run_sql('''
        alter table widget_config alter column search_type type varchar(256);
        ''')

    def upgrade_v2_4_0_a01_002(self):
        self.run_sql('''
        alter table widget_config alter column view type varchar(256);
        ''')

    def upgrade_v2_4_0_a01_001(self):
        self.run_sql('''
        alter table widget_config add column project_code varchar(256);
        ''')

    def upgrade_v2_2_0_rc03_002(self):
        self.run_sql('''
        ALTER TABLE trigger add constraint trigger_class_name_event_unique UNIQUE(class_name, event);
        ''')

    def upgrade_v2_2_0_rc03_001(self):
        self.run_sql('''
        ALTER TABLE trigger drop constraint trigger_class_name_key CASCADE;
        ''')

    def upgrade_v2_2_0_rc02_001(self):
        self.run_sql('''
        UPDATE search_object SET class_name = 'pyasm.prod.biz.AssetLibrary' where search_type='prod/asset_library';
        ''')

    #
    # 2.2.0.rc01
    #
    def upgrade_v2_2_0_rc01_001(self):
        self.run_sql('''
        INSERT INTO search_object (search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('prod/snapshot_type', 'prod', 'Snapshot Type', '{project}', 'snapshot_type', 'pyasm.biz.SnapshotType', 'Snapshot Type', 'public');
        ''')

    #
    # 2.2.0.b01
    #
    def upgrade_v2_2_0_b01_005(self):
        self.run_sql('''
        alter table transaction_state add constraint "transaction_state_unique"
        unique(ticket);
        ''')
    
    def upgrade_v2_2_0_b01_004(self):
        self.run_sql('''
        drop index "transaction_state_ticket_idx";
        ''')

    def upgrade_v2_2_0_b01_003(self):
        self.run_sql('''
        alter table ticket add constraint ticket_unique unique (ticket);
        ''')


    #
    # 2.1.0.b08
    #
    def upgrade_v2_1_0_b08_005(self):
        self.run_sql('''
        CREATE INDEX snapshot_search_code_idx on snapshot(search_code);
        ''')


    def upgrade_v2_1_0_b08_004(self):
        self.run_sql('''
        ALTER TABLE snapshot ADD COLUMN search_code varchar(256);
        ''')


    def upgrade_v2_1_0_b08_003(self):
        # NOTE: this gives a warning:
        #WARNING:  nonstandard use of \\ in a string literal
        #LINE 1: ...hot set project_code = substring(search_type from '=(\\w+)$'...
        self.run_sql('''
        update snapshot set project_code = substring(search_type from '=(\\w+)$');
        ''')

    def upgrade_v2_1_0_b08_002(self):
        self.run_sql('''
        CREATE INDEX snapshot_project_code_idx on snapshot(project_code);
        ''')


    def upgrade_v2_1_0_b08_001(self):
        self.run_sql('''
        ALTER TABLE snapshot ADD COLUMN project_code varchar(256);
        ''')

    #
    # 2.1.0.b05
    #
    def upgrade_v2_1_0_b05_002(self):
        self.run_sql('''
        CREATE UNIQUE INDEX transaction_state_ticket_idx on transaction_state(ticket);
        ''')

    def upgrade_v2_1_0_b05_001(self):
        self.run_sql('''
        ALTER TABLE transaction_state ADD PRIMARY KEY (id);
        ''')


    #
    # 2.1.0.a02
    #
    def upgrade_v2_1_0_a02_002(self):
        self.run_sql('''
        ALTER TABLE snapshot_type ADD COLUMN relfile text;
        ''')

    # Repeating here so 2.1.0 users can also get this 
    def upgrade_v2_1_0_a02_001(self):
        
        self.run_sql('''
        ALTER TABLE transaction_log add column title text;
        ''')



    #
    # 2.0.0.rc01
    #
    def upgrade_v2_0_0_rc01_001(self):
        
        self.run_sql('''
        ALTER TABLE transaction_log add column title text;
        ''')

    #
    # 2.0.0.b03
    #
   

    def upgrade_v2_0_0_b03_001(self):
        
        self.run_sql('''
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

    def upgrade_v2_0_0_a01_002(self):
        self.run_sql('''
    INSERT INTO search_object (search_type, namespace, description, "database", table_name, class_name, title, "schema") VALUES ('sthpw/access_log', 'sthpw', 'Access Log', 'sthpw', 'access_log', 'pyasm.search.SObject', 'Access Log', 'public');
        ''')


    def upgrade_v2_0_0_a01_001(self):
        self.run_sql('''
        CREATE TABLE access_log (
            id serial PRIMARY KEY,
            code varchar(256),
            url text,
            data text,
            start_time timestamp,
            end_time timestamp,
            duration float
        );
        ''')


    """



