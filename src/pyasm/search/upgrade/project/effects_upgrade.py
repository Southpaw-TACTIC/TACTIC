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

__all__ = ['EffectsUpgrade']


from pyasm.search.upgrade.project import *


class EffectsUpgrade(BaseUpgrade):

    def upgrade_20061102(self):
        self.run_sql('''
        -- add a keywords column to the art_reference table --
        alter table art_reference add column keywords text;
        ''')


    def upgrade_20060907(self):
        self.run_sql('''
        ALTER TABLE texture ADD COLUMN pipeline varchar(30);
        ''')






