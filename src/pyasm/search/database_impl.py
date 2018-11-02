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

__all__ = ['DatabaseImpl', 'PostgresImpl', 'OracleImpl', 'SqliteImpl', 'MySQLImpl', 'SQLServerImpl', 'TacticImpl', 'DatabaseImplException']

import os, sys, types, re
import subprocess
import datetime

from pyasm.common import Environment, SetupException, Config, Container, TacticException, SPTDate


class DatabaseImplException(TacticException):
    pass



class DatabaseImplInterface(object):


    def get_columns(cls, db_resource, table):
        pass

    def get_column_info(cls, db_resource, table, use_cache=True):
        pass

    def is_column_sortable(self, db_resource, table, column):
        pass

    def get_id_col(db_resource, search_type):
        pass

    def get_code_col(db_resource, search_type):
        pass


    def get_page(self, limit=None, offset=0):
        pass

    def get_table_info(self, db_resource):
        pass

    def table_exists(self, db_resource, table):
        pass

    def execute_query(self, sql, select):
        pass

    def execute_update(self, sql, update):
        pass




class DatabaseImpl(DatabaseImplInterface):
    '''Provides an abstraction layer for the various databases'''

    def get_database_type(self):
        return None


    def get_version(self):
        return (0,0,0)


    def get(vendor=None):
        '''Get the current database implementation'''
        from sql import Sql
        if not vendor:
            vendor = Sql.get_default_database_type()
            return DatabaseImpl.get(vendor)

        if vendor == "PostgreSQL":
            return PostgresImpl()
        elif vendor == "Sqlite":
            return SqliteImpl()
        elif vendor == "MySQL":
            return MySQLImpl()
        elif vendor == "SQLServer":
            return SQLServerImpl()
        elif vendor == "Oracle":
            return OracleImpl()

        # TEST
        elif vendor == "MongoDb":
            from mongodb import MongoDbImpl
            return MongoDbImpl()

        elif vendor == "TACTIC":
            return TacticImpl()

        else:
            class_name = Config.get_value(vendor, "class")

            from pyasm.common import Common
            from pyasm.search import Search
            search = Search("sthpw/db_resource")
            search.add_filter("vendor", vendor)
            sobject = search.get_sobject()
            if sobject:
                impl_class = sobject.get_value("db_impl_class", no_exception=True)
                impl_class = "spt.tools.salesforce.SalesforceImpl"
                return Common.create_from_class_path(impl_class)

        raise DatabaseImplException("Vendor [%s] not supported" % vendor)

    get = staticmethod(get)



    def preprocess_sql(self, data, unquoted_cols):
        pass

    def postprocess_sql(self, statement):
        return statement

    def process_value(self, name, value, column_type="varchar"):
        '''process a database value based on column type.

        @params:
            value: current input value
            column_type: the database column type

        @return
            dict:
                value: the new value
                quoted: True|False - determines whether the value is quoted or not
        '''
        return None
    
    def process_date(self, value):
        '''DatabaseImpl process date str to work with db before commit. SQLServer needs it'''
        return value




    def get_id_col(self, db_resource, search_type):
        from pyasm.search import SearchType
        search_type_obj = SearchType.get(search_type)
        id_col = search_type_obj.get_search_type_id_col()
        return id_col


    def get_code_col(self, db_resource, search_type):
        from pyasm.search import SearchType
        search_type = SearchType.get(search_type)
        code_col = search_type.get_search_type_code_col()
        return code_col



    #
    # Column type functions
    #
    def get_text(self, not_null=False):
        parts = []
        parts.append("text")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)




    #
    # Schema functions
    #
    def get_schema_dir(self):
        # get the schema directory for the appropriate database type
        install_dir = Environment.get_install_dir()
        schema_dir = "%s/src/pyasm/search/upgrade/%s" % (install_dir, self.get_database_type().lower() )
        if not os.path.exists(schema_dir):
            raise DatabaseImplException("Schema '%s' does not exist" % schema_dir)

        return schema_dir


    def import_sql_file(self, db_resource, path):

        from pyasm.search import DbResource, DbContainer
        if isinstance(db_resource, basestring):
            database = db_resource
        else:
            database = db_resource.get_database()

        sql = DbContainer.get(db_resource)

        f = open(path, 'r')
        data = f.read()
        f.close()

        print("Importing sql to database [%s]..." % (database))
        print("   using path [%s]" % (path))

        cmds = data.split(";")
        for cmd in cmds:
            cmd = cmd.strip()
            sql.do_update(cmd)

        self.clear_table_cache()
        sql = DbContainer.get(db_resource)



    def import_schema(self, db_resource, type):
        '''import the schema of certain type to the given database'''

        # import the necessary schema
        types = ['config', type]
        
        # sthpw schema is composed of 2 files
        if db_resource == 'sthpw':
            types.insert(0, 'bootstrap')
        for schema_type in types:
            schema_dir = self.get_schema_dir()
            schema_path = "%s/%s_schema.sql" % (schema_dir, schema_type)
            if not os.path.exists(schema_path):
                # This warning occurs too often in harmless places
                #Environment.add_warning("Schema does not exist", "Schema '%s' does not exist" % schema_path)
                continue

            self.import_sql_file(db_resource, schema_path)




    def import_default_data(self, db_resource, type):
        '''import the data of certain type to the given database'''

        # import the necessary schema
        schema_dir = self.get_schema_dir()
        data_path = "%s/%s_data.sql" % (schema_dir, type)
        data_path = os.path.normpath(data_path)
        if not os.path.exists(data_path):
            #Environment.add_warning("Default data does not exist", "Data '%s' does not exist" % data_path)
            return

        self.import_sql_file(db_resource, data_path)



    #
    # Database methods for base database implementation
    #

    def set_autocommit(self, sql, flag):
        sql.conn.autocommit = flag


    def commit_on_schema_change(self):
        return False


    def has_sequences(self):
        raise DatabaseImplException("TACTIC database implementation for current database vendor does not have method has_sequences() defined.")

    def get_table_info(self, database):
        raise DatabaseImplException("Must override 'get_table_info' for [%s]" % self.vendor)


    def database_exists(self, database, host=None, port=None):
        '''@param: 
            database - if string, it's just a database name (old)
                       if DbResource, it could contain the host already
            host - can be localhost or a different server
            port - port number that the database is listen on'''
        try:
            db_resource = database
            #from pyasm.search import DbContainer, DbResource
            from sql import DbContainer, DbResource
            if isinstance(database, basestring):
                if host == None:
                    vendor = Config.get_value("database", "vendor")
                    host = Config.get_value("database", "server")
                    port = Config.get_value("database", "port")
                else:
                    vendor = self.get_database_type()
                db_resource = DbResource(database=database, host=host, vendor=vendor, port=port)
            
            cached = Container.get("Sql:database_exists:%s"%db_resource.get_key()) 
            if cached != None:
                return cached

            sql = DbContainer.get(db_resource, connect=True)
            if sql:
                if not sql.get_connection():
                    sql.connect()
            else:
                return False
            # cache it for repeated use
            Container.put("Sql:database_exists:%s"%db_resource.get_key(), True) 
        except Exception as e:
            #print("Error: ", str(e))
            return False
        else:
            return True


    def clear_table_cache(cls):
        # this relies on the __str__ method of db_resource
        key = "DatabaseImpl:table_exists"
        Container.remove(key)
        key = "DatabaseImpl:table_info"
        Container.remove(key)
        key = "DatabaseImpl:column_info"
        Container.remove(key)
    clear_table_cache = classmethod(clear_table_cache)


    def table_exists(self, db_resource, table):

        key = "DatabaseImpl:table_exists"

        cached_dict = Container.get(key)
        if cached_dict == None:
            cached_dict = {}
            Container.put(key, cached_dict)

        # this relies on the __str__ method of db_resource
        key2 = "%s:%s" % (db_resource, table)
        cached = cached_dict.get(key2)
        if cached != None:
            return cached

        table_info = self.get_table_info(db_resource)
        if table_info.has_key(table):
            exists = True
        else:
            exists = False

        cached_dict[key2] = exists

        return exists


    def get_column_types(self, db_resource, table):
        return {}



    #
    # Save point methods
    #
    def has_savepoint(self):
        return True

    def set_savepoint(self, name='save_pt'):
        '''set a savepoint'''
        if not self.has_savepoint():
            return None
        return "SAVEPOINT %s" %name

    def rollback_savepoint(self, name='save_pt', release=False):
        if not self.has_savepoint():
            return None
        stmt = "ROLLBACK TO SAVEPOINT %s"%name
        return stmt

    def release_savepoint(self, name='save_pt'):
        if not self.has_savepoint():
            return None
        stmt = "RELEASE SAVEPOINT %s"%name
        return stmt






    def get_constraints(self, db_resource, table):
        return []
      



    def handle_pagination(self, statement, limit, offset):
        return statement

    def get_id_override_statement(self, table, override=False):
        return ''

    def get_constraint(self, mode, name='', columns=[], table=None):
        if not name and table:
            if mode == 'PRIMARY KEY':
                name = '%s_pkey' %table
        return 'CONSTRAINT %s %s (%s)' %(name, mode, ','.join(columns))



    def get_regex_filter(self, column, regex, op='EQI'):
        return None

    def _get_cte_where(self, op_filters):
        '''Get the where clause for cte used in parent and child search'''
        from search import Search
        search = Search('workflow/base_keyword')
        search.add_op_filters(op_filters)
        search_stmt = search.get_statement()
       
        wheres = search_stmt.split('WHERE')
        where = wheres[-1]
        
        return where

    def get_parent_cte(self, op_filters):
        '''Postgres parent CTE'''
        where = self._get_cte_where(op_filters)

        stmt = '''WITH RECURSIVE res(parent_keyword_code, parent_key, child_keyword_code, child_key, alias, path,  depth) AS (
                   SELECT
                  r."parent_keyword_code", p1."name",
                  r."child_keyword_code", p2."name",
                        p1."alias",
                        CAST(ARRAY[r."child_keyword_code"] AS TEXT),
                  1
                 FROM "keyword_map" AS r, "base_keyword" AS p1, "base_keyword" AS p2
                 WHERE (%s)
                  
                 AND p1."code" = r."parent_keyword_code" AND p2."code" = r."child_keyword_code"
                 UNION ALL
                 SELECT
                  r."parent_keyword_code", p1."name",
                  r."child_keyword_code", p2."name",
                        p2."alias",
                        path || r."child_keyword_code",
                  ng.depth + 1
                 FROM "keyword_map" AS r, "base_keyword" AS p1, "base_keyword" AS p2,
                  res AS ng
                 WHERE r."child_keyword_code" = ng."parent_keyword_code" and depth < 4
                 AND p1."code" = r."parent_keyword_code" AND p2."code" = r."child_keyword_code"
                )

                Select * from res;'''%where

        return stmt

    def get_child_cte(self, op_filters):
        '''Postgres child CTE'''
        where = self._get_cte_where(op_filters)

        stmt = '''WITH RECURSIVE res(parent_keyword_code, parent_key, child_keyword_code, child_key, alias, path,  depth) AS (
                  SELECT
                  r."parent_keyword_code", p1."name",
                  r."child_keyword_code", p2."name",
                        p1."alias",
                        CAST(ARRAY[r."parent_keyword_code"] AS TEXT),
                  1
                 FROM "keyword_map" AS r, "base_keyword" AS p1, "base_keyword" AS p2
                 WHERE (%s)
                 AND p1."code" = r."parent_keyword_code" AND p2."code" = r."child_keyword_code"
                 UNION ALL
                 SELECT
                  r."parent_keyword_code", p1."name",
                  r."child_keyword_code", p2."name",
                        p2."alias",
                        path || r."parent_keyword_code",
                  ng.depth + 1
                 FROM "keyword_map" AS r, "base_keyword" AS p1, "base_keyword" AS p2,
                  res AS ng
                 WHERE r."parent_keyword_code" = ng."child_keyword_code" and depth < 4
                 AND p1."code" = r."parent_keyword_code" AND p2."code" = r."child_keyword_code"
                )

        Select * from res;'''%where

        return stmt

    def get_child_codes_cte(self, collection_type, search_type, parent_collection_code):
        '''Postgres collection child codes CTE'''

        var_dict = {
            'parent_collection_code': parent_collection_code,
            'collection_type': collection_type.split("/")[1],
            'search_type': search_type.split("/")[1]
        }

        stmt = '''
            WITH RECURSIVE res(parent_code, parent_key, search_code, search_key, path, depth) AS (
            SELECT
            r."parent_code", p1."name",
            r."search_code", p2."name",
                  CAST(ARRAY[r."parent_code"] AS TEXT),
             1
            FROM "%(collection_type)s" AS r, "%(search_type)s" AS p1, "%(search_type)s" AS p2
            WHERE p1."code" IN ('%(parent_collection_code)s')
            AND p1."code" = r."parent_code" AND p2."code" = r."search_code"
            UNION ALL
            SELECT
             r."parent_code", p1."name",
             r."search_code", p2."name",
                   path || r."parent_code",
             ng.depth + 1
            FROM "%(collection_type)s" AS r, "%(search_type)s" AS p1, "%(search_type)s" AS p2,
             res AS ng
            WHERE r."parent_code" = ng."search_code" and depth < 10
            AND p1."code" = r."parent_code" AND p2."code" = r."search_code"
            )
            
            Select search_code from res;
            ''' % var_dict


        return stmt
        
    def get_text_search_filter(cls, column, keywords, column_type, table=None, op="&"):
        '''default impl works with Postgres'''

        if isinstance(keywords, basestring):
            def split_keywords(keywords):
                keywords = keywords.strip()
                # The input should be stripped and single spaced. This line seems redundant, to be removed
                keywords = keywords.replace("  ", "")
                parts = keywords.split(" ")
                op_str = " %s " % op
                value = op_str.join(parts)
                return value
            
            if keywords.find("|") != -1 or keywords.find("&") != -1:
                # prevent syntax error from multiple | or &
                keywords = re.sub( r'\|+', r'|', keywords)
                keywords = re.sub( r'\&+', r'&', keywords)
                keywords = keywords.rstrip('&')
                value = keywords
                if keywords.find("|") == -1 and  keywords.find("&") == -1:
                    value = split_keywords(keywords)
            else:
                value = split_keywords(keywords)

        elif type(keywords) == types.ListType:
            # remove empty strings from the list
            keywords = filter(None, keywords)
            value = ' & '.join(keywords)
        else:
            value = str(keywords)


        # explicitly set the config in case there is an index available
        # TODO: this should be configurable
        config = 'english'

        # for multiple columns
        #coalesce(title,'') || ' ' || coalesce(body,'')
        
        # avoid syntax error
        value = value.replace("'", "''")

       

        if table:
            column = '"%s"."%s"' % (table, column)
        else:
            column = '"%s"' % column

        if column_type in ['integer','serial']:
            column = "CAST(%s AS varchar(10))" %column
        else:
            # prefix matching
            value = '%s:*'%value
        
        wheres = []
        if column_type == 'tsvector':
            wheres.append(column)
        else:
            wheres.append('''to_tsvector('%s', %s)''' % (config, column) )
        wheres.append("@@")
        wheres.append("to_tsquery('%s', '%s')" % (config, value) )

        where = " ".join(wheres)
        return where

    get_text_search_filter = classmethod(get_text_search_filter)

    
    def get_columns(cls, db_resource, table):
        '''get ordered column names'''
         # do a dummy select to get the ordered columns
        from sql import Select, DbContainer
        sql = DbContainer.get(db_resource)

        select = Select()
        select.set_database(db_resource)
        select.add_table(table)
        select.set_limit(0)
        statement = select.get_statement()
        sql.do_query(statement)

        columns = []
        for description in sql.description:
            # convert to unicode
            value = description[0].decode('utf-8')
            columns.append(value)

        return columns

    get_columns = classmethod(get_columns)




    def can_join(db_resource1, db_resource2):

        # if the hosts are difference, joins cannot happen
        host1 = db_resource1.get_host()
        host2 = db_resource2.get_host()
        if host1 != host2:
            return False

        # if the database types are differenct, joins cannot happen
        database_type1 = db_resource1.get_database_type()
        database_type2 = db_resource2.get_database_type()
        if database_type1 != database_type2:
            return False

        # if the host is the same and the database is the same, then joins
        # can happen
        database1 = db_resource1.get_database()
        database2 = db_resource2.get_database()
        if database1 == database2:
            return True

        # multi database joins are not support in Postgres or Sqlite
        if database_type1 in ["PostgreSQL", "Sqlite"]:
            return False
        if database_type2 in ["PostgreSQL", "Sqlite"]:
            return False

        # otherwise joins can happen between the two resources
        return True

    can_join = staticmethod(can_join)


    def can_search_types_join(search_type1, search_type2):
        from search import SearchType
        db_resource = SearchType.get_db_resource_by_search_type(search_type1)
        db_resource2 = SearchType.get_db_resource_by_search_type(search_type2)
        can_join = DatabaseImpl.can_join(db_resource, db_resource2)
        return can_join
    can_search_types_join = staticmethod(can_search_types_join)



    # Defines temporary column name to be used.  Only SQLServerImpl implements
    # this
    def get_temp_column_name(self):
        return ""



class BaseSQLDatabaseImpl(DatabaseImpl):
    
    def is_column_sortable(self, db_resource, table, column):

        # support -> operator
        if column.find("->"):
            parts = column.split("->")
            column = parts[0]

        from sql import DbContainer
        sql = DbContainer.get(db_resource)
        columns = sql.get_columns(table)
        if column in columns:
            return True
        else:
            return False



class SQLServerImpl(BaseSQLDatabaseImpl):
    '''Implementation for Microsoft SQL Server's SQL'''

    def get_database_type(self):
        return "SQLServer"

    def __init__(self):

        # NOTE: This will not work in mixed db cases because it assumes a
        # global single database
        self.server   = Config.get_value("database", "server")
        self.port     = Config.get_value("database", "port")
        self.user     = Config.get_value("database", "user")
        self.password = Config.get_value("database", "password")




    def get_version(self):
        from sql import DbContainer
        sql = DbContainer.get("sthpw")
        result = sql.do_query("select @@version")

        # result is [(u'Microsoft SQL Server 2008 R2 (RTM) - 10.50.1600.1 (X64) \n\tApr  2 2010 15:48:46 \n\tCopyright (c) Microsoft Corporation\n\tExpress Edition (64-bit) on Windows NT 6.0 <X64> (Build 6002: Service Pack 2) (Hypervisor)\n', )]
        version_str = result[0][0]

        parts = version_str.split(" ")
        version_parts = parts[7].split(".")
        version_parts = [int(x) for x in version_parts]
        return version_parts


    def get_create_sequence(self, sequence_name):
        #return 'CREATE SEQUENCE "%s" START WITH 1 INCREMENT BY 1 NO MAXVALUE CACHE 1' % name
        # SQL Server specific implementation.
        #postfix_len = '_id_seq'.__len__()
        #table_name_len = sequence_name.__len__() - postfix_len
        #table_name = sequence_name[0:table_name_len] 
        #print('  get_create_sequence: table_name = ', table_name)
        #return 'ALTER TABLE %s ADD %s INT IDENTITY(100, 5) ' % (table_name, sequence_name)
        #return 'ALTER COLUMN %s ADD %s INT IDENTITY(100, 5) ' % (table_name, sequence_name)
        return

    def get_sequence_name(self, table, database=None):
        # SQL Server specific implementation: use the ID column as the sequence.
        # OLD return "%s_id_seq" % table
        from pyasm.search import SearchType
        if isinstance(table, SearchType):
            search_type = table
            table = search_type.get_table()
        return table



    def get_page(self, limit=None, offset=0, table_input=0, already_in_where_clause=0):
        '''get the pagination sql based on limit and offset'''
        #
        # SQL Server implementation
        #
        return None

    def handle_pagination(self, statement, limit, offset):
        '''specific method to handle MS SQL Server's pagination'''

        if limit == None:
            return statement

        # SQL Server implementation
        # 
        # Example:
        # SELECT * from (SELECT TOP 100 *, 
        #        ROW_NUMBER() over (ORDER BY id) as _tmp_spt_rownum FROM
        # [tblCatalogCrossReference]  WHERE code='abc'
        #   ) tmp_spt_table 
        # WHERE tmp_spt_table._tmp_spt_rownum between (5) and (10)
        start = offset + 1
        end = start + int(limit) - 1
        # one can set the limit to be 0 to return 0 row back
        if end < start and limit > 0:
            raise DatabaseImplException('start [%s] must be larger than end [%s] for limit' %(start, end))
        #order_by = ''
        #if order_bys:
        #    order_by = "ORDER BY %s" % ", ".join( order_bys )
        tmp_col = self.get_temp_column_name()
        page = "tmp_spt_table.%s BETWEEN (%s) AND (%s)" % (tmp_col, start, end)

        statement = "SELECT * FROM ( \
                     %s ) tmp_spt_table \
                     WHERE %s" % (statement, page)
        return statement

    def get_id_override_statement(self, table, override=True):
        '''SQL Server needs to manually turn on an off the auto id generation feature'''
        if override:
            return "SET IDENTITY_INSERT %s ON" % table
        else:
            return "SET IDENTITY_INSERT %s OFF" % table




    #
    # Column methods
    #
    def get_boolean(self, not_null=False):
        parts = []
        parts.append("bit")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)

    def get_serial(self, not_null=False):
        parts = []
        # For SQL Server, replaced "serial" type with "identity".
        # create table "hi" ("colA" int, "id" int identity(1,1) primary key("id") );
        # 
        parts.append("int identity(1,1)")
        return " ".join(parts)


    def get_int(self, length=4, not_null=False):
        """
        http://technet.microsoft.com/en-us/library/cc917573.aspx

        If the integer is from 1 through 255, use tinyint.
        If the integer is from -32768 through 32767, use smallint.
        If the integer is from -2,147,483,648 through 2,147,483,647 use int.
        If you require a number with decimal places, use decimal. Do not use float or real, because rounding may occur (Oracle NUMBER and SQL Server decimal do not round).
        If you are not sure, use decimal; it most closely resembles Oracle NUMBER data type.

        """
        parts = []
        parts.append("int")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)

    def get_text(self, not_null=False):
        parts = []
        parts.append("varchar(max)")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_varchar(self, length=256, not_null=False):
        if not length:
            length = 256

        if length == -1:
            length = 'max'
        parts = []
        parts.append("varchar(%s)" % length)
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)

    def get_nvarchar(self, length=256, not_null=False):
        assert length
        if length == -1:
            length = 'max'
        parts = []
        parts.append("nvarchar(%s)" % length)
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)

    def get_timestamp(self, default="now", not_null=False, timezone=False):
        # SQL Server implementation.
        parts = []
        if timezone:
            parts.append("datetimeoffset(6)")
        else:
            parts.append("datetime2(6)")

        if default:
            if default == "now":
                parts.append("DEFAULT(%s)" % self.get_timestamp_now())
            else:
                parts.append("DEFAULT(%S)" % default)

        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_timestamp_now(self, offset=None, type=None, op='+'):
        # SQL Server implementation.

        if not type:
            type = 'day'
        
        if offset:
            # Postgres: parts.append("'%s %s'::interval" % (offset, type) )
            # Postgres: eg. now() + '10 hour'::interval

            # SQL Server: DATEADD(hour, +10, CURRENT_TIMESTAMP)
            part = "DATEADD(%s, %s%s, GETDATE())" % (type, op, offset) 
        else:
            part = "GETDATE()"
        return part



    def get_json(self, not_null=False):
        raise Exception("JSON Type not supported yet")

    
    #
    # Sequence methods for SQL Server
    #
    def has_sequences(self):
        return True

    def get_nextval(self, sequence):
        return '"%s".nextval' % sequence

    def get_currval(self, sequence):
        # IDENT_CURRENT returns the last identity value
        # generated for a specified table[
        return 'SELECT IDENT_CURRENT(\'' + sequence + '\')'

    def get_currval_select(self, sequence):
        # IDENT_CURRENT returns the last identity value
        # generated for a specified table[
        return 'SELECT IDENT_CURRENT(\'' + sequence + '\')'

    def get_nextval_select(self, sequence):
        # In Postgres, when a table is created, currval is undefined and nextval is 1.
        # SQL Server doesn't have a concept of nextval.
        # When the table is created, the currval *is already 1*, 
        # and so nextval becomes 2.  This poses a problem.
        # The solution is to check if
        # ident_current('table_name') = 1 then just return 1.

        cmd  = "declare @cur_id int;"
        cmd += "select @cur_id = ident_current('" + sequence + "');"
        cmd += "if @cur_id = 1"
        cmd += "  select @cur_id;"
        cmd += "else"
        cmd += "  select @cur_id + 1;"
        return cmd

    def get_setval_select(self, sequence, num):
        # Set the current identity value for the specified table.
        cmd = "DBCC CHECKIDENT ('" + sequence + "', RESEED, " + str(num) + ");"
        return cmd

    # Method to build and return an SQL statement that can be run to reset the ID sequence for a table to a number
    # that is one greater than the highest index found in the given table.  NOTE: this ASSUMES that there are rows
    # in the table to provide a MAX id value from.  TODO: provide handling for a table with no data rows.
    def get_reset_table_sequence_statement(self, table, database=None):

        from sql import DbContainer
        sql = DbContainer.get(database)

        query = "SELECT MAX(id) + 1 FROM %s ;" % table
        result = sql.do_query(query)
        max_id = result[0][0]

        reset_seq_sql = "ALTER SEQUENCE %s_id_seq RESTART WITH %d ;" % (table, max_id)
        return reset_seq_sql


    #
    # Regular Expressions
    # 
    def get_regex_filter(self, column, regex, op='EQI'):
        if op == 'EQI':
            op = 'LIKE'
            column = 'lower(CAST("%s" AS varchar(max)))' %column
            regex = "lower('%%%s%%')"%regex
        elif op == 'EQ':
            op = 'LIKE'
            regex = "'%%%s%%'" %regex
        elif op == 'NEQI':
            op = 'NOT LIKE'
            regex = "lower('%%%s%%')"%regex
        elif op == 'NEQ':
            op = 'NOT LIKE'
            regex = "'%%%s%%'" %regex
        else:
            raise SetupException('Invalid op [%s]. Try EQ, EQI, NEQ, or NEQI' %op)
            
        return "%s %s %s" %(column, op, regex)


    def get_text_search_filter(cls, column, keywords, column_type, table=None, op="&"):
        '''When Full Text Index is created in the db for the table, it works with SQLServer 2008 and above'''
        if isinstance(keywords, basestring):
            value = keywords
        elif type(keywords) == types.ListType:
            # remove empty strings from the list
            keywords = filter(None, keywords)
            value = " ".join(keywords)
        else:
            value = str(keywords)

        
        # avoid syntax error
        value = value.replace("'", "''")

       

        if table:
            column = '"%s"."%s"' % (table, column)
        else:
            column = '"%s"' % column

        """
        if column_type in ['integer','serial']:
            column = "CAST(%s AS varchar(10))" %column
       
        """
        wheres = []

        # op & will translate to AND, | to OR if we use CONTAINS() in the future
        # use FREETEXT() or CONTAINS(), CONTAINS() takes OR AND operator
        wheres.append("FREETEXT(%s, '%s')" % (column, value) )

        where = " ".join(wheres)
        return where

    get_text_search_filter = classmethod(get_text_search_filter)


    def get_parent_cte(self,  op_filters):
        '''SQLServer parent CTE'''
        where = self._get_cte_where(op_filters)

        stmt = '''WITH res(parent_keyword_code, parent_key, child_keyword_code, child_key, alias, path,  depth) AS (
                  SELECT
                  r."parent_keyword_code", p1."name",
                  r."child_keyword_code", p2."name",
                        p1."alias",
                        CAST(r."child_keyword_code" AS varchar(256)),
                  1
                 FROM "keyword_map" AS r, "base_keyword" AS p1, "base_keyword" AS p2
                 WHERE (%s)
                 AND p1."code" = r."parent_keyword_code" AND p2."code" = r."child_keyword_code"
                 UNION ALL
                 SELECT
                  r."parent_keyword_code", p1."name",
                  r."child_keyword_code", p2."name",
                        p2."alias",
                        CAST ((path + ' > ' + r."child_keyword_code") AS varchar(256)),
                  ng.depth + 1
                 FROM "keyword_map" AS r, "base_keyword" AS p1, "base_keyword" AS p2,
                  res AS ng
                 WHERE r."child_keyword_code" = ng."parent_keyword_code" and depth < 5
                 AND p1."code" = r."parent_keyword_code" AND p2."code" = r."child_keyword_code"
                )

        Select * from res;'''%where

        return stmt

    def get_child_cte(self, op_filters):
        '''SQLServer child CTE'''
        where = self._get_cte_where(op_filters)

        stmt = '''WITH res(parent_keyword_code, parent_key, child_keyword_code, child_key, alias, path,  depth) AS (
                  SELECT
                  r."parent_keyword_code", p1."name",
                  r."child_keyword_code", p2."name",
                        p1."alias",
                        CAST(r."parent_keyword_code" AS varchar(256)),
                  1
                 FROM "keyword_map" AS r, "base_keyword" AS p1, "base_keyword" AS p2
                 WHERE ( %s )
                    
                 AND p1."code" = r."parent_keyword_code" AND p2."code" = r."child_keyword_code"
                 UNION ALL
                 SELECT
                  r."parent_keyword_code", p1."name",
                  r."child_keyword_code", p2."name",
                        p2."alias",
                        CAST((path + ' > ' + r."parent_keyword_code") AS varchar(256)),
                  ng.depth + 1
                 FROM "keyword_map" AS r, "base_keyword" AS p1, "base_keyword" AS p2,
                  res AS ng
                 WHERE r."parent_keyword_code" = ng."child_keyword_code" and depth < 10
                 AND p1."code" = r."parent_keyword_code" AND p2."code" = r."child_keyword_code"
                )

        Select * from res;'''%where

        return stmt

    def get_child_codes_cte(self, collection_type, search_type, parent_collection_code):
        '''SQLServer collection child codes CTE'''

        var_dict = {
            'parent_collection_code': parent_collection_code,
            'collection_type': collection_type.split("/")[1],
            'search_type': search_type.split("/")[1]
        }

        stmt = '''
            WITH res(parent_code, parent_key, search_code, search_key, path, depth) AS (
            SELECT
            r."parent_code", p1."name",
            r."search_code", p2."name",
                  CAST(r."parent_code" AS varchar(256)),
             1
            FROM "%(collection_type)s" AS r, "%(search_type)s" AS p1, "%(search_type)s" AS p2
            WHERE p1."code" IN ('%(parent_collection_code)s')
            AND p1."code" = r."parent_code" AND p2."code" = r."search_code"
            UNION ALL
            SELECT
             r."parent_code", p1."name",
             r."search_code", p2."name",
                   CAST((path + ' > ' + r."parent_code") AS varchar(256)),
             ng.depth + 1
            FROM "%(collection_type)s" AS r, "%(search_type)s" AS p1, "%(search_type)s" AS p2,
             res AS ng
            WHERE r."parent_code" = ng."search_code" and depth < 10
            AND p1."code" = r."parent_code" AND p2."code" = r."search_code"
            )
            
            Select search_code from res;
            ''' % var_dict

        return stmt

    def process_date(self, value):
        '''SQL Server process date str to work with db before commit'''
        lower_value = ''
        if isinstance(value, datetime.datetime):
            value = str(value)
        if not value:
            pass
        else:
            lower_value = value.lower()
            if value == "NOW":
                value = "getdate()"
            # this is now called in commit() but as a precaution 
            elif not lower_value.startswith("convert") and not lower_value.startswith("getdate") and not lower_value.startswith("dateadd") :
                if value == 'NULL':
                    pass
                else:
                    # TODO:  condensed to process + or - 
                    if re.search(r"(\s\+\d{4})", value):
                        # add : so it becomes +00:00
                        parts = value.split(' +')
                        parts[-1] = '%s:%s' %(parts[-1][0:2], parts[-1][2:4])
                        value = '%s +%s'%(parts[0], parts[1])
                    elif re.search(r"(\s-\d{4})", value):
                        # add : so it becomes -00:00
                        parts = value.split(' -')
                        parts[-1] = '%s:%s' %(parts[-1][0:2], parts[-1][2:4])
                        value = '%s -%s'%(parts[0], parts[1])
                    value = "convert(datetime2, '%s', 0)" % value 
        return value
    #
    # Type process methods
    #
    def process_value(self, name, value, column_type="varchar"):
        ''' the majority of the value mod is done in process_date()'''
        if column_type in ['timestamp','datetime','datetime2']:
            # for straight sql statement conversion skipping commit
            if value == "NOW":
                value = "getdate()"
            quoted = False
            """
            lower_value = ''
            if isinstance(value, datetime.datetime):
                pass
            elif not value:
                pass
            else:
                lower_value = value.lower()
            
                if value == "NOW":
                    value = "getdate()"
                    #return {"value": value, "quoted": quoted}
                # FIXME: this is implemented this way because set_value 
                # can be called twice.  This method should called from commit
                # and not set_value
                elif not lower_value.startswith("convert") and not lower_value.startswith("getdate") and not lower_value.startswith("dateadd") :
                    if value == 'NULL':
                        pass
                    else:
                        # TODO:  condensed to process + or - 
                        if re.search(r"(\s\+\d{4})", value):
                            # add : so it becomes +00:00
                            parts = value.split(' +')
                            parts[-1] = '%s:%s' %(parts[-1][0:2], parts[-1][2:4])
                            value = '%s +%s'%(parts[0], parts[1])
                        elif re.search(r"(\s-\d{4})", value):
                            # add : so it becomes -00:00
                            parts = value.split(' -')
                            parts[-1] = '%s:%s' %(parts[-1][0:2], parts[-1][2:4])
                            value = '%s -%s'%(parts[0], parts[1])
                        value = "convert(datetime2, '%s', 0)" % value
            """    
            return {"value": value, "quoted": quoted}

          


        elif column_type in ['uniqueidentifier'] and value == "NEWID":
            value = "newid()"
            quoted = False
            return {"value": value, "quoted": quoted}




    #
    # Database methods
    # 
    def _get_db_info(self, db_resource):
        ''' get the database info from the config file'''
        if isinstance(db_resource, DbResource):
            host = db_resource.get_host()
            user = db_resource.get_user()
            password = db_resource.get_password()
            port = db_resource.get_port()
        else:
            host = Config.get_value("database", "server")
            user = Config.get_value("database", "user")
            password = Config.get_value("database", "password")
            port = Config.get_value("database", "port")


        parts = []
        host_str ="-S %s" % host 
        if port:
            host_str = '%s,%s'%(host_str, port)
        parts.append(host_str)
        parts.append("-U %s" % user)
        parts.append("-P %s" % password)
        parts.append("-p %s" % port)

        
        return " ".join(parts)


    def create_database(self, database):
        '''create a database.  This is done by a system command'''
        
        # if the database already exists, do nothing
        if self.database_exists(database):
            return

        if not isinstance(database, basestring):
            database = database.get_database()

        # TODO: Retrieve server, username, password from TACTIC config file.
        # eg.  sqlcmd -S localhost -U tactic -P south123paw -d sthpw -Q "create database test1"
        # note: The database we are connecting to must be 'sthpw'
        create_SQL_arg = '"CREATE DATABASE ' + database + '"'
        create = 'sqlcmd -S %s,%s -U %s -P %s -Q %s' % \
                 (self.server, self.port, self.user, self.password, create_SQL_arg)
        cmd = os.popen(create)
        result = cmd.readlines()
        if not result:
            print("No output from sql command to create db [%s], assumed success" % database)
            cmd.close()
            return
            #raise Exception("Error creating database '%s'" % database)
        cmd.close()

        if result[0].find("already exists") != -1:
            print("already exists")
            print("  Try deleting C:\Program Files\Microsoft SQL Server\MSSQL10_50.SQLEXPRESS\MSSQL\DATA\<database_name>.mdf")
        else:
            print("no returned result from database creation (sqlcmd)")


    def drop_database(self, db_resource):
        '''remove a database in SQL Server. Note this is a very dangerous
        operation.  Use with care.'''
        # if the database does not exist, do nothing
        #if not database_exists(database):
        #    return
        from sql import DbResource, DbContainer
        if DbResource.is_instance(db_resource):
            database = db_resource.get_database()
        else:
            database = db_resource

  
        # TODO: Retrieve server, username, password from TACTIC config file.
        # eg.  sqlcmd -S localhost -U tactic -P south123paw -d sthpw -Q "dropdatabase test1"
        # note: The database we are connecting to must be 'sthpw'
        drop_SQL_arg = '"DROP DATABASE %s"' % (database)
        create = 'sqlcmd -S %s,%s -U %s -P %s -Q %s' % \
                 (self.server, self.port, self.user, self.password, drop_SQL_arg)
        cmd = os.popen(create)
        result = cmd.readlines()
        if not result:
            print("No output from sql command to drop db [%s], assumed success" % database)
            cmd.close()
            return
        else:
            print("Drop database: ", result)
        cmd.close()

    def get_modify_column(self, table, column, type, not_null=None):
        ''' get the statement for setting the column type '''
        # this may not return the type exacty like before like varchar is in place of
        # varchar(256) due to the column type returned from the sql impl
        statements = []
        statements.append('ALTER TABLE "%s" ALTER COLUMN "%s" %s' \
            % (table,column,type))
        if not_null == None:
            return statements
        if not_null:
            # In order to set the column to disallow NULL values,
            # we must first set any current NULL values to the empty string ''.
            statements.append('UPDATE "%s" SET "%s"=\'\' WHERE %s IS NULL' \
            % (table,column, column))

            # Now that any existing NULL values for that column are set to the empty string,
            # proceed to alter the column so that it disallows NULL values.
            statements.append('ALTER TABLE "%s" ALTER COLUMN "%s" %s NOT NULL' \
            % (table,column,type))
        else:
            statements.append('ALTER TABLE "%s" ALTER COLUMN "%s" %s' \
                % (table, column, type))
        return statements



    def import_schema(self, db_resource, type):
        '''import the schema of certain type to the given database'''


        # DEPRECATED: this shouldn't be necessary anymore as the base class
        # should be general enough

        from pyasm.search import DbResource, DbContainer
        if isinstance(db_resource, basestring):
            database = db_resource
        else:
            database = db_resource.get_database()

        sql = DbContainer.get(db_resource)


        types = ['config', type]
        if db_resource == 'sthpw':
            types.insert(0, 'bootstrap')

        for schema_type in types:
            schema_dir = self.get_schema_dir()
            schema_path = "%s/%s_schema.sql" % (schema_dir, schema_type)
            schema_path = os.path.normpath(schema_path)
            if not os.path.exists(schema_path):
                Environment.add_warning("Schema does not exist", "Schema '%s' does not exist" % schema_path)
                return
                #raise Exception("Schema '%s' does not exist" % schema_path)

            # cmd = 'psql -q %s %s < "%s"' % (self._get_db_info(database), database, schema_path)
            # TODO: Retrieve server, username, password from TACTIC config file.
            # eg.  sqlcmd -S localhost -U tactic -P south123paw -d sthpw -i c:/schema.py
            cmd = 'sqlcmd -S %s,%s -U %s -P %s -d %s -i "%s"' % \
                  (self.server, self.port, self.user, self.password, database, schema_path)

           
            print("Importing schema ...")
            print(cmd)
            os.system(cmd)
            #program = subprocess.call(cmd, shell=True)
            #print("FINSIHED importing schema")


    def import_default_data(self, db_resource, type):
        '''import the data of certain type to the given database'''

        from sql import DbResource, DbContainer
        if isinstance(db_resource, DbResource):
            database = db_resource.get_database()
        else:
            database = db_resource

        # import the necessary schema
        schema_dir = self.get_schema_dir()
        data_path = "%s/%s_data.sql" % (schema_dir, type)
        data_path = os.path.normpath(data_path)
        if not os.path.exists(data_path):
            #Environment.add_warning("Default data does not exist", "Data '%s' does not exist" % data_path)
            return

        #cmd = 'psql -q %s %s < "%s"' % (self._get_db_info(database), database, data_path)
        # TODO: Retrieve server, username, password from TACTIC config file.
        # eg.  sqlcmd -S localhost -U tactic -P south123paw -d sthpw -i c:/schema.py
        cmd = 'sqlcmd -S %s,%s -U %s -P %s -d %s -i "%s"' % \
              (self.server, self.port, self.user, self.password, database, data_path)

        print("Importing data ...")
        print(cmd)
        os.system(cmd)


    def get_table_info(self, db_resource):

        key = "DatabaseImpl:table_info"
        cache_dict = Container.get(key)
        if cache_dict == None:
            cache_dict = {}
            Container.put(key, cache_dict)

        from sql import DbContainer, Sql
        if isinstance(db_resource, Sql):
            key2 = "%s" % (db_resource.get_db_resource())
        else:
            key2 = "%s" % (db_resource)
        cache = cache_dict.get(key2)
        if cache != None:
            return cache


        from sql import Select, DbContainer
        sql = DbContainer.get(db_resource)

        statement = 'SELECT * from sys.Tables'
        results = sql.do_query(statement)
        info = {}
        for result in results:
            table = result[0]
            info[table] = table

        Container.put(key2, info)

        return info


    def get_column_info(cls, db_resource, table, use_cache=True):
        '''SQLServer: get column info like data types, is_nullable in a dict'''

        from sql import DbContainer, Sql
        if isinstance(db_resource, Sql):
            prefix = "%s" % db_resource.get_db_resource()
        else:
            prefix = "%s" % db_resource
            
        if use_cache:
            # use global cache
            if prefix.endswith(':sthpw'):
                from pyasm.biz import CacheContainer
                from pyasm.security import Site
                site = Site.get()
                if site:
                    key = "%s:sthpw_column_info" % site
                else:
                    key = "sthpw_column_info"
                cache = CacheContainer.get(key)
                if cache:
                    dict = cache.get_value_by_key("data", table)
                    if dict != None:
                        return dict

        key2 = "%s:%s" % (prefix, table)
      
        key = "DatabaseImpl:column_info"
        cache_dict = Container.get(key)
        if cache_dict == None:
            cache_dict = {}
            Container.put(key, cache_dict)
        
        if use_cache:    
            cache = cache_dict.get(key2)
            if cache != None:
                return cache

        cache = {}
        cache_dict[key2] = cache


        # get directly from the database
        from sql import DbContainer
        # get directly from the database
        if isinstance(db_resource, Sql):
            sql = db_resource
        else:
            sql = DbContainer.get(db_resource)
        query = "select column_name, data_type, \
            is_nullable, character_maximum_length from \
            information_schema.columns where table_name = '%s' \
            " % table

            #order by ordinal_position" % table
        result = sql.do_query(query)

        # convert to the proper data structure
        if len(result) > 0:
            for k in range(len(result)):
                name = result[k][0]
                data_type = result[k][1]
                is_nullable = result[k][2] == 'YES'
                size = result[k][3]
                if data_type in ['character varying', 'varchar','nvarchar']:
                    data_type = 'varchar'
                elif data_type in ['integer', 'smallint', 'int']:
                    data_type = 'integer'
                elif data_type in ['text','ntext']:
                    data_type = "text"
                elif data_type == 'boolean':
                    data_type = "boolean"
                elif data_type == 'bit':
                    data_type = "boolean"

                elif data_type == 'uniqueidentifier':
                    data_type = "uniqueidentifier"
                # sqlserver handles timestamp different and is *not the same
                # timestamp from other databases
                elif data_type == 'timestamp':
                    data_type = "sqlserver_timestamp"
                elif data_type.startswith('int identity'):
                    data_type = "serial"

                elif data_type.startswith("datetime"):
                    data_type = "timestamp"
                # for time with/wihtout time zone
                elif data_type.startswith("time "):
                    data_type = "time"

                info_dict = {'data_type': data_type, 'nullable': is_nullable, 'size': size}
                cache[name] = info_dict


        return cache

    get_column_info = classmethod(get_column_info)

  

   
 

    def get_column_types(self, database, table):
        ''' get column data types. Note: can potentially get 
            character_maximum_length, numeric_precision, and udt_name '''
    
        info = self.get_column_info(database, table) 
        column_dict = {}
        for key, value in info.items():
            column_dict[key] = value.get('data_type')
        return column_dict

    def get_column_nullables(self, database, table):
        ''' get column data nullables '''
    
        info = self.get_column_info(database, table) 
        column_dict = {}
        for key, value in info.items():
            column_dict[key] = value.get('nullable')
        return column_dict 

   

    def set_savepoint(self, name='save_pt'):
        '''set a savepoint'''
        stmt = 'if @@TRANCOUNT > 0 SAVE TRANSACTION %s'%name
        return stmt
        """
        from sql import DbContainer
        sql = DbContainer.get(database)
        query = 'SAVE TRANSACTION %s'%name
        sql.execute(query)
        """

    def rollback_savepoint(self, name='save_pt', release=False):
        stmt = "ROLLBACK TRANSACTION %s"%name
        return stmt

    def release_savepoint(self, name='save_pt'):
        # does not apply in MS SQL
        return None

    def get_temp_column_name(self):
        return "_tmp_spt_rownum"

    def get_columns(cls, db_resource, table):
        '''SQLServer get ordered column names'''
        
        from sql import DbContainer
        sql = DbContainer.get(db_resource)

        statement = "EXEC sp_columns @table_name = '%s'"%table
        results = sql.do_query(statement)

        columns = []
        if len(results) > 0:
            for k in range(len(results)):
                name = results[k][3]
                columns.append(name)


        # remove temp columns
        columns = cls.remove_temp_column(columns, sql) 
        

        return columns

    get_columns = classmethod(get_columns)

    def remove_temp_column(cls, columns, sql):
        # SQL Server temp columns are put in by ROW_NUMBER()
        # in database_impl.handle_pagination()
        impl = sql.get_database_impl()
        temp_column_name = impl.get_temp_column_name()
        if temp_column_name and temp_column_name in columns:
            columns.remove(temp_column_name)

        return columns

    remove_temp_column = classmethod(remove_temp_column)




class PostgresImpl(BaseSQLDatabaseImpl):
    '''Implementation for PostgreSQL'''

    def get_database_type(self):
        return "PostgreSQL"

    def get_version(self):
        from sql import DbContainer
        sql = DbContainer.get("sthpw")
        result = sql.do_query("select version()")
        version_str = result[0][0]

        #eg. result = PostgreSQL 8.2.11 on i386-redhat-linux-gnu, compiled by GCC gcc (GCC) 4.1.2 20070925 (Red Hat 4.1.2-33)
        #eg. result = PostgreSQL 9.1.3, compiled by Visual C++ build 1500, 64-bit 
        parts = version_str.split(" ")
        version_parts = parts[1].split(".")
        version_parts = [int(re.split('[\.,]',x)[0]) for x in version_parts]
        return version_parts



    def get_page(self, limit=None, offset=0, table_input=0, already_in_where_clause=0):
        '''get the pagination sql based on limit and offset'''
        if limit == None:
            return None

        parts = []
        parts.append("LIMIT %s" % limit)
        if offset:
            parts.append("OFFSET %s" % offset)
        return " ".join(parts)


    #
    # Column methods
    #
    def get_boolean(self, not_null=False):
        parts = []
        parts.append("boolean")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)

    def get_serial(self, length=4, not_null=False):
        parts = []
        parts.append("serial")
        return " ".join(parts)


    def get_int(self, length=4, not_null=False):
        parts = []
        parts.append("int%s" % length)
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_float(self, not_null=False):
        parts = []
        parts.append("float")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_text(self, not_null=False):
        parts = []
        parts.append("text")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_char(self, length=256, not_null=False):
        assert length
        parts = []
        parts.append("char(%s)" % length)
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_varchar(self, length=256, not_null=False):
        if not length:
            length = 256

        if length in [-1, 'max']:
            return self.get_text(not_null=not_null)
        parts = []
        parts.append("varchar(%s)" % length)
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_nvarchar(self, length=256, not_null=False):
        return self.get_varchar(length=length, not_null=not_null)

    def get_timestamp(self, default=None, not_null=False, timezone=False):
        parts = []
        if timezone:
            parts.append("timestamp with time zone")
        else:
            parts.append("timestamp")
        if default:
            if default == "now":
                parts.append("DEFAULT %s" % self.get_timestamp_now())
            else:
                parts.append("DEFAULT %s" % default)

        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_timestamp_now(self, offset=None, type=None, op='+'):
        parts = []
        parts.append("now()")
        if offset:
            if not type:
                type = "day"
            parts.append("'%s %s'::interval" % (offset, type) )
        op = ' %s ' % op
        return op.join(parts)



    def get_json(self, not_null=False):
       parts = []
       parts.append("jsonb")
       if not_null:
           parts.append("NOT NULL")
       return " ".join(parts)


    
    #
    # Sequence methods for Postgres
    #
    def has_sequences(self):
        return True

    def get_create_sequence(self, name):
        return 'CREATE SEQUENCE "%s" START WITH 1 INCREMENT BY 1 NO MAXVALUE CACHE 1' % name

    def get_sequence_name(self, table, database=None):
        from pyasm.search import SearchType
        if isinstance(table, SearchType):
            search_type = table
            table = search_type.get_table()
            id_col = search_type.get_search_type_id_col()
            if id_col:
                return "%s_%s_seq" % (table, id_col)

        return "%s_id_seq" % table


    def get_nextval(self, sequence):
        return '"%s".nextval' % sequence

    def get_currval(self, sequence):
        return '"%s".currval' % sequence

    def get_currval_select(self, sequence):
        return "select currval('\"%s\"')" % sequence

    def get_nextval_select(self, sequence):
        return "select nextval('\"%s\"')" % sequence

    def get_setval_select(self, sequence, num):
        return "select setval('\"%s\"', %s)" % (sequence, num)


    # Method to build and return an SQL statement that can be run to reset the ID sequence for a table to a number
    # that is one greater than the highest index found in the given table.  NOTE: this ASSUMES that there are rows
    # in the table to provide a MAX id value from.  TODO: provide handling for a table with no data rows.
    def get_reset_table_sequence_statement(self, table, database=None):

        from sql import DbContainer
        sql = DbContainer.get(database)

        query = "SELECT MAX(id) + 1 FROM %s ;" % table
        result = sql.do_query(query)
        max_id = result[0][0]

        reset_seq_sql = "ALTER SEQUENCE %s_id_seq RESTART WITH %d ;" % (table, max_id)
        return reset_seq_sql


    #
    # Regular Expressions
    # 
    def get_regex_filter(self, column, regex, op='EQI'):
        if op == 'EQI':
            op = '~*'
        elif op == 'EQ':
            op = '~'
        elif op == 'NEQI':
            op = '!~*'
        elif op == 'NEQ':
            op = '!~'
        else:
            raise SetupException('Invalid op [%s]. Try EQ, EQI, NEQ, or NEQI' %op)
            
        return "\"%s\" %s '%s'" %(column, op, regex)




    #
    # Type process methods
    #
    def process_value(self, name, value, column_type="varchar"):
        '''Postgres process_value'''
        if column_type == 'timestamp':
            quoted = True
            if value == "NOW":
                value = "now()"
                return {"value": value, "quoted": quoted}

        elif column_type == 'boolean':
            quoted = False
            if value in ['true', 'True', 1 ,'1', True]:
                value = True
            else:
                value = False
            return {"value": value, "quoted": quoted}

        elif column_type in ['decimal', 'numeric']:
            quoted = False
            if isinstance(value, basestring):
                value = value.replace("Decimal('", '')
                value = value.replace("')", '')
            return {"value": value, "quoted": quoted}


    #
    # Database methods
    # 
    def _get_db_info(self, db_resource, host=None, port=None):
        ''' get the database info from the config file if db_resource object is not given. e.g. during install'''
        from sql import DbResource
        if isinstance(db_resource, DbResource):
            host = db_resource.get_host()
            user = db_resource.get_user()
            password = db_resource.get_password()
            port = db_resource.get_port()
        else:
            if not host:
                host = Config.get_value("database", "server")
            user = Config.get_value("database", "user")
            password = Config.get_value("database", "password")
            if not port:
                port = Config.get_value("database", "port")


        # put in some defaults
        if not host:
            host = '127.0.0.1'
        if not user:
            user = 'postgres'
        if not port:
            port = '5432'

        parts = []
        parts.append("-h %s" % host)
        parts.append("-U %s" % user)
        if port:
            parts.append("-p %s" % port)

        return " ".join(parts)

  


    def create_database(self, database):
        '''create a database.  This is done by a system command'''
        
        # if the database already exists, do nothing
        if self.database_exists(database):
            return

        if not isinstance(database, basestring):
            database = database.get_database()

        from pyasm.search import DbResource
        db_resource = DbResource.get_default(database)

        create = 'createdb %s -E UNICODE "%s"' % (self._get_db_info(db_resource), database)
        cmd = os.popen(create)
        result = cmd.readlines()
        # Psql 8.3 doesn't have outputs on creation
        if not result:
            print("no output, assumed success")
            return
            #raise Exception("Error creating database '%s'" % database)
        cmd.close()
        
        

        if result[0] == "CREATE DATABASE":
            print("success")
        elif result[0].endswith("already exists"):
            print("already exists")
        else:
            print("no returned result from database creation (psql 8.2+)")


    def drop_database(self, db_resource):
        '''remove a postgres database . Note this is a very dangerous
        operation.  Use with care.'''


        # if the database already exists, do nothing
        if not self.database_exists(db_resource):
            return
        from sql import DbResource, DbContainer, Sql

        if isinstance(db_resource, DbResource):
            database = db_resource.get_database()
        else:
            database = db_resource
        info = self._get_db_info(db_resource)

        database_version = Sql.get_default_database_version()
        major = database_version[0]
        minor = database_version[1] 


        # connect from the main db    
        sql = DbContainer.get('sthpw') 
        
        # try to kill the connections first
        version = '%s.%s' %(major, minor)
        if version >= '8.4':
            col_name = 'procpid'
            if version >= '9.2':
                col_name = 'pid'


            sql.do_query("""SELECT pg_terminate_backend(pg_stat_activity.%s)
            FROM pg_stat_activity WHERE pg_stat_activity.datname = '%s'"""%(col_name, database))

        print("Dropping Database [%s] ..." % database)
        """
        isolation_level = sql.conn.isolation_level
        sql.conn.set_isolation_level(0)
        sql.execute('''DROP DATABASE "%s";''' % str(database) )
        # FIXME: this creates a warning
        DbContainer.release_thread_sql()
        """

        cmds = ['dropdb']
        cmds.extend(info.split(' '))
        # has to str() to avoid unicode str
        cmds.append(str(database))

        #drop_cmd = "dropdb %s %s" % (info, database)
        #cmd = os.popen(drop_cmd, 'r')
        #result = cmd.readlines()
        #cmd.close()
        popen =  subprocess.Popen(cmds, shell=False, stdout=subprocess.PIPE)
        popen.wait()
        output = ''
        value = popen.communicate()
        if value:
            output = value[0].strip()
            if not output:
                err = value[1]
                if err:
                    output = err

        return output


    def get_modify_column(self, table, column, type, not_null=None):
        ''' get the statement for setting the column type '''
        # this may not return the type exacty like before like varchar is in place of
        # varchar(256) due to the column type returned from the sql impl
        statements = []
        statements.append('ALTER TABLE "%s" ALTER "%s" TYPE %s' \
            % (table,column,type))
        if not_null == None:
            return statements
        if not_null:
            statements.append('ALTER TABLE "%s" ALTER "%s" SET NOT NULL' \
            % (table,column))
        else:
            statements.append('ALTER TABLE "%s" ALTER "%s" DROP NOT NULL' \
                % (table,column))

        return statements




    """
    def import_default_data(self, db_resource, type):
        '''import the data of certain type to the given database'''

        from sql import DbResource, DbContainer
        if isinstance(db_resource, DbResource):
            database = db_resource.get_database()
        else:
            database = db_resource

        # import the necessary schema
        schema_dir = self.get_schema_dir()
        schema_path = "%s/%s_data.sql" % (schema_dir, type)
        if not os.path.exists(schema_path):
            if type != 'simple':
                #Environment.add_warning("Default data does not exist", "Data '%s' does not exist" % schema_path)
            return

        schema = 'psql -q %s %s < "%s"' % (self._get_db_info(db_resource), database, schema_path)
        print("Importing data ...")
        print(schema)
        os.system(schema)
    """

    def get_constraints(self, db_resource, table):
        '''Get contraints primarily UNIQUE for PostgreSQL'''
        from sql import Select, DbContainer
        constraints = []
        try:
            db = DbContainer.get(db_resource)
            statement = '''SELECT * from information_schema.table_constraints where table_name='%s';''' % table
            results = db.do_query(statement)


            # ignore Primary Key and CHECK CONSTRAINT for now
            if len(results) > 0:
                for k in range(len(results)):
                    mode = results[k][6]
                    name = results[k][2]
                    if mode in ['PRIMARY KEY', 'CHECK']:
                        continue
                    constraints.append({'mode':mode, 'name': name}) 
            
            for constraint in constraints:
                name = constraint.get('name')
                statement = '''select pg_get_indexdef(oid) from pg_class where relname='%s';''' % name
                sub_result = db.do_query(statement)
                value = sub_result[0][0]
                m = re.search(r'\((.*)\)', value, re.M)
                group =  m.group()
                columns = []
                if group:
                    columns = group.lstrip('(').rstrip(')')
                    columns = columns.split(',')
                constraint['columns'] = columns
        except Exception as e:
            print("ERROR: ", e)


        return constraints

    def get_table_info(self, db_resource):

        key = "DatabaseImpl:table_info"
        cache_dict = Container.get(key)
        if cache_dict == None:
            cache_dict = {}
            Container.put(key, cache_dict)


        from sql import DbContainer, Sql
        if isinstance(db_resource, Sql):
            key2 = "%s" % (db_resource.get_db_resource())
        else:
            key2 = "%s" % (db_resource)
        cache = cache_dict.get(key2)
        if cache != None:
            return cache

        info = {}
        cache_dict[key2] = info


        from sql import Select, DbContainer
        sql = DbContainer.get(db_resource)

        statement = '''SELECT tablename FROM pg_tables
        WHERE tablename NOT LIKE 'pg_%'
        AND tablename NOT LIKE 'sql_%'
        '''
        results = sql.do_query(statement)
        for result in results:
            table = result[0]
            info[table] = table

        #statement = '''SELECT viewname FROM pg_views
        #WHERE schemaname NOT IN ['information_schema', 'pg_catalog']
        #'''
        # or (this will not work if we define schema for projects
        statement = '''SELECT viewname FROM pg_views WHERE schemaname = 'public';'''
        results = sql.do_query(statement)
        for result in results:
            table = result[0]
            info[table] = table

        return info



    def get_column_info(cls, db_resource, table, use_cache=True):
        '''get column info like data types, is_nullable in a dict'''

        from sql import DbContainer, Sql
        if isinstance(db_resource, Sql):
            prefix = "%s" % db_resource.get_db_resource()
        else:
            prefix = "%s" % db_resource

        if use_cache:
            # use global cache
            if prefix.endswith(':sthpw'):
                from pyasm.biz import CacheContainer
                from pyasm.security import Site
                site = Site.get()
                if site:
                    key = "%s:sthpw_column_info" % site
                else:
                    key = "sthpw_column_info"
                cache = CacheContainer.get(key)
                if cache:
                    dict = cache.get_value_by_key("data", table)
                    if dict != None:
                        return dict

        key2 = "%s:%s" % (prefix, table)
      
        key = "DatabaseImpl:column_info"
        cache_dict = Container.get(key)
        if cache_dict == None:
            cache_dict = {}
            Container.put(key, cache_dict)
        
        if use_cache:    
            cache = cache_dict.get(key2)
            if cache != None:
                return cache

        cache = {}
        cache_dict[key2] = cache


        # get directly from the database
        if isinstance(db_resource, Sql):
            sql = db_resource
        else:
            sql = DbContainer.get(db_resource)
        query = "select column_name, data_type, \
            is_nullable, character_maximum_length from \
            information_schema.columns where table_name = '%s' \
            " % table

        #order by ordinal_position" % table
        result = sql.do_query(query)

        # convert to the proper data structure
       
        if len(result) > 0:
            for k in range(len(result)):
                name = result[k][0]
                data_type = result[k][1]
                is_nullable = result[k][2] == 'YES'
                size = result[k][3]
                if data_type == 'character varying':
                    data_type = 'varchar'
                elif data_type in ['integer', 'smallint']:
                    data_type = 'integer'
                elif data_type == 'text':
                    data_type = "text"
                elif data_type == 'boolean':
                    data_type = "boolean"
                elif data_type == 'jsonb':
                    data_type = "json"
                elif data_type.startswith("timestamp"):
                    data_type = "timestamp"
                # for time with/wihtout time zone
                elif data_type.startswith("time "):
                    data_type = "time"

                info_dict = {'data_type': data_type, 'nullable': is_nullable, 'size': size}
               

                cache[name] = info_dict

        return cache

    get_column_info = classmethod(get_column_info)


    

    def get_column_types(self, database, table, use_cache=True):
        ''' get column data types. Note: can potentially get 
            character_maximum_length, numeric_precision, and udt_name '''
        info = self.get_column_info(database, table) 
        column_dict = {}
        for key, value in info.items():
            column_dict[key] = value.get('data_type')
        return column_dict

    def get_column_nullables(self, database, table):
        ''' get column data nullables '''
    
        info = self.get_column_info(database, table) 
        column_dict = {}
        for key, value in info.items():
            column_dict[key] = value.get('nullable')
        return column_dict 



class OracleImpl(PostgresImpl):


    def get_database_type(self):
        return "Oracle"


    def create_database(self, database):
        '''create a database.  This is done by a system command'''
        # get the system user
        from pyasm.search import DbPasswordUtil, DbContainer
        password = DbPasswordUtil.get_password()
        statement = 'create user %s identified by %s' % (database, password)

        sql = DbContainer.get("system")
        sql.do_update(statement)

 
    def get_page(self, limit=None, offset=0):
        '''get the pagination sql based on limit and offset'''
        if limit == None:
            return ""
        # This is not used
        return "rownum between %s and %s" % (offset, offset+limit)


    def handle_pagination(self, statement, limit, offset):
        '''specific method to handle Oracle's insane pagination'''

        if limit == None:
            return statement

        # handle crazy logic to convert offset to start/end.  Note that
        # offset starts at 1 in oracle
        start = offset + 1
        end = start + limit - 1


        if offset == 0:
            page = "rownum between %s and %s" % (start, end)
            statement = "SELECT * FROM (%s) WHERE %s" % (statement, page)
        else:
            page = "spt_rownum between %s and %s" % (start, end)
            statement = "SELECT * FROM ( SELECT spt.*, rownum as spt_rownum FROM (%s ) spt ) WHERE %s" % (statement, page)

        return statement

    #
    # Sequence methods for Oracle
    #
    def has_sequences(self):
        return True

    def get_create_sequence(self, name):
        # FIXME: sequence names have quote in them.  This needs to be fixed!!!
        return 'CREATE SEQUENCE %s START WITH 1 NOMAXVALUE' % name


    def get_sequence_name(self, table, database=None):
        from pyasm.search import SearchType
        if isinstance(table, SearchType):
            search_type = table
            table = search_type.get_table()

        if database:
            return '''%s."%s_id_seq"''' % (database, table)
        else:
            return '''"%s_id_seq"''' % (table)


    # Method to build and return a PL/SQL that can be run to reset the ID sequence for a table to a number that
    # is one greater than the highest index found in the given table.  NOTE: this ASSUMES that there are rows
    # in the table to provide a MAX id value from.  TODO: provide handling for a table with no data rows.
    def get_reset_table_sequence_statement(self, table, database=None):

        template_stmt_arr = [
            '''declare''',
            '''next_val NUMBER;''',
            '''new_next_val NUMBER;''',
            '''incr NUMBER;''',
            '''highest_id NUMBER;''',
            '''v_code NUMBER;''',
            '''v_errmsg VARCHAR2(64);''',
            '''BEGIN''',
            '''SAVEPOINT start_transaction;''',
            '''    -- get the max PK from the table that's using the sequence''',
            '''    select max("id") into highest_id from [DB]"[table]";''',
            '''    -- then read nextval from the sequence''',
            '''    EXECUTE IMMEDIATE 'select [DB]"[table]_id_seq".nextval from dual' into next_val;''',
            '''    DBMS_OUTPUT.PUT_LINE('[DB]"[table]_id_seq" next_val obtained is ' || next_val);''',
            '''    -- calculate the desired next increment for the sequence''',
            '''    -- incr := highest_id - next_val + 1;   -- ORIGINAL LINE THAT ADDS ONE TOO MANY''',
            '''    incr := highest_id - next_val ;''',
            '''    EXECUTE IMMEDIATE 'ALTER SEQUENCE [DB]"[table]_id_seq" increment by ' || incr;''',
            '''    EXECUTE IMMEDIATE 'select [DB]"[table]_id_seq".nextval from dual' into new_next_val;''',
            '''    EXECUTE IMMEDIATE 'ALTER SEQUENCE [DB]"[table]_id_seq" increment by 1';''',
            '''    DBMS_OUTPUT.PUT_LINE('[DB]"[table]_id_seq" new_next_val is ' || new_next_val);''',
            '''commit;''',
            '''EXCEPTION''',
            '''    WHEN OTHERS THEN''',
            '''        ROLLBACK to start_transaction;''',
            '''    DBMS_OUTPUT.PUT_LINE('Error code ' || v_code || ': ' || v_errmsg);''',
            '''end;''',
        ]

        template_stmt = '\n'.join( template_stmt_arr )
        pl_sql_stmt = template_stmt.replace("[table]", table)

        if database:
            pl_sql_stmt = pl_sql_stmt.replace("[DB]", "%s." % database)
        else:
            pl_sql_stmt = pl_sql_stmt.replace("[DB]", "")

        return pl_sql_stmt


    #
    # Column methods
    #
    def get_boolean(self, not_null=False):
        parts = []
        # No boolean in Oracle??!??
        parts.append("CHAR(1)")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)

    def get_serial(self, length=4, not_null=False):
        '''oracle does not have auto serial'''
        parts = []
        parts.append("NUMBER")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)

    def get_int(self, length=4, not_null=False):
        parts = []
        parts.append("NUMBER")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)

    def get_text(self, not_null=False):
        parts = []
        parts.append("CLOB")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_varchar(self, length=256, not_null=False):
        if not length:
            length = 256

        if length in [-1, 'max']:
            return self.get_text(not_null=not_null)
        parts = []
        parts.append("VARCHAR2(%s)" % length)
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_timestamp(self, default="now", not_null=False, timezone=False):
        parts = []
        parts.append("TIMESTAMP")

        if default:
            if default == "now":
                parts.append("DEFAULT %s" % self.get_timestamp_now())
            else:
                parts.append("DEFAULT %s" % default)

        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)

    def get_timestamp_now(self, offset=None, type=None, op='+'):
        parts = []
        parts.append("SYSTIMESTAMP")
        if offset:
            if not type:
                type = "day"
            parts.append("INTERVAL '%s' %s" % (offset, type))
        op = ' %s ' % op
        return op.join(parts)


    #
    # Sequence methods -- FIXME: quotes around sequence identifier needed?
    #
    def get_nextval(self, sequence):
        return '%s.nextval' % sequence

    def get_currval(self, sequence):
        return '%s.currval' % sequence

    def get_currval_select(self, sequence):
        return 'select %s.currval from dual' % sequence

    def get_nextval_select(self, sequence):
        return 'select %s.nextval from dual' % sequence
    
    def get_setval_select(self, sequence):
        return None
        #return 'select %s.setval from dual' % sequence

    #
    # Regular expressions
    #
    def get_regex_filter(self, column, regex, op='EQI'):
        not_like = False
        parts = []
        if op == 'EQI':
            op = 'i'
        elif op == 'EQ':
            op = 'c'
        elif op == 'NEQI':
            op = 'i'
            parts.append("NOT")
        elif op == 'NEQ':
            op = 'c'
            parts.append("NOT")
        else:
            raise SetupException('Invalid op [%s]. Try EQ, EQI, NEQ, or NEQI' %op)
        expr = "REGEXP_LIKE(\"%s\", '%s', '%s')" % (column, regex, op)
        parts.append(expr)
        return " ".join(parts)




    #
    # Database methods
    #
    info = {}

    def get_table_info(self, database):
        # FIXME: this function needs to handle DbResource class

        #key = "Oracle:table_info:%s" % database
        #info = Container.get(key)

        # FIXME: this doesn't work too well as it gets called once per session
        # If the schema changes, TACTIC needs to be restarted

        info = OracleImpl.info.get(database)

        if not info:

            from pyasm.search import DbResource, DbContainer
            if isinstance(database, basestring):
                database_name = database
            else:
                database_name = database.get_database()

            from sql import Select, DbContainer
            sql = DbContainer.get(database)
            select = Select()
            select.set_database(sql)
            select.add_table("ALL_TABLES")
            select.add_column("TABLE_NAME")
            select.add_where('''"OWNER" in ('%s','%s')''' % (database_name, database_name.upper()))

            statement =  select.get_statement()
            results = sql.do_query(statement)
            #print(results)

            info = {}
            for result in results:
                table_name = result[0]
                if table_name.startswith("BIN$"):
                    continue
                table_info = {}
                info[table_name] = table_info

            #Container.put(key, info)
            OracleImpl.info[database] = info

        return info

    #
    # Table definitions
    #
    def get_column_description(self, database, table):
        '''NOTE: this is not very useful in postgres, use get_column_info()
           instead'''
        from sql import DbContainer, Sql, Select
        sql = DbContainer.get(database)

        select = Select()
        select.set_database(sql)
        select.add_table(table)
        select.add_limit(0)
        query = select.get_statement()
        result = sql.do_query(query)

        description = sql.get_table_description()
        return description

    def get_column_info(self, database, table):
        '''get column info like data types and nullable'''
        dict = {}


        key = "OracleImpl:column_info:%s:%s" % (database, table)
        description = Container.get(key)
        if not description:
            description = self.get_column_description(database, table)
            Container.put(key, description)

        import cx_Oracle
        for item in description:
            name = item[0]
            data_type = item[1]
            size = item[2]
            nullable = bool(item[6])
            # FIXME: for whatever reason, type(data_type) returns <type 'type'>
            # and isinstance(data_type, cx_Oracle.XXX) always returns false
            #if isinstance(data_type,cx_Oracle.CLOB):
            #    data_type = "text"
            #elif isinstance(data_type,cx_Oracle.STRING):
            #    data_type = "character"
            #elif isinstance(data_type,cx_Oracle.NUMBER):
            #    data_type = "integer"

            data_type_str = str(data_type)
            if data_type_str == "<type 'cx_Oracle.CLOB'>":
                data_type = "text"
            elif data_type_str == "<type 'cx_Oracle.STRING'>":
                data_type = "varchar"
            elif data_type_str == "<type 'cx_Oracle.FIXED_CHAR'>":
                # NOTE:big assumption here that character of size 1 are booleans
                if size == 1:
                    data_type = "boolean"
                    #??
                    data_type = "string"
                else:
                    data_type = "string"
            elif data_type_str == "<type 'cx_Oracle.NUMBER'>":
                data_type = "integer"
            elif data_type_str == "<type 'cx_Oracle.TIMESTAMP'>":
                data_type = "timestamp"
            elif data_type_str == "<type 'cx_Oracle.DATETIME'>":
                data_type = "timestamp"
            else:
                raise DatabaseImplException("Unknown type [%s] for column [%s] in table [%s]" % (data_type_str, name, table) )

            info_dict = {'data_type': data_type, 'nullable': nullable,
                'size': size}
            dict[name] = info_dict


        return dict

    def get_column_types(self, database, table):
        ''' get column data types in a dict '''
        
        return super(OracleImpl, self).get_column_types(database, table)

    # schema manipulation
    def get_modify_column(self, table, column, type, not_null=False):
        ''' get the list of statements for setting the column type '''
        # this may not return the type exacty like before like varchar is in place of
        # varchar(256) due to the column type returned from the sql impl
        statement = 'ALTER TABLE "%s" MODIFY "%s" %s' % (table,column,type)
        if not_null:
            statement = '%s NOT NULL' %statement
        return [statement]
    # 
    # Sql manipulation functions
    #
    # This deals with Oracles absurdly low 4000 byte limit on sql statements
    #
    def preprocess_sql(self, data, unquoted_cols):
        self.plsql_vars = []

        values = data.values()
        cols = data.keys()
        for i in range(0, len(cols)):

            # plsql code to get around oracles stupid 4000 byte limit
            value = values[i]
            if value and type(value) in types.StringTypes and len(value) > 4000:
                # remember this column
                varname = "%s__var" %cols[i]
                self.plsql_vars.append((varname, value))
                value = varname

                data[cols[i]] = value

                if cols[i] not in unquoted_cols:
                    unquoted_cols.append(cols[i])


    def postprocess_sql(self, statement):
        from sql import Sql
        if not self.plsql_vars:
            return statement

        expr = []

        # inspired from:
        # http://www.uaex.edu/srea/Huge_Strings_Using_LOBs.htm

        l_varname = []
        # do 16k chunks
        chunk_length = 16*1024

        # pl/sql code to get aroung oracles stupid 4000 byte limit
        expr.append("declare")
        for varname, value in self.plsql_vars:
            length = len(value)
            if length >= 30*1024:
                expr.append("tmp varchar2(%s) := '';" % chunk_length)
                expr.append("%s clob := empty_clob;" % varname)
                l_varname.append((varname, value))
            else:
                expr.append("%s varchar2(%s) := %s;" % (varname, length, Sql.quote(value)))

        expr.append("begin")


        for varname, value in l_varname:

            chunks = int(float(len(value)) / chunk_length) + 1

            expr.append("dbms_lob.createTemporary(%s, true);" % varname)
            expr.append("dbms_lob.open(%s, dbms_lob.lob_readwrite);" % varname)

            # add to the temporary log variable in chunks
            for i in range(0, chunks):
                start = i*chunk_length
                end = (i+1)*chunk_length
                part = value[start:end]
                if part == '':
                    continue

                quoted = Sql.quote(part)
                expr.append("tmp := %s;" % quoted)
                expr.append("dbms_lob.writeAppend(%s, length(tmp), tmp);" % (varname) )

            expr.append("dbms_lob.close(%s);" % varname)


        expr.append(statement)
        expr.append(";")

        # free up the lob memory
        for varname, value in l_varname:
            expr.append("dbms_lob.freeTemporary(%s);" % varname)

        expr.append("end;")
        statement = "\n".join(expr)

        return statement


    def process_value(self, column, value, column_type="varchar"):
        '''Some values need to be preprocessed before going to an sql
        statement depending on type'''
        quoted = True 

        if value == "NULL":
            quoted = False
        elif column_type == "integer":
            quoted = False 
        elif column_type == "timestamp":
            orig_value = value
            value = str(value)
            if orig_value == None:
                quoted = False
                value = "NULL"
            elif value.startswith('SYSTIMESTAMP'):
                quoted = False 
            else:
                # try to match the date with regular expressions

                # Feb 20, 1999
                pattern1 = re.compile("^(\w{3}) (\d+), (\d+)$")

                # 1999-02-20
                pattern2 = re.compile("^(\d{4})-(\d{1,2})-(\d{1,2})$")

                # 02/20/2005 10:30
                pattern3 = re.compile("^(\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2})$")

                # 02/20/1999
                pattern4 = re.compile("^(\d{1,2})/(\d{2})/(\d{2,4})$")

                # Wed Apr 15 07:29:41 2009
                pattern5 = re.compile("^(\w{3}) (\w{3}) (\d{2}) (\d{2}):(\d{2}):(\d{2}) (\d{4})$")

                # 2008-03-01 00:00:00
                pattern6 = re.compile("^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$")
                # Wed Jun 3 18:13:13 2009
                pattern7 = re.compile("^(\w{3}) (\w{3}) \ ?(\d{1,2}) (\d{1,2}):(\d{2}):(\d{2}) (\d{4})$")

                # 18:13
                pattern8 = re.compile("^(\d{1,2}):(\d{2})$")

                # 18:13:15
                pattern9 = re.compile("^(\d{1,2}):(\d{2}):(\w{2})$")


                # remove the fractional seconds
                if value.find(".") != -1:
                    value, tmp = value.split(".", 1)

                # convert this using dateutil ... this makes all the
                # pattern matching unnecessary
                from dateutil import parser
                xx = parser.parse(value)
                value = xx.strftime("%Y-%m-%d %H:%M:%S")

                # put this one first ... all others are probably unnecessary
                if pattern6.match(value):
                    date_pattern = "YYYY-MM-DD HH24:MI:SS"
                elif pattern1.match(value):
                    date_pattern = "MON DD, YYYY"
                elif pattern2.match(value):
                    date_pattern = "YYYY-MM-DD"
                elif pattern3.match(value):
                    date_pattern = "MM/DD/YYYY HH24:MI"
                elif pattern4.match(value):
                    date_pattern = "MM/DD/YYYY"
                elif pattern5.match(value):
                    value = value[4:]
                    date_pattern = "MON DD HH24:MI:SS YYYY"
                elif pattern7.match(value):
                    date_pattern = "DY MON DD HH24:MI::SS YYYY"
                elif pattern8.match(value):
                    value = '1900-01-01 %s' % value
                    date_pattern = "YYYY-MM-DD HH24:MI"
                elif pattern9.match(value):
                    value = '1900-01-01 %s' % value
                    date_pattern = "YYYY-MM-DD HH24:MI:SS"
                else:
                    raise DatabaseImplException("Cannot match timestamp format for value [%s] in column [%s]" % (value, column))

                value = "TO_DATE('%s', '%s')" % (value, date_pattern)
                quoted = False

        return {"value": value, "quoted": quoted}


class SqliteImpl(PostgresImpl):
    
    def get_database_type(self):
        return "Sqlite"

    """
    def get_version(self):
        from sql import DbContainer
        sql = DbContainer.get("sthpw")
        result = sql.do_query("select version()")
        version_str = result[0][0]

        #PostgreSQL 8.2.11 on i386-redhat-linux-gnu, compiled by GCC gcc (GCC) 4.1.2 20070925 (Red Hat 4.1.2-33)
        parts = version_str.split(" ")
        version_parts = parts[1].split(".")
        version_parts = [int(x) for x in version_parts]
        return version_parts
    """


    #
    # Column methods
    #
    """
    def get_boolean(self, not_null=False):
        parts = []
        parts.append("boolean")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)

    """
    def get_serial(self, length=4, not_null=False):
        parts = []
        parts.append("integer")
        return " ".join(parts)


    """
    def get_int(self, length=4, not_null=False):
        parts = []
        parts.append("int%s" % length)
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)

    def get_text(self, not_null=False):
        parts = []
        parts.append("text")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_varchar(self, length=256, not_null=False):
        if not length:
            length = 256

        if length in [-1, 'max']:
            return self.get_text(not_null=not_null)
        parts = []
        parts.append("varchar(%s)" % length)
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)
    """

    def has_savepoint(self):
        return False


    def get_timestamp(self, default='now', not_null=False):
        parts = []
        parts.append("timestamp")
        if default:
            if default == "now":
                parts.append("DEFAULT %s" % self.get_timestamp_now())
            else:
                parts.append("DEFAULT %s" % default)

        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_timestamp_now(self, offset=None, type=None, op='+'):
        parts = []
        parts.append("CURRENT_TIMESTAMP")
        if offset:
            parts = ["DATETIME('now',"]

            # combine the the op and offset sign.
            if op == '-':
                offset = offset * -1
            
            if not type:
                type = "days"
            elif type.lower() in ['week','weeks']:
                # doesn't understand week, but month, year are fine
                type = "days"
                offset = offset * 7
            elif not type.endswith('s'):
                type = '%ss'%type

            parts.append("'%s %s')" % (offset, type) )
        return ''.join(parts)



    #
    # Sequence methods
    #
    # Sequences are not used in Sqlite
    def has_sequences(self):
        return False

    def get_reset_table_sequence_statement(self, table, database=None):
        # We do not use sequences in Sqlite
        return ""



    #
    # Regular Expressions
    # 
    def get_regex_filter(self, column, regex, op='EQI'):
        if op == 'EQI':
            #op = '~*'
            return "\"%s\" LIKE '%%%s%%'" %(column, regex)
        elif op == 'EQ':
            #op = '~'
            return "\"%s\" LIKE '%%%s%%'" %(column, regex)
        elif op == 'NEQI':
            #op = '!~*'
            return "\"%s\" NOT LIKE '%%%s%%'" %(column, regex)
        elif op == 'NEQ':
            #op = '!~'
            return "\"%s\" NOT LIKE '%%%s%%'" %(column, regex)
        else:
            raise SetupException('Invalid op [%s]. Try EQ, EQI, NEQ, or NEQI' %op)
            
        return "\"%s\" %s '%s'" %(column, op, regex)




    #
    # Type process methods
    #
    def process_value(self, name, value, column_type="varchar"):
        quoted = True
        if value == "NULL":
            quoted = False
        elif column_type == 'boolean':
            quoted = False
            if value in ['true', 'True', 1 ,'1', True]:
                value = 1
            else:
                value = 0
        elif column_type == 'timestamp':
            if value  == "NOW":
                quoted = False
                value = self.get_timestamp_now()
            elif isinstance(value, datetime.datetime):
                pass
            elif value.startswith(("CURRENT_TIMESTAMP","DATETIME(")):
                quoted = False

        return {"value": value, "quoted": quoted}

    #
    # Database methods
    # 

    def _get_database_path(self, database):

        if not isinstance(database,basestring):
            database = database.get_database()

        # dropping a database means deleting the database file
        db_dir = Config.get_value("database", "sqlite_db_dir")
        if not db_dir:
            data_dir = Environment.get_data_dir()
            db_dir = "%s/db" % data_dir

        db_path = "%s/%s.db" % (db_dir, database)
        
        return db_path



    def database_exists(self, database, host=None):
        db_path = self._get_database_path(database)
        if os.path.exists(db_path):
            return True
        else:
            return False


    def create_database(self, database):
        '''create a database'''
        # if the database already exists, do nothing
        if self.database_exists(database):
            return

        # nothing needs to be done ... databases are created automatically
        # on connection
        pass



    def drop_database(self, database):
        '''remove a database on disk. Note this is a very dangerous
        operation.  Use with care.'''
        # if the database already exists, do nothing
        if not self.database_exists(database):
            return

        # dropping a database means deleting the database file
        db_path = self._get_database_path(database)
        if os.path.exists(db_path):
            os.unlink(db_path)



    def get_modify_column(self, table, column, type, not_null=None):
        '''This is the same as postgres'''
        return super(Sqlite, self).get_modify_column(table, column, type, not_null)




    # Although this is a general function, it is presently only use for
    # Sqlite.  All table info is cached immediately with Sqlite because
    # the PRAGMA statement below causes transactions to commit
    #
    def cache_database_info(cls, sql):
        table_info = cls.get_table_info(sql)
        for table in table_info.keys():
            cls.get_column_info(sql, table)
    cache_database_info = classmethod(cache_database_info)


    def get_column_info(cls, db_resource, table, use_cache=True):

        key = "DatabaseImpl:column_info"
        cache_dict = Container.get(key)
        if cache_dict == None:
            cache_dict = {}
            Container.put(key, cache_dict)


        from sql import DbContainer, Sql
        if isinstance(db_resource, Sql):
            key2 = "%s:%s" % (db_resource.get_db_resource(), table)
        else:
            key2 = "%s:%s" % (db_resource, table)
        cache = cache_dict.get(key2)
        if cache != None:
            return cache

        cache = {}
        cache_dict[key2] = cache

        # get directly from the database
        if isinstance(db_resource, Sql):
            sql = db_resource
        else:
            sql = DbContainer.get(db_resource)

        query = 'PRAGMA table_info("%s")' % table
        results = sql.do_query(query)

        # data return is a list of the following
        #(0, u'id', u'integer', 1, None, 0)
        for result in results:
            name = result[1]
            data_type = result[2]
            # notnull could be 1 or 99 which equals True
            nullable = result[3] not in [1, 99]
            #nullable = True

            if data_type.startswith("character varying"):
                size = data_type.replace("character varying", "")
                size = size.replace("(", "")
                size = size.replace(")", "")
                size = int(size)
                data_type = 'varchar'
            elif data_type.startswith("varchar"):
                size = data_type.replace("varchar", "")
                size = size.replace("(", "")
                size = size.replace(")", "")
                if size:
                    size = int(size)
                else:
                    size = 256
                data_type = 'varchar'
            elif data_type.startswith("timestamp"):
                data_type = 'timestamp'
                size = 0
            else:
                size = 0
        

            info_dict = {'data_type': data_type, 'nullable': nullable,
                'size': size}
            cache[name] = info_dict

        return cache

    get_column_info = classmethod(get_column_info)


    def get_table_info(cls, db_resource):

        key = "DatabaseImpl:table_info"
        cache_dict = Container.get(key)
        if cache_dict == None:
            cache_dict = {}
            Container.put(key, cache_dict)


        from sql import DbContainer, Sql
        if isinstance(db_resource, Sql):
            key2 = "%s" % (db_resource.get_db_resource())
        else:
            key2 = "%s" % (db_resource)
        cache = cache_dict.get(key2)
        if cache != None:
            return cache

        info = {}
        cache_dict[key2] = info


        if isinstance(db_resource, Sql):
            sql = db_resource
        else:
            sql = DbContainer.get(db_resource)
        statement = '''SELECT name FROM sqlite_master where type='table';'''
        results = sql.do_query(statement)
        for result in results:
            table = result[0]
            info[table] = table

        return info

    get_table_info = classmethod(get_table_info)



    def get_constraints(self, db_resource, table):

        # FIXME: this only works with Sqlite!!!
        # FIXME: this only works with Sqlite!!!
        # FIXME: this only works with Sqlite!!!

        from sql import Select, DbContainer
        db = DbContainer.get(db_resource)
        statement = '''SELECT sql FROM sqlite_master where name='%s';''' % table
        results = db.do_query(statement)

        constraints = []
        if not results:
            return constraints
        sql = results[0][0]

        for line in sql.split("\n"):
            line = line.strip()
            if line.startswith("CONSTRAINT"):
                parts = line.split(" ")
                name = parts[1].strip('"')
                mode = parts[2]
                columns = parts[3].strip("(").strip(")").split(",")
                # remove unicode
                columns = [str(x) for x in columns]

                info = {
                    'name': name,
                    'columns': columns,
                    'mode': mode
                }
                constraints.append(info)


        return constraints




class MySQLImpl(PostgresImpl):

    def __init__(self):

        # FIXME: this will not work in mixed db cases because it assumes a global
        # single database
        self.server   = Config.get_value("database", "server")
        self.port     = Config.get_value("database", "port")
        self.user     = Config.get_value("database", "user")
        self.password = Config.get_value("database", "password")


    def get_database_type(self):
        return "MySQL"


    def get_version(self):
        from sql import DbContainer
        sql = DbContainer.get("sthpw")

        # eg. result is (('5.1.47',),)
        result = sql.do_query("select @@version")
        version_str = result[0][0]
        version_parts = version_str.split(".")
        version_parts = [int(x) for x in version_parts]
        
        # eg. result is [5, 1, 47]
        return version_parts


  

    def process_value(self, name, value, column_type="varchar"):
        if column_type == 'boolean':
            quoted = False
            if value in ['true', 1, True]:
                value = 1
            else:
                value = 0
            return {"value": value, "quoted": quoted}

        if (column_type == 'timestamp'):
            # We are converting a timestamp ISO string to datetime obj.
            from dateutil import parser
            try:
                value = parser.parse(value)
            except:
                value = value

        if isinstance(value, datetime.datetime):
            # We need to convert the time to UTC, and strip the timezone info.
            if value.tzinfo is not None:
                # Convert to UTC
                if value.utcoffset() is not None:
                    value = value - value.utcoffset()
            # Strip the timezone info.
            value = value.replace(tzinfo=None)
            # We now have a datetime obj without timezone info.
            value_str = value.strftime("%Y-%m-%d %H:%M:%S")
            return {"value": value_str, "quoted": True}


    def get_table_info(self, db_resource):

        key = "DatabaseImpl:table_info"
        cache_dict = Container.get(key)
        if cache_dict == None:
            cache_dict = {}
            Container.put(key, cache_dict)

        from sql import DbContainer, Sql
        if isinstance(db_resource, Sql):
            key2 = "%s" % (db_resource.get_db_resource())
        else:
            key2 = "%s" % (db_resource)
        cache = cache_dict.get(key2)
        if cache != None:
            return cache

        info = {}
        cache_dict[key2] = info


        if not isinstance(db_resource, basestring):
            database_name = db_resource.get_database()
        else:
            database_name = db_resource

        from sql import Select, DbContainer
        sql = DbContainer.get(db_resource)
        statement = '''SHOW TABLES FROM "%s"''' % database_name
        results = sql.do_query(statement)
        for result in results:
            table = result[0]
            info[table] = table

        return info


    def get_column_info(cls, db_resource, table, use_cache=True):

        key = "DatabaseImpl:column_info"
        cache_dict = Container.get(key)
        if cache_dict == None:
            cache_dict = {}
            Container.put(key, cache_dict)


        from sql import DbContainer, Sql
        if isinstance(db_resource, Sql):
            key2 = "%s:%s" % (db_resource.get_db_resource(), table)
        else:
            key2 = "%s:%s" % (db_resource, table)
        cache = cache_dict.get(key2)
        if cache != None:
            return cache

        dict = {}
        cache_dict[key2] = dict

        # get directly from the database
        from sql import DbContainer
        sql = DbContainer.get(db_resource)
        query = '''SHOW COLUMNS FROM "%s"''' % table
        results = sql.do_query(query)


        # data return is a list of the following
        #(0, u'id', u'integer', 1, None, 0)
        for result in results:
            #if table == "search_object":
            #    print("result: ", result)

            name = result[0]
            data_type = result[1]
            nullable = True

            if data_type.startswith("character varying"):
                size = data_type.replace("character varying", "")
                size = size.replace("(", "")
                size = size.replace(")", "")
                size = int(size)
                data_type = 'varchar'
            elif data_type.startswith("varchar"):
                size = data_type.replace("varchar", "")
                size = size.replace("(", "")
                size = size.replace(")", "")
                if size:
                    size = int(size)
                else:
                    size = 256
                data_type = 'varchar'

            # rather big assumption that tinyint == boolean
            elif data_type.startswith("tinyint"):
                parts = data_type.split(" ")
                size = parts[0].replace("tinyint", "")
                size = size.replace("(", "")
                size = size.replace(")", "")
                if size:
                    size = int(size)
                else:
                    size = 4
                data_type = 'boolean'

            elif data_type.startswith("longtext"):
                data_type = 'text'
                size = 0
            elif data_type.startswith("mediumtext"):
                data_type = 'text'
                size = 0
            elif data_type.startswith("varchar"):
                data_type = 'text'
                size = 256

            elif data_type.startswith("JSON"):
                data_type = 'json'
                size = 0

            elif data_type.startswith("int"):
                parts = data_type.split(" ")
                size = parts[0]
                size = size.replace("int", "")
                size = size.replace("(", "")
                size = size.replace(")", "")
                if size:
                    size = int(size)
                else:
                    size = 4
                data_type = 'integer'
            elif data_type.startswith("timestamp"):
                data_type = 'timestamp'
                size = 0
            else:
                size = 0
        

            info_dict = {'data_type': data_type, 'nullable': nullable,
                'size': size}
            dict[name] = info_dict


        return dict


    #
    # Column methods
    #
    def get_serial(self, length=4, not_null=False):
        parts = []
        parts.append("serial")
        return " ".join(parts)

    def get_text(self, not_null=False):
        parts = []
        parts.append("longtext")
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)


    def get_boolean(self, not_null=False):
       parts = []
       parts.append("tinyint")
       if not_null:
           parts.append("NOT NULL")
       return " ".join(parts)



    def get_varchar(self, length=191, not_null=False):
        if not length:
            length = 191

        if length in [-1, 'max']:
            return self.get_text(not_null=not_null)
        parts = []
        parts.append("varchar(%s)" % length)
        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)




    def get_timestamp(self, default=None, not_null=False, timezone=False):
        parts = []
        if timezone:
            parts.append("timestamp with time zone")
        else:
            parts.append("timestamp")
        if default:
            if default == "now":
                # If more than one column has CURRENT_TIMESTAMP in MySQL
                # then it produces the error:

                # Incorrect table definition; there can be only one TIMESTAMP
                # column with CURRENT_TIMESTAMP in DEFAULT or ON UPDATE clause

                # This appears to be an old code implementation error in
                # MySQL, so we are ignoring the now() default until this is
                # fixed
                #parts.append("DEFAULT %s" % self.get_timestamp_now())
                pass

            else:
                parts.append("DEFAULT %s" % default)

        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)



    def get_json(self, not_null=False):
        parts = []

        # JSON not support untile MySQL 5.7 (need to check version) 
        #parts.append("JSON")
        parts.append("text")

        if not_null:
            parts.append("NOT NULL")
        return " ".join(parts)



 

    def get_timestamp_now(self, offset=None, type=None, op='+'):
        '''MySQL get current / offset timestamp from now'''
        parts = []
        parts.append("NOW()")
        if offset:
            if not type:
                type = "DAY"
            parts.append(" INTERVAL %s %s" % (offset, type) )
        op = ' %s ' % op
        return op.join(parts)

    #
    # Sequence methods
    #
    # Sequences are not used in MySQL
    def has_sequences(self):
        return False

    def get_reset_table_sequence_statement(self, table, database=None):
        # We do not use sequences in Sqlite
        return ""




    #
    # Regular Expressions
    # 
    def get_regex_filter(self, column, regex, op='EQI'):
        if op == 'EQI':
            #op = '~*'
            return "\"%s\" LIKE '%%%s%%'" %(column, regex)
        elif op == 'EQ':
            #op = '~'
            return "\"%s\" LIKE '%%%s%%'" %(column, regex)
        elif op == 'NEQI':
            #op = '!~*'
            return "\"%s\" NOT LIKE '%%%s%%'" %(column, regex)
        elif op == 'NEQ':
            #op = '!~'
            return "\"%s\" NOT LIKE '%%%s%%'" %(column, regex)
        else:
            raise SetupException('Invalid op [%s]. Try EQ, EQI, NEQ, or NEQI' %op)
            
        return "\"%s\" %s '%s'" %(column, op, regex)


    #
    # Regex expressions
    #
    def get_regex_filter(self, column, regex, op='EQI'):
        if op == 'EQI':
            op = 'REGEXP'
            case_sensitive = False
        elif op == 'EQ':
            op = 'REGEXP'
            case_sensitive = True
        elif op == 'NEQI':
            op = 'NOT REGEXP'
            case_sensitive = False
        elif op == 'NEQ':
            op = 'NOT REGEXP'
            case_sensitive = True
        else:
            raise SetupException('Invalid op [%s]. Try EQ, EQI, NEQ, or NEQI' %op)

        if case_sensitive:
            return "\"%s\" %s '%s'" %(column, op, regex)
        else:
            regex = regex.lower()
            return "LOWER(\"%s\") %s '%s'" %(column, op, regex)


    #
    # Database methods
    # 
    def create_database(self, database):
        '''create a database'''
        from sql import DbContainer, DbResource
        db_resource = DbResource.get_default("")

        if not isinstance(database, basestring):
            database = database.get_database()

        sql = DbContainer.get(db_resource)
        statement = '''CREATE DATABASE IF NOT EXISTS "%s";''' % database
        results = sql.do_update(statement)


    def drop_database(self, database):
        # TODO: if the database does not exist, do nothing
        # if not database_exists(database):
        #    return
        

        # TODO: Retrieve server, username, password from TACTIC config file.
        # eg.   mysql --host=localhost --port=5432 --user=root --password=south123paw --execute="create database unittest"
        drop_SQL_arg = 'DROP DATABASE %s' % database.get_database()
        if self.password == 'none':
            create = 'mysql --host=%s --port=%s --user=%s --execute="%s"' % \
                (self.server, self.port, self.user, drop_SQL_arg)
        else:
            create = 'mysql --host=%s --port=%s --user=%s --password=%s --execute="%s"' % \
                (self.server, self.port, self.user, self.password, drop_SQL_arg)
        cmd = os.popen(create)
        result = cmd.readlines()
        if not result:
            print("No output from sql command to drop db [%s], assumed success" % database)
            cmd.close()
            return
        else:
            print(result)
        cmd.close()

    def set_autocommit(self, sql, flag):
        '''Note: This must be performed before transactions are started.'''
        sql.conn.autocommit(flag)

    def commit_on_schema_change(self):
        return True




class TacticImpl(PostgresImpl):

    class TacticCursor(object):
        def execute():
            print("execute")

    # Mimic DB2 API
    OperationalError = Exception
    def cursor():
        return TacticCursor()
    cursor = staticmethod(cursor)

    def __init__(self):
        from tactic_client_lib import TacticServerStub
        self.server = TacticServerStub.get(protocol='xmlrpc')



    def get_database_type(self):
        return "TACTIC"



    def get_table_info(self, db_resource):
        search_type = "table/whatever?project=fifi"
        table_info = self.server.get_table_info(search_type)
        return table_info





