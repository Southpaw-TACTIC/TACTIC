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
# Description: Custom properties are a list of properties added to sobjects
#   that are not part of the standard templates.

__all__ = ["CustomProperty"]


from pyasm.search import Search, SObject, SearchType, AlterTableUndo, DbContainer, SqlException


class CustomProperty(SObject):

    SEARCH_TYPE = "prod/custom_property"
    
    def delete(my,log=False):
        column = my.get_value("name")

        search_type = my.get_value("search_type")
        search_type_obj = SearchType.get(search_type)

        table = search_type_obj.get_table()
        database = search_type_obj.get_database()

        # remove it from the table
        if log:
            AlterTableUndo.log_drop(database, table, column)
            sql = DbContainer.get(database)
            try:

                from pyasm.search.sql import Sql
                if Sql.get_database_type() == 'SQLServer':
                    statement = 'ALTER TABLE [%s] DROP "%s" %s' % \
                        (table, column)
                else:
                    statement = 'ALTER TABLE "%s" DROP COLUMN "%s"' % (table, column) 

                sql.do_update(statement)
            except SqlException, e:
                print("WARNING: %s" % e )
            

        super(CustomProperty, my).delete(log)



