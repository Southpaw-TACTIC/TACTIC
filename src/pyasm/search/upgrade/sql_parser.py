#!/usr/bin/python
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

__all__ = ['TableData', 'SqlParser']


import sys, os, re



class Postgres(object):
    def get_create_table(my):
        return "CREATE TABLE"

    def get_alter_table(my):
        return "ALTER TABLE ONLY"

    def get_add_constraint(my):
        return "ADD CONSTRAINT"

    def get_create_index(my):
        return "CREATE INDEX"

    def get_create_unique_index(my):
        return "CREATE UNIQUE INDEX"


class TableData:

    def __init__(my, table):
        my.table = table
        my.database = Postgres()

        my.columns = {}
        my.columns_order = []

        my.constraints = []
        my.indexes = []

        my.rows = {}


    def add_column(my, column, create):
        my.columns[column] = create
        my.columns_order.append(column)


    def get_create_table(my):

        create = ""
        create += "--\n"
        create += "-- Create table: %s\n" % my.table
        create += "--\n"
        create += "%s %s (\n" % (my.database.get_create_table(), my.table)
        tmp = []
        for column in my.columns_order:
            value = my.columns[column]
            tmp.append("    %s %s" % (column,value) )
        create += ",\n".join(tmp)
        create += "\n);\n"

        for constraint in my.constraints:
            create += "%s %s\n" % (my.database.get_alter_table(), my.table)
            create += "    %s\n" % constraint

        for index in my.indexes:
            #create += "%s %s\n" % (my.database.get_create_unique_index(), my.table)
            create += "%s\n" % index


        return create


    def get_alter_table(my, column):
        alter =  "%s %s\n" % (my.database.get_alter_table(), my.table)
        alter += "    ADD COLUMN %s %s;" % (column, my.columns[column])
        return alter


    def get_diff(my,standard_data):
        '''gets the sql difference between the two tables'''

        # print add columns
        extra_columns = [x for x in standard_data.columns if x not in my.columns]
        for column in extra_columns:
            print standard_data.get_alter_table(column)

        #for column, definition in my.columns.items():
        #    if column in extra_columns:
        #        continue
        #    definition2 = data.columns[column]
        #    if definition != definition2:
        #        print definition2

            





    def compare(my, data):
        missing_columns = [x for x in my.columns if x not in data.columns]
        extra_columns = [x for x in data.columns if x not in my.columns]

        if missing_columns:
            print "missing columns: ", missing_columns
        if extra_columns:
            print "extra columns: ", extra_columns

            for extra_column in extra_columns:
                print data.get_alter_table(extra_column)

        missing_constraints = [x for x in my.constraints if x not in data.constraints]
        extra_constraints = [x for x in data.constraints if x not in my.constraints]
        if missing_constraints:
            print "missing constraints: ", missing_constraints
        if extra_constraints:
            print "extra constraints: ", extra_constraints






class SqlParser:

    def __init__(my):
        my.tables = {}
        my.database = Postgres()


    def get_tables(my):
        tables = my.tables.keys()
        tables.sort()
        return tables


    def get_data(my, table):
        if my.tables.has_key(table):
            return my.tables[table]
        else:
            return TableData(table)



    def _extract_values(my, expr, line):
        p = re.compile(expr, re.DOTALL)
        m = p.search(line)
        if not m:
            return []
        values = m.groups()
        return values


    def _extract_value(my, expr, line):
        values = my._extract_values(expr,line)
        if not values:
            return None
        return values[0]


    def _extract_table(my, expr, line):
        table = my._extract_value(expr, line)
        table = table.replace('"','')
        return table

 
    def parse(my, file_path):

        # open file and read
        file = open(file_path)
        lines = file.readlines()
        file.close()

        create_table = None
        alter_table = None
        alter_table_line = None

        tmp_line = ""

        for line in lines:
            line = line.rstrip()
            line = line.rstrip(",")
            line = line.lstrip()

            # handle create
            if line.startswith(my.database.get_create_table()):
                expr = '%s "?(\w+)"? \(' % my.database.get_create_table()
                create_table = my._extract_table(expr, line)

                data = TableData(create_table)
                my.tables[create_table] = data

                continue


            if create_table: 
                if line == ");":
                    create_table = None
                    continue

                # handle the line
                tmp = line.split()
                column = tmp[0]
                column = column.replace('"','')
                create = " ".join(tmp[1:])
                my.tables[create_table].add_column(column, create)
                continue



            # handle alter table
            if line.startswith(my.database.get_alter_table()):
                expr = '%s "?(\w+)"?' % my.database.get_alter_table()
                alter_table = my._extract_table(expr, line)
                alter_table_line = line
                continue


            if alter_table:

                if line == "":
                    alter_table = None
                    continue

                alter_table_line += " %s" % line
                my.tables[alter_table].constraints.append(alter_table_line)


            # handle create index
            if line.startswith(my.database.get_create_index()):
                expr = '%s \w+ ON "?(\w+)"?' % (my.database.get_create_index())
                index_table = my._extract_table(expr, line)
                if index_table:
                    my.tables[index_table].indexes.append(line)

            # handle create index
            if line.startswith(my.database.get_create_unique_index()):
                expr = '%s \w+ ON "?(\w+)"?' % (my.database.get_create_unique_index())
                index_table = my._extract_table(expr, line)
                if index_table:
                    my.tables[index_table].indexes.append(line)


            # handle inserts
            if tmp_line != "" or line.startswith("INSERT INTO"):

                # have to figure out is this is the complete line
                if not line.endswith(";"):
                    tmp_line += "\n"+line
                    continue

                if tmp_line != "":
                    line = tmp_line + "\n" + line
                    tmp_line = ""


                expr = '%s "?(\w+)"? \(' % ("INSERT INTO")
                data_table = my._extract_table(expr, line)

                expr = '\((.*)\) VALUES \((.*)\);$'
                info = my._extract_values(expr, line)
                if not info:
                    print "Error: "
                    print line
                    raise Exception("Improper INSERT statement")

                columns = info[0].split(", ")
                columns = [ x.lstrip('"') for x in columns ]
                columns = [ x.rstrip('"') for x in columns ]

                values = info[1].split(", ")
                values = [ x.lstrip("'") for x in values ]
                values = [ x.rstrip("'") for x in values ]

                rows = {}
                for i in range(0, len(columns)):
                    rows[columns[i]] = values[i]

                # ensure that the data object exists
                if not my.tables.has_key(data_table):
                    data = TableData(create_table)
                    my.tables[data_table] = data


                # store the data by the unique identifier
                if data_table == "search_object":
                    primary_index = 1
                    
                elif "code" in columns:
                    primary_index = columns.index('code')
                elif "id" in columns:
                    primary_index = columns.index('id')
                else:
                    primary_index = 1

                primary_value = values[primary_index]
                my.tables[data_table].rows[primary_value] = rows



    def compare(my, data, data2):

        columns = data.columns
        columns2 = data2.columns

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

        if diffs:
            print
            print
            print "Table: ", table
            print "-"*20

            print pattern % ("column","standard schema","target schema")
            print "-"*110

            for diff in diffs:
                print diff

            print "-"*110


        # print constraints
        constraints = data.constraints
        constraints2 = data2.constraints

        if constraints != constraints2:
            print constraints
            print constraints2

        # print indexes
        indexes = data.indexes
        indexes2 = data2.indexes

        if indexes != indexes:
            print indexes
            print indexes2




if __name__ == '__main__':

    # test parser
    import sys
    db_parser = SqlParser()
    db_parser.parse( sys.argv[1] )






