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

__all__ = ["ColumnAddCmd", "ColumnDropCmd", "ColumnAlterCmd", "ColumnAddIndexCmd"]

'''A collection of useful command for the database'''

from pyasm.common import TacticException
from pyasm.biz import Project
from pyasm.search import SearchType, DbContainer, AlterTableUndo, AlterTable, Sql

from command import Command

class ColumnAddCmd(Command):
    '''Add a column'''
    def __init__(my, search_type, attr_name, attr_type, nullable=True):
        my.search_type = search_type
        my.attr_name = attr_name
        my.attr_type = attr_type
        my.nullable = nullable
        super(ColumnAddCmd,my).__init__()



    def get_data_type(cls, search_type, attr_type):
        search_type_obj = SearchType.get(search_type)

        db_resource = Project.get_db_resource_by_search_type(search_type)
        sql = DbContainer.get(db_resource)
        impl = sql.get_database_impl()


        # SearchType Manager and Add Widget Column use mixed upper and
        # lowercases for the following attr_type, so fix it at some point
        if not attr_type:
            attr_type = "varchar"

        if attr_type == "integer":
            data_type = impl.get_int() 
        elif attr_type == "float":
            data_type = "float"
        elif attr_type == "boolean":
            data_type = impl.get_boolean()
        elif attr_type == "link":
            data_type = "text"
        elif attr_type.startswith('varchar'):
            data_type = attr_type

        elif attr_type == 'time':
            data_type = impl.get_timestamp()
        elif attr_type in ["Date", "date"]:
            data_type = impl.get_timestamp()
        elif attr_type == "Category":
            data_type = "varchar(256)"
        elif attr_type in ["text", "Text"]:
            data_type = impl.get_text()
        elif attr_type in ["Date Range", 'timestamp']:
            data_type = impl.get_timestamp()
        elif attr_type == "Checkbox":
            data_type = "varchar(256)"
        elif attr_type in ["Foreign Key", "foreign_key"]:
            data_type = "varchar(256)"
        elif attr_type in ["List", "list"]:
            data_type = "varchar(512)"
        elif attr_type == "Name/Code":
            data_type = "varchar(256)"
        elif attr_type == "Number":
            data_type = impl.get_int() 

        elif attr_type in ["currency", "scientific", "percent"]:
            data_type = "float"
        elif attr_type == "timecode":
            data_type = impl.get_int() 

        else:
            #data_type = "varchar(256)"
            data_type = impl.get_varchar()

        return data_type

    get_data_type = classmethod(get_data_type)


    def execute(my):

        search_type_obj = SearchType.get(my.search_type)

        db_resource = Project.get_db_resource_by_search_type(my.search_type)
        sql = DbContainer.get(db_resource)
        impl = sql.get_database_impl()

        data_type = my.get_data_type(my.search_type, my.attr_type)


        """
        # SearchType Manager and Add Widget Column use mixed upper and
        # lowercases for the following attr_type, so fix it at some point
        if not my.attr_type:
            my.attr_type = "varchar"

        if my.attr_type == "integer":
            type = impl.get_int() 
        elif my.attr_type == "float":
            type = "float"
        elif my.attr_type == "boolean":
            type = impl.get_boolean()
        elif my.attr_type == "link":
            type = "text"
        elif my.attr_type.startswith('varchar'):
            type = my.attr_type

        elif my.attr_type == 'time':
            type = impl.get_timestamp()
        elif my.attr_type in ["Date", "date"]:
            type = impl.get_timestamp()
        elif my.attr_type == "Category":
            type = "varchar(256)"
        elif my.attr_type in ["text", "Text"]:
            type = impl.get_text()
        elif my.attr_type in ["Date Range", 'timestamp']:
            type = impl.get_timestamp()
        elif my.attr_type == "Checkbox":
            type = "varchar(256)"
        elif my.attr_type in ["Foreign Key", "foreign_key"]:
            type = "varchar(256)"
        elif my.attr_type in ["List", "list"]:
            type = "varchar(512)"
        elif my.attr_type == "Name/Code":
            type = "varchar(256)"
        elif my.attr_type == "Number":
            type = impl.get_int() 

        elif my.attr_type in ["currency", "scientific", "percent"]:
            type = "float"
        elif my.attr_type == "timecode":
            type = impl.get_int() 

        else:
            #type = "varchar(256)"
            type = impl.get_varchar()
        """


        # if there is no type, then no column is created for widget_config
        if my.attr_type == "Date Range":
            column1 = "%s_start_date" % my.attr_name
            column2 = "%s_end_date" % my.attr_name
            my._add_column(column1, data_type)
            my._add_column(column2, data_type)
        elif type != "":
            my._add_column(my.attr_name, data_type)


        my.add_description("Added attribute '%s' of type '%s'" % (my.attr_name, my.attr_type) )


    def _add_column(my, column, type):

        # if there is no type, then no column is created for widget_config
        if type != "":
            # alter the table
            search_type_obj = SearchType.get(my.search_type)
            db_resource = Project.get_db_resource_by_search_type(my.search_type)
            sql = DbContainer.get(db_resource)
            impl = sql.get_database_impl()
            table = search_type_obj.get_table()

            columns = sql.get_columns(table)
            # if the column exists already, skip it
            if column in columns:
                print "skipping: ", column
                raise TacticException('[%s] already existed in this table [%s]'%(column, table))
                return

            # FIXME: database dependency should be in DatabaseImpl
            if sql.get_database_type() == "Oracle":
                statement = 'ALTER TABLE "%s" ADD("%s" %s)' % \
                    (table, column, type)
            else:
                if sql.get_database_type() == 'SQLServer':
                    statement = 'ALTER TABLE [%s] ADD "%s" %s' % \
                        (table, column, type)
                else: 
                    statement = 'ALTER TABLE "%s" ADD COLUMN "%s" %s' % \
                        (table, column, type)
            if not my.nullable:
                statement = '%s NOT NULL' %statement
            sql.do_update(statement)

            # FIXME: should we be storing just the database ... or maybe the
            # project?
            #database = sql.get_database_name()
            AlterTableUndo.log_add(db_resource,table,column,type)




class ColumnDropCmd(Command):
    '''Drop a column'''
    def __init__(my, search_type, attr_name):
        # this should be a full search_type
        super(ColumnDropCmd,my).__init__()
        my.search_type = search_type
        my.attr_name = attr_name

    def check(my):
        #search_type_obj = SearchType.get(my.search_type)
        columns =  SearchType.get_columns(my.search_type)
        if my.attr_name not in columns:
            raise TacticException('[%s] does not exist in this table [%s]'%(my.attr_name, my.search_type))
        return True

    def execute(my):    
        search_type_obj = SearchType.get(my.search_type)
        database = search_type_obj.get_database()
        table = search_type_obj.get_table()

        alter = AlterTable(my.search_type)
        alter.drop(my.attr_name)

        # log it first before committing
        AlterTableUndo.log_drop(database,table, my.attr_name)
        alter.commit()  
        

class ColumnAlterCmd(Command):
    '''Alter a column'''
    def __init__(my, search_type, attr_name, data_type=None, nullable=True):
        # this should be a full search_type
        my.search_type = search_type
        my.attr_name = attr_name    
        my.data_type = data_type
        my.nullable = nullable
        
        super(ColumnAlterCmd,my).__init__()

    def execute(my):    
        search_type_obj = SearchType.get(my.search_type)
        database = search_type_obj.get_database()
        table = search_type_obj.get_table()

        alter = AlterTable(my.search_type)
        #TODO: check the varchar length and put it in
        alter.modify(my.attr_name, my.data_type, not_null=not my.nullable)

        # log it first before committing to get the corrent from and to data type
        AlterTableUndo.log_modify(database,table, my.attr_name, \
             my.data_type, not my.nullable)
        alter.commit()



class ColumnAddIndexCmd(Command):

    def __init__(my, **kwargs):
        my.search_type = kwargs.get("search_type")
        my.column = kwargs.get("column")
        my.constraint = kwargs.get("constraint")


    def execute(my):
        search_type_obj = SearchType.get(my.search_type)
        table = search_type_obj.get_table()

        db_resource = Project.get_db_resource_by_search_type(my.search_type)
        sql = DbContainer.get(db_resource)

        index_name = "%s_%s_idx" % (table, my.column)
        
        if my.constraint == "unique":
            statement = 'ALTER TABLE "%s" add constraint "%s" UNIQUE ("%s")' % (table, index_name, my.column)
        else:
            statement = 'CREATE INDEX "%s" ON "%s" ("%s")' % (index_name, table, my.column)

        sql.do_update(statement)
        sql.commit() 


