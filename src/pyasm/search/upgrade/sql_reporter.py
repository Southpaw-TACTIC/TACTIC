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

# DEPRECATED


class SqlReporter:

    def __init__(my, target, standard):
        my.target = target
        my.standard = standard


    def ignore_table(my, table):
        if table.startswith("pga_") or table.startswith("pg_"):
            return True
        else:
            return False


    def compare_tables(my):
        
        t_tables = my.target.get_tables()
        s_tables = my.standard.get_tables()

        print "-- extra tables: ", [x for x in t_tables if x not in s_tables]
        missing_tables = [x for x in s_tables if x not in t_tables]
        print "-- missing tables: ", missing_tables


    def compare_all_schema(my):
        # get union of all tables
        t_tables = my.target.get_tables()
        s_tables = my.standard.get_tables()

        missing_tables = [x for x in s_tables if x not in t_tables]
        tables = t_tables
        tables.extend(missing_tables)


        for table in tables:
            if my.ignore_table(table):
                continue
            my.compare_table_schema(table)


    def compare_table_schema(my, table):
        '''dumps a readable comparison between 2 tables'''
        target_data = my.target.get_data(table)
        standard_data = my.standard.get_data(table)

        columns = target_data.columns
        columns2 = standard_data.columns

        diffs = []
        pattern = "%-18s%-45s%-45s"

        for column, schema in columns.items():

            if not columns2.has_key(column):
                database = "x"
            else:
                database = columns2[column]
                if schema != database:
                    database = database
                else:
                    #schema = "-"
                    #database = "-"
                    continue

            diffs.append( pattern % (column,schema,database) )


        for column2, database in columns2.items():
            if not columns.has_key(column2):
                schema = "x"
                diffs.append( pattern % (column2,schema,database) )

        extras = []
        new_mods = []

        # print constraints
        target_constraints = target_data.constraints
        standard_constraints = standard_data.constraints

        if target_constraints != standard_constraints:
            # go through the standard constraints and print the ones
            # that are not in the target
            for standard_constraint in standard_constraints:
                if standard_constraint not in target_constraints:
                    new_mods.append(standard_constraint)

            for target_constraint in target_constraints:
                if target_constraint not in standard_constraints:
                    extras.append(target_constraint)

        # print indexes
        target_indexes = target_data.indexes
        standard_indexes = standard_data.indexes

        if target_indexes != standard_indexes:
            for standard_index in standard_indexes:
                if standard_index not in target_indexes:
                    new_mods.append(standard_index)

            for target_index in target_indexes:
                if target_index not in standard_indexes:
                    extras.append(target_index)


        # print everything out
        if not diffs and not extras and not new_mods:
            return
        print
        print
        print "Table: ", table
        print "-"*20

        if diffs:
            print pattern % ("column","target schema","standard schema")
            print "-"*110

            for diff in diffs:
                print diff

            print "-"*110


        for new in new_mods:
            print new
        # print all of the extras
        if extras:
            print "Not in standard:"
            for extra in extras:
                print "\t", extra



    def create_missing_tables(my):
        t_tables = my.target.get_tables()
        s_tables = my.standard.get_tables()

        missing_tables = [x for x in s_tables if x not in t_tables]
        
        file = open("upgrade.sql","w")

        for table in missing_tables:
            if my.ignore_table(table):
                continue
            data = my.standard.get_data(table)
            print data.get_create_table()
            file.write( data.get_create_table() )

        file.close()
 


    def create_extra_tables(my):
        t_tables = my.target.get_tables()
        s_tables = my.standard.get_tables()

        extra_tables = [x for x in t_tables if x not in s_tables]

        
        for table in extra_tables:
            if my.ignore_table(table):
                continue
            data = my.target.get_data(table)

            print data.get_create_table()

 


    def create_diffs(my):
        t_tables = my.target.get_tables()
        s_tables = my.standard.get_tables()

        common_tables = [x for x in s_tables if x in t_tables]

        for table in common_tables:
            target_data = my.target.get_data(table)
            standard_data = my.standard.get_data(table)
            target_data.get_diff(standard_data)
            



    def create_data_diffs(my):
        t_tables = my.target.get_tables()
        s_tables = my.standard.get_tables()

        common_tables = [x for x in s_tables if x in t_tables]

        for table in common_tables:
            print "table: ", table
            target_data = my.target.get_data(table)
            standard_data = my.standard.get_data(table)

            for row_key,target_rows in target_data.rows.items():

                # check if the standard has this entry
                if not standard_data.rows.has_key(row_key):
                    print "Entry not in target:"
                    #print target_rows
                    print "\tINSERT INTO %s (%s) VALUES (%s)" % (table, ", ".join(target_rows.keys()), ", ".join(["'%s'" % x for x in target_rows.values()] ))
                    continue



                standard_rows = standard_data.rows[row_key]

                if target_rows != standard_rows:

                    target_keys = target_rows.keys()
                    for col_key in target_keys:
                        if target_rows[col_key] != standard_rows[col_key]:
                            print "Data does not match:"
                            print "column: ", col_key
                            print "\t'%s' != '%s'" % \
                                (target_rows[col_key],standard_rows[col_key])



            for row_key,standard_rows in standard_data.rows.items():

                # check if the target has this entry
                if not target_data.rows.has_key(row_key):
                    print "Entry not in standard:"
                    #print standard_rows
                    print "\tINSERT INTO %s (%s) VALUES (%s)" % (table, ", ".join(target_rows.keys()), ", ".join(["'%s'" % x for x in standard_rows.values()] ))







