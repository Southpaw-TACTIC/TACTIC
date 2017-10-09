############################################################
#
#    Copyright (c) 2011, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#


from pyasm.common import Config, Common

class DatabaseBackup(object):

    def execute(my):
        base_dir = "/tmp"
        root = 'tacticdb'

        import datetime
        now = datetime.datetime.now()
        date = now.strftime("%Y%m%d_%H%M")
        file_name = '%s_%s.sql' % (root, date)
        path = "%s/%s" % (base_dir, file_name)

        print("Backing up database to: [%s]" % path)

        import os
        cmd = 'pg_dumpall -U postgres > %s' % path
        os.system(cmd)
        cmd = 'gzip -f /tmp/%s' % file_name
        os.system(cmd)



