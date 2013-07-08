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

from schema_dumper import *
from sql_parser import *
from sql_reporter import *

import sys, os

if __name__ == '__main__':


    executable = sys.argv[0]
    args = sys.argv[1:]


    if len(args) != 2:
        print "Usage: summary.py <target> <standard>"
        print "e.g. if you have a 3d project named 'dragonball', run:"
        print "       summary.py dragonball prod "
        sys.exit()

    cwd = os.path.dirname(executable)
    if not cwd:
        cwd = "."


    target_project = args[0]
    standard_project = args[1]

    # get the current schema from the database
    dumper = SchemaDumper(target_project)
    dumper.dump_schema()
    target_file = dumper.get_file_path()

    target = SqlParser()
    target.parse( target_file )

    # parse the standard version of the database
    standard_path = "%s/schema/%s_schema.sql" % (cwd, standard_project)
    standard = SqlParser()
    standard.parse( standard_path )


    reporter = SqlReporter(target, standard)
    reporter.compare_tables()

    reporter.compare_all_schema()

    reporter.create_missing_tables()

    reporter.create_diffs()

    os.unlink(target_file)




