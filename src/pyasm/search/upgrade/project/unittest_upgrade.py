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

    def upgrade_v3_8_0_rc01_001(self):
        self.run_sql('''
        ALTER TABLE city add column metadata text;
        ''')


    def upgrade_v3_1_0_b09_001(self):
        self.run_sql('''
        ALTER TABLE person add column pipeline_code varchar(256);
        ''')

    def upgrade_v2_5_0_v01_003(self):
        self.run_sql('''
        ALTER TABLE person add column "timestamp" timestamp default now();
        ''')

    def upgrade_v2_5_0_v01_002(self):
        self.run_sql('''
        ALTER TABLE person add column age integer;
        ''')

    def upgrade_v2_5_0_v01_001(self):
        self.run_sql('''
        ALTER TABLE person add column birth_date timestamp;
        ''')

    def upgrade_v2_5_0_rc12_001(self):
        self.run_sql('''
        ALTER TABLE city ADD CONSTRAINT city_code_unique UNIQUE(code);
        ''')

    def upgrade_v2_5_0_rc12_002(self):
        self.run_sql('''
        ALTER TABLE country ADD CONSTRAINT country_code_unique UNIQUE(code);
        ''')

    def upgrade_v2_5_0_rc12_003(self):
        self.run_sql('''
        ALTER TABLE person ADD CONSTRAINT person_code_unique UNIQUE(code);
        ''')

    # 2.5.0.rc01
    def upgrade_v2_5_0_rc01_001(self):
        self.run_sql('''
        ALTER TABLE person ADD COLUMN age integer
        ''')



    #
    # 2.1.0.b01
    #
    def upgrade_v2_1_0_b01_001(self):
        self.run_sql('''
        alter table person add column metadata text;
        ''')


    #
    # 2.0.0.a01
    #
    # ???? Is this needed?    
    def upgrade_v2_0_0_a01_003(self):
        self.run_sql('''
        CREATE TABLE session_contents (
            id serial NOT NULL,
            "login" character varying(100) NOT NULL,
            pid integer NOT NULL,
            data text,
            "session" text,
            "timestamp" timestamp without time zone DEFAULT now()
        );
        ''')




