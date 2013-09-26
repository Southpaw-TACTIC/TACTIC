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

__all__ = ['TableSchemaDumper', 'TableDataDumper']


import re, sys
import types
import datetime
import codecs

from sql import SqlException


class TableSchemaDumper(object):

    def __init__(my, search_type, delimiter=None):
        my.search_type = search_type
        my.delimiter = "#"
        my.end_delimiter = my.delimiter
        my.ignore_columns = []



    def set_delimiter(my, delimiter, end_delimiter=None):
        my.delimiter = delimiter
        if not end_delimiter:
            my.end_delimiter = my.delimiter
        else:
            my.end_delimiter = end_delimiter


    def set_ignore_columns(my, columns=[]):
        my.ignore_columns = columns



    def dump_to_tactic(my, path=None, mode='sql'):

        from pyasm.search import SearchType, Sql, DbContainer

        search_type_obj = SearchType.get(my.search_type)
        database = search_type_obj.get_database()
        table = search_type_obj.get_table()
        db_resource = SearchType.get_db_resource_by_search_type(my.search_type)
        sql = DbContainer.get(db_resource)
        exists = sql.table_exists(table)   
        if not exists:
            return

        info = sql.get_column_info(table)
        impl = sql.get_database_impl()


        columns = info.keys()
        columns.sort()

        # if the table does not exist, there are no columns
        if not columns:
            return

        if path:
            import os
            f = codecs.getwriter('utf8')(open(path, 'ab'))
        else:
            import sys
            f = sys.stdout

        if not my.delimiter:
            my.delimiter = "--"
            my.end_delimiter = my.delimiter


        f.write( "%s\n" % my.delimiter )

        if mode == 'sobject':
            f.write("table = CreateTable('%s')\n" % my.search_type)
        else:
            f.write("table = CreateTable()\n")
            f.write("table.set_table('%s')\n" % table)

        # Hard code this - all search types have id as the primary key at the
        # moment
        primary_key_col = 'id'

        for column in columns:

            if column in my.ignore_columns:
                continue

            col_info = info[column]
            #print col_info
            space = " "*(25-len(column)) 
            data_type = col_info['data_type']
            is_nullable = col_info['nullable']

            if column == "id":
                # A dump will output a database independent serial
                #data_type = impl.get_serial()   <--- Database depenedent
                data_type = 'serial'
                f.write("table.add('%s',%s'%s', primary_key=True)\n" % (column, space, data_type) )
                continue

            elif data_type in ['varchar','char','nvarchar']:
                size = col_info.get('size')
                if size == -1:
                    size = 'max'
                if not size:
                    size = 256
                if is_nullable:
                    f.write("table.add('%s',%s'%s', length='%s' )\n" % (column, space, data_type, size))
                else:
                    f.write("table.add('%s',%s'%s', length='%s', not_null=True )\n" % (column, space, data_type, size))
                continue


            if is_nullable:
                f.write("table.add('%s',%s'%s' )\n" % (column, space, data_type))
            else:
                f.write("table.add('%s',%s'%s', not_null=True )\n" % (column, space, data_type))


        # add the constraints
        constraints = impl.get_constraints(db_resource, table)
        for constraint in constraints:
            name = constraint.get("name")
            columns = constraint.get("columns")
            mode = constraint.get("mode")
            if not name:
                name = "%s_%s_idx" % (name, "_".join(columns))
            f.write('''table.add_constraint(%s, mode="%s")\n''' % (columns, mode))
            #def add_constraint(my, columns, mode="UNIQUE"):


        #f.write("table.set_primary_key('id')\n")

        # Disable commit for now
        #if mode == 'sobject':
        #    f.write("table.commit()\n")

        f.write( "%s\n" % my.end_delimiter )
        f.write("\n")


class TableDataDumper(object):
    '''Dumps out sql statement'''

    def __init__(my):
        my.sobjects = None
        my.delimiter = "--"
        my.end_delimiter = my.delimiter

        my.database = None
        my.table = None

        my.no_exception = False

        my.pl_sql_var_out_fp = None
        my.pl_sql_ins_out_fp = None
        my.sql_out_fp = None

        my.include_id = True
        my.search_type = None
        my.ignore_columns = []


    def set_include_id(my, flag=True):
        my.include_id = flag

    def set_ignore_columns(my, columns=[]):
        my.ignore_columns = columns



    def set_delimiter(my, delimiter, end_delimiter=None):
        my.delimiter = delimiter
        if not end_delimiter:
            my.end_delimiter = my.delimiter
        else:
            my.end_delimiter = end_delimiter

    def set_sobjects(my, sobjects):

        from pyasm.search import Search, SObject, Insert, SearchType

        my.sobjects = sobjects
        first = my.sobjects[0]

        # get the database
        project_code = first.get_project_code()
        from pyasm.biz import Project
        project = Project.get_by_code(project_code)
        if not project:
            raise Exception("SObject [%s] has a project_code [%s] that does not exist" % (first.get_search_key(), project_code) )

        my.db_resource = project.get_project_db_resource()

        # get the search_type
        my.search_type = first.get_base_search_type()
        my.search_type_obj = SearchType.get(my.search_type)
        my.table = my.search_type_obj.get_table()


    def set_info(my, table):
        from pyasm.biz import Project
        project = Project.get()
        my.db_resource = project.get_project_db_resource()

        my.table = table

    def set_search_type(my, search_type):
        my.search_type = search_type


    def set_no_exception(my, flag):
        my.no_exception = flag


    def execute(my):
        assert my.db_resource
        assert my.table

        database = my.db_resource.get_database()

        from pyasm.search import Insert, Select, DbContainer, Search, Sql

        # get the data
        if not my.sobjects:
            search = Search("sthpw/search_object")

            # BAD assumption
            #search.add_filter("table", my.table)
            # create a search_type. This is bad assumption cuz it assumes project-specific search_type
            # should call set_search_type()
            if not my.search_type:
                my.search_type = "%s/%s" % (my.database, my.table)
            search.add_filter("search_type", my.search_type)

            my.search_type_obj = search.get_sobject()
            if not my.search_type_obj:
                if my.no_exception == False:
                    raise SqlException("Table [%s] does not have a corresponding search_type" % my.table)
                else:
                    return

            search_type = my.search_type_obj.get_base_key()
            search = Search(my.search_type)
            search.set_show_retired(True)
            my.sobjects = search.get_sobjects()
            
        # get the info for the table
        column_info = SearchType.get_column_info(my.search_type)

        for sobject in my.sobjects:
            print my.delimiter

            insert = Insert()
            insert.set_database(my.database)
            insert.set_table(my.table)

            data = sobject.data
            for name, value in data.items():

                if name in my.ignore_columns:
                    continue

                if not my.include_id and name == "id":
                    insert.set_value("id", '"%s_id_seq".nextval' % table, quoted=False)
                    #insert.set_value(name, value, quoted=False)
                elif value == None:
                    continue
                else:
                    # replace all of the \ with double \\
                    insert.set_value(name, value)

            print "%s" % insert.get_statement()
            print my.end_delimiter
            print



    def dump_tactic_inserts(my, path, mode='sql'):
        assert my.db_resource
        assert my.table

        database = my.db_resource.get_database()

        assert mode in ['sql', 'sobject']

        if path:
            import os
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
      
            #f = open(path, 'w')
            #f = codecs.open(path, 'a', 'utf-8')
            UTF8Writer = codecs.getwriter('utf8')
            f = UTF8Writer(open(path, 'ab'))
        else:
            import sys
            f = sys.stdout

        from pyasm.search import Insert, Select, DbContainer, Search, Sql

        # get the data
        if not my.sobjects:
            search = Search("sthpw/search_object")
            search.add_filter("table_name", my.table)
            search.add_order_by("id")
            my.search_type_obj = search.get_sobject()
            if not my.search_type_obj:
                if my.no_exception == False:
                    raise Exception("Table [%s] does not have a corresponding search_type" % my.table)
                else:
                    return

            search_type = my.search_type_obj.get_base_key()
            search = Search(search_type)
            search.set_show_retired(True)
            my.sobjects = search.get_sobjects()
            
        # get the info for the table
        from pyasm.search import SearchType, Sql
        column_info = SearchType.get_column_info(my.search_type)

        for sobject in my.sobjects:
            f.write( "%s\n" % my.delimiter )


            if mode == 'sobject':
                search_type = sobject.get_base_search_type()
                f.write("insert = SearchType.create('%s')\n" % search_type)
            else:
                f.write("insert.set_table('%s')\n" % my.table)

            data = sobject.get_data()
            for name, value in data.items():
                if name in my.ignore_columns:
                    continue

                if name == '_tmp_spt_rownum':
                    continue
                if not my.include_id and name == "id":
                    #insert.set_value("id", '"%s_id_seq".nextval' % table, quoted=False)
                    pass
                elif value == None:
                    continue
                else:
                    # This is not strong enough
                    #if value.startswith("{") and value.endswith("}"):
                    #    f.write("insert.set_expr_value('%s', \"\"\"%s\"\"\")\n" % (name, value))
                    if type(value) == types.IntType or \
                            type(value) == types.FloatType or \
                            type(value) == types.BooleanType or \
                            type(value) == types.LongType:

                        f.write("insert.set_value('%s', %s)\n" % (name, value))
                    else:    
                        # if the value contains triple double quotes, convert to
                        # triple quotes
                        if isinstance(value, datetime.datetime):
                            value = str(value)
                        elif isinstance(value, unicode):
                            #value = str(value)
                            value = value.encode("UTF-8")

                        # this fixes a problem with non-ascii characters
                        if isinstance(value, basestring):
                            quoted = value.startswith('"') and value.endswith('"')
                            value = repr(value)
                            quoted2 = value.startswith('"') and value.endswith('"')
                            if not quoted and quoted2:
                                value = value.strip('"')


                            # repr puts single quotes at the start and end
                            value = value.strip("'")
                            # and it puts a slash in front
                            value = value.replace(r"\'", "'")
                            # replace literal \n with newline (comes from repr)
                            value = value.replace(r"\n", "\n")


                            value = value.replace('"""', "'''")
                            #value = value.replace("\\", "\\\\")

                            # handle the case where the value starts with a quote
                            if value.startswith('"'):
                                value = '\\%s' % value
                            # handle the case where the value ends starts with a quote
                            if value.endswith('"'):
                                value = '%s\\"' % value[:-1]


                        f.write("insert.set_value('%s', \"\"\"%s\"\"\")\n" % (name, value))


            # Disable commit for now
            #if mode == 'sobject':
            #    f.write("insert.commit()\n")

            f.write( "%s\n" % my.end_delimiter )
            f.write( "\n" )

        if path:
            f.close()


    def set_sql_out_fps(my, sql_out_fp, pl_sql_var_out_fp, pl_sql_ins_out_fp):
        my.sql_out_fp = sql_out_fp
        my.pl_sql_var_out_fp = pl_sql_var_out_fp
        my.pl_sql_ins_out_fp = pl_sql_ins_out_fp


    # DEPRECATED
    # FIXME: why is there SQLServer code in an Oracle function
    def execute_mms_oracle_dump(my):
        assert my.db_resource
        assert my.table

        database = my.db_resource.get_database()

        if not my.sql_out_fp or not my.pl_sql_var_out_fp or not my.pl_sql_ins_out_fp:
            raise Exception("SQL and PL-SQL file pointers are required for generating output.")

        from pyasm.search import Insert, Select, DbContainer, Search, Sql

        # get the data
        if not my.sobjects:
            search = Search("sthpw/search_object")
            search.add_filter("table_name", my.table)
            my.search_type_obj = search.get_sobject()
            if not my.search_type_obj:
                if my.no_exception == False:
                    raise Exception("Table [%s] does not have a corresponding search_type" % my.table)
                else:
                    return

            search_type = my.search_type_obj.get_base_key()
            search = Search(search_type)
            search.set_show_retired(True)
            my.sobjects = search.get_sobjects()

        # get the info for the table
        column_info = my.search_type_obj.get_column_info()

        for sobject in my.sobjects:

            column_list = []
            value_list = []
            update_col_list = []
            update_map = {}

            timestamp_regex = re.compile("^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})")

            data = sobject.data
            sobject_id = data.get("id")
            do_pl_sql = False
            for name, value in data.items():
                if value == None:
                    continue
                else:
                    col_name = '"%s"' % name
                    column_list.append(col_name)

                    if isinstance(value, types.StringTypes):
                        if timestamp_regex.match(value):
                            value_list.append( "TO_TIMESTAMP('%s','RR-MM-DD HH24:MI:SS')" %
                                    str(value).split('.')[0][2:] )
                        else:
                            new_value = my.get_oracle_friendly_string_value( value )
                            if len(new_value) > 3800:
                            #{
                                do_pl_sql = True
                                var_name = "%s_%s_%s__var" % \
                                                ( my.table, col_name.replace('"',''), str(sobject_id).zfill(5) )

                                my.pl_sql_var_out_fp.write( "\n%s VARCHAR2(%s) := %s ;\n" %
                                                                (var_name, len(new_value), new_value) )
                                new_value = var_name
                            #}
                            value_list.append( new_value )


                    # elif type(value) == datetime.datetime:
                    #     value_list.append( "TO_TIMESTAMP('%s','RR-MM-DD HH24:MI:SS.FF')" %
                    #             str(value).split('.')[0][2:] )
                    else:
                        value_list.append( "%s" % value )

            if do_pl_sql:
                my.pl_sql_ins_out_fp.write( '\n' )
                from sql import Sql
                if database_type == "SQLServer":
                    my.pl_sql_ins_out_fp.write( 'INSERT INTO "%s" (%s) VALUES (%s);\n' %
                                        (my.database, my.table, ','.join(column_list), ','.join(value_list)) )
                else:
                    my.pl_sql_ins_out_fp.write( 'INSERT INTO "%s" (%s) VALUES (%s);\n' %
                                        (my.table, ','.join(column_list), ','.join(value_list)) )
            else:
                my.sql_out_fp.write( '\n' )
                from sql import Sql
                if database_type == "SQLServer":
                    my.sql_out_fp.write( 'INSERT INTO "%s" (%s) VALUES (%s);\n' %
                                        (my.database, my.table, ','.join(column_list), ','.join(value_list)) )
                else:
                    my.sql_out_fp.write( 'INSERT INTO "%s" (%s) VALUES (%s);\n' %
                                        (my.table, ','.join(column_list), ','.join(value_list)) )



    def get_oracle_friendly_string_value( my, str_value ):
        return "'%s'" % str_value.replace("'","''").replace('&',"&'||'")



