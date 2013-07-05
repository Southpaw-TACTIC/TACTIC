#!/usr/bin/env python


# This is a simple command line script that can be used to backup the
# TACTIC database.  It is independent of TACTIC, so can be run on
# servers where TACTIC is not install with the database.

class DatabaseBackup(object):

    def execute(my):
        base_dir = "/tmp"
        root = 'tacticdb'

        import datetime
        now = datetime.datetime.now()
        date = now.strftime("%Y%m%d_%H%M")
        file_name = '%s_%s.sql' % (root, date)
        path = "%s/%s" % (base_dir, file_name)

        print "Backing up database to: [%s]" % path

        import os
        cmd = 'pg_dumpall -U postgres > %s' % path
        os.system(cmd)
        cmd = 'gzip -f %s' % path
        os.system(cmd)


if __name__ == '__main__':

    cmd = DatabaseBackup()
    cmd.execute()

