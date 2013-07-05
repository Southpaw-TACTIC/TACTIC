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

__all__ = ['SimpleUpgrade']


from pyasm.search.upgrade.project import *


class SimpleUpgrade(BaseUpgrade):

    #
    # 2.5.0.a01
    #
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
            timestamp timestamp,
            s_status varchar(256)
        );
        ''')




    #
    # 1.9.0.a01
    #
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


    def upgrade_v1_6_0_b2_002(my):
        my.run_sql('''
        CREATE TABLE naming (
            id serial NOT NULL,
            search_type character varying(100),
            dir_naming text,
            file_naming text
        );
        ''')

    def upgrade_v1_6_0_b2_001(my):
        my.run_sql('''
        CREATE TABLE prod_setting (
            id serial NOT NULL,
            "key" character varying(100),
            value text,
            description text,
            "type" character varying(30),
            search_type character varying(200)
        );
        ''')


