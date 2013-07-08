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

__all__ = ['SchemaDumper']

import sys, os


class SchemaDumper(object):
    '''Note: this currently has to be run on the local machine of the
    database'''
    def __init__(my, database):
        my.database = database
        my.file_path = None

    def set_file_path(my, file_path):
        my.file_path = file_path
        
    def get_file_path(my):
        return my.file_path

    def dump_schema(my):

        if os.name == "nt":
            tmp_dir = "C:/temp"
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
        else:
            tmp_dir = "/tmp"
        
        if not my.file_path:
            my.file_path = "%s/%s.sql" % (tmp_dir, my.database)

        cmd = "pg_dump -U postgres -E UTF8 --schema-only %s > \"%s\"" % \
            (my.database, my.file_path)
        os.system(cmd)



    def dump_data(my, table):

        if os.name == "nt":
            tmp_dir = "C:/temp"
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
        else:
            tmp_dir = "/tmp"
        
        if not my.file_path:
            my.file_path = "%s/%s.sql" % (tmp_dir, my.database)

        cmd = "pg_dump -U postgres --column-inserts --data-only -t %s %s > \"%s\"" % \
            (table, my.database, my.file_path)
        os.system(cmd)

# dump the schema in the <cur_dir>/schema 
if __name__ == '__main__':

    executable = sys.argv[0]
    args = sys.argv[1:]

    if len(args) != 2:
        print "Usage: schema_dumper.py <target_project> <project_type>"
        sys.exit() 

    target_project = args[0]
    project_type = args[1]
    if project_type not in ['sthpw','prod','flash','game','design']:
        print "Usage: schema_dumper.py <target_project> <project_type>. Invalid \
            project type [%s]" % project_type
        sys.exit()

    cwd = os.path.dirname(executable)
    if not cwd:
        cwd = os.getcwd()

            
    dumper = SchemaDumper(target_project)
    dumper.set_file_path("%s/schema/%s_schema.sql" %(cwd, project_type)) 
    dumper.dump_schema()



