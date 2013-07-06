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

    if len(args) != 3:
        print "Usage: data_summary.py <target> <standard> <table>"
        sys.exit()

    target_project = args[0]
    standard_project = args[1]
    table = args[2]

    # get the current schema from the database
    dumper = SchemaDumper(target_project)
    dumper.dump_data(table)
    target_file = dumper.get_file_path()

    target = SqlParser()
    target.parse( target_file )

    cwd = os.path.dirname(executable)
    if not cwd:
        cwd = os.getcwd()

    # parse the standard version of the database
    standard_path = "%s/data/%s_%s.sql" % (cwd, standard_project, table)
    standard = SqlParser()
    standard.parse( standard_path )


    reporter = SqlReporter(target, standard)

    reporter.create_data_diffs()

    os.unlink(target_file)




