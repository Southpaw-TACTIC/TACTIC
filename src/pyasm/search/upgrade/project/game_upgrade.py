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

__all__ = ['GameUpgrade']


# DEPRECATED


from pyasm.search.upgrade.project import *


class GameUpgrade(BaseUpgrade):

    def upgrade_v1_9_0_a1_005(my):
        my.run_sql('''
        ALTER TABLE art_reference add column code varchar(256);
        ''') 


    def upgrade_v1_9_0_a1_004(my):
        my.run_sql('''
        ALTER TABLE asset ALTER COLUMN pipeline_code TYPE varchar(256);
        ''') 


    def upgrade_v1_9_0_a1_003(my):
        my.run_sql('''
        ALTER TABLE level ADD COLUMN pipeline_code varchar(256);
        ''') 

    def upgrade_v1_9_0_a1_002(my):
        my.run_sql('''
        ALTER TABLE prod_setting ADD COLUMN category varchar(256);
        ''') 

    def upgrade_v1_9_0_a1_001(my):
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


    def upgrade_20071015(my):
        my.run_sql('''
        CREATE TABLE naming (
            id serial PRIMARY KEY,
            search_type varchar(100),
            dir_naming text,
            file_naming text
        );
        ''')


    def upgrade_20061110(my):
        my.run_sql('''
        alter table asset rename column pipeline to pipeline_code;
        ''')   

    def upgrade_20060918(my):
        my.run_sql('''
        -- add repo_path to asset_library
        alter table asset_library add column repo_path text;
        -- rename column instance to name
        alter table instance rename column instance to name;
        
        ''')



