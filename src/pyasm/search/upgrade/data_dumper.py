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

__all__ = ['DataDumper']

import sys, os


from schema_dumper import SchemaDumper


# dump the schema in the <cur_dir>/schema 
if __name__ == '__main__':

    executable = sys.argv[0]
    args = sys.argv[1:]

    if len(args) != 3:
        print "Usage: data_dumper.py <target_project> <project_type> <table>"
        sys.exit() 

    target_project = args[0]
    project_type = args[1]
    table = args[2]

    if project_type not in ['sthpw','prod','flash','game','design']:
        print "Usage: data_dumper.py <target_project> <project_type> <table>. Invalid \
            project type [%s]" % project_type
        sys.exit()
    

    dumper = SchemaDumper(target_project)
    dumper.set_file_path("%s/data/%s_%s.sql" %(os.getcwd(), project_type, table)) 
    dumper.dump_data(table)

