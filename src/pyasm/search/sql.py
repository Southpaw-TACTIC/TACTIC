##########################################################
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

__all__ = ["SqlException", "DatabaseException", "Sql", "DbContainer", "DbResource", "DbPasswordUtil", "Select", "Insert", "Update", "Delete", "CreateTable", "DropTable", "AlterTable", 'CreateView']


import os, types, thread, sys
import re, datetime

from threading import Lock

from pyasm.common import Config, TacticException, Environment
from dateutil.tz import * 

# import database libraries
DATABASE_DICT = {}

try:
    import pyodbc
    DATABASE_DICT["SQLServer"] = pyodbc
    #Config.set_value("database", "vendor", "SQLServer")
except ImportError, e:
    pass

try:
    try:
        import psycopg2
    except ImportError, e:
        # if psycopg2 is not installed we try to use psycopg2cffi (useful for pypy compatibility)
        from psycopg2cffi import compat
        compat.register()
    # set to return only unicode
    import psycopg2.extensions
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    #psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
    DATABASE_DICT["PostgreSQL"] = psycopg2
except ImportError, e:
    pass

try:
    ORACLE_HOME = Config.get_value("database", "ORACLE_HOME")
    if ORACLE_HOME:
        os.environ['ORACLE_HOME'] = str(ORACLE_HOME)

    NLS_LANG = Config.get_value("database", "NLS_LANG")
    if not NLS_LANG:
        NLS_LANG = 'american_america.us7ascii'
    os.environ['NLS_LANG'] = str(NLS_LANG)

    import cx_Oracle

    DATABASE_DICT["Oracle"] = cx_Oracle

except ImportError, e:
    pass

# MySQL
try:
    import MySQLdb
    DATABASE_DICT["MySQL"] = MySQLdb
except ImportError, e:
    pass


# Sqlite
try:
    import sqlite3 as sqlite
    DATABASE_DICT["Sqlite"] = sqlite
except ImportError, e:
    pass


# MongoDb
try:
    import pymongo
    pymongo.ProgrammingError = Exception
    DATABASE_DICT["MongoDb"] = pymongo
except ImportError, e:
    pass


# Salesforce
"""
try:
    import simple_salesforce
    DATABASE_DICT["Salesforce"] = simple_salesforce
except ImportError, e:
    pass
"""



# TACTIC Database
try:
    from database_impl import TacticImpl
    DATABASE_DICT["TACTIC"] = TacticImpl
except ImportError, e:
    pass




VENDORS = ['PostgreSQL', 'SQLServer', 'Oracle', 'Sqlite', 'MySQL', 'MongoDb', 'TACTIC']


# Get the configured Db.
DATABASE = None
pgdb = None
def set_default_vendor(vendor=None):
    global DATABASE
    global pgdb

    if vendor:
        DATABASE = vendor
        return

    DATABASE = Config.get_value("database", "vendor")
    if not DATABASE:
        DATABASE = "PostgreSQL"

    assert DATABASE in VENDORS
    pgdb = DATABASE_DICT.get(DATABASE)
    if not pgdb:
        raise TacticException("WARNING: database library for default database [%s] is not installed" % DATABASE)


try:
    set_default_vendor()
except TacticException as e:
    print(e)


from pyasm.common import *

from database_impl import *
from transaction import *


class SqlException(TacticException):
    pass
class DatabaseException(TacticException):
    pass


class Sql(Base):
    '''Class that handles all access to the database'''

    DO_QUERY_ERR = "do_query error"

    def __init__(self, database_name, host=None, user=None, password=None, vendor=None, port=None):

        if DbResource.is_instance(database_name):
            db_resource = database_name
            host = db_resource.get_host()
            port = db_resource.get_port()
            database_name = db_resource.get_database()
            vendor = db_resource.get_vendor()
            user = db_resource.get_user()
            password = db_resource.get_password()
        else:
            #assert type(database_name) in types.StringTypes
            # allow unicode
            assert isinstance(database_name, basestring) 
        self.database_name = database_name
        #self.database_name = "schema_test"

        # get the database from the config file
        if host:
            self.host = host
        else:
            self.host = Config.get_value("database", "server")

        if user:
            self.user = user
        else:
            self.user = Config.get_value("database", "user")
        if port: self.port = port
        else: self.port = Config.get_value("database", "port")
       
        if password:
            self.password = password
        # get from encrypted file
        else:
            self.password = DbPasswordUtil.get_password()

        if not self.host:
            self.host = "localhost"

        self.vendor = vendor
        if not self.vendor:
            self.vendor = Config.get_value("database", "vendor")

        self.database_impl = DatabaseImpl.get(self.vendor)
        self.pgdb = DATABASE_DICT.get(self.vendor)
        if not self.pgdb:
            raise TacticException("ERROR: database library for [%s] is not installed" % self.vendor)


        self.cursor = None
        self.results = ()
        self.conn = None
        self.last_query = None
        self.row_count = -1

        self.transaction_count = 0
        self.description = None


    def get_db_resource(self):
        db_resource = DbResource(self.database_name, host=self.host, port=self.port, vendor=self.vendor, user=self.user, password=self.password)
        return db_resource


    def set_default_vendor(vendor):
        set_default_vendor(vendor)
    set_default_vendor = staticmethod(set_default_vendor)



    #def __del__(self):
    #    print("CONNECT: delete: ", self)


    ### These are for the default .. most often for the sthpw database
    def default_database_exists(cls, database):
        '''test if a table exists in a db'''
        impl = Sql.get_database_impl()
        return impl.database_exists(database)
    default_database_exists = classmethod(default_database_exists) 


    def get_default_database_version(cls):
        return cls.get_default_database_impl().get_version()
    get_default_database_version = classmethod(get_default_database_version)



    def get_default_database_type():
        return Config.get_value("database", "vendor")
    get_default_database_type = staticmethod(get_default_database_type)




    def get_default_database_impl():
        return DatabaseImpl.get()
    get_default_database_impl = staticmethod(get_default_database_impl)


    def get_default_timestamp_now():
        return DatabaseImpl.get().get_timestamp_now()
    get_default_timestamp_now = staticmethod(get_default_timestamp_now)



    #####
    def get_database_version(self):
        return self.get_database_impl().get_version()

    def get_database_type(self):
        return self.vendor

    def get_database_impl(self):
        return self.database_impl


    def get_timestamp_now(self):
        return self.database_impl.get_timestamp_now()




    def get_table_description(self):
        return self.description


    def get_database_name(self):
        return self.database_name

    def get_host(self):
        return self.host

    def get_user(self):
        return self.user

    def get_password(self):
        return self.password

    def get_vendor(self):
        return self.vendor



    def get_connection(self):
        '''get the underlying database connection'''
        return self.conn



    def get_columns_from_description(self):
        columns = []
        for description in self.description:
            columns.append( description[0] )

        # In some versions of sqlite, the full name is returned with quotes
        # and table, so just process this
        fixed_columns = []
        for column in columns:
            parts = column.split(".")
            column = parts[-1]
            column = column.strip('"')
            fixed_columns.append(column)

        return fixed_columns




    def get_columns(self,table=None,use_cache=True):
        '''Returns a list of string ordered columns contained in this table
        '''
        db_resource = self.get_db_resource()
        database = self.get_database_name()

        from pyasm.security import Site
        #use_cache = False
        site = Site.get_site()
        if site:
            key = '%s:%s:%s' %(site, db_resource, table)
        else:
            key = '%s:%s' %(db_resource, table)
        if use_cache:
            columns = Container.get_dict("Sql:table_columns", key)
            if columns:
                return columns[:]

            # use global cache
            if database == 'sthpw':
                from pyasm.biz import CacheContainer
                if site:
                    cache = CacheContainer.get("%s:sthpw_column_info" % site)
                else:
                    cache = CacheContainer.get("sthpw_column_info")
                if cache:
                    columns = cache.get_value_by_key("columns", table)
                    if columns != None:
                        return columns[:]
                        #return columns

        impl = self.get_database_impl()
        columns = impl.get_columns(db_resource, table)

        if use_cache:
            Container.put_dict("Sql:table_columns", key, columns)
 
        return columns[:]


    def get_table_info(self):
        impl = self.get_database_impl()
        info = impl.get_table_info(self.get_db_resource()) 
        return info


 
    def get_column_info(self, table, column=None, use_cache=True):
        impl = self.get_database_impl()
        info = impl.get_column_info(self.get_db_resource(), table)
        if not column:
            return info
        else:
            return info.get(column)

  
    def get_column_types(self, table):
        impl = self.get_database_impl()
        return impl.get_column_types(self.get_db_resource(), table) 

    def get_column_nullables(self, table):
        impl = self.get_database_impl()
        return impl.get_column_nullables(self.get_db_resource(), table) 


    def is_in_transaction(self):
        '''Returns a boolean showing whether the database is in transaction
        or not'''
        if self.transaction_count <= 0:
            return False
        else:
            return True

    def get_row_count(self):
        '''returns the number of rows effected in the last update'''
        return self.row_count


    def start(self):
        '''start a transaction'''
        self.transaction_count += 1

    def set_savepoint(self, name='save_pt'):
        '''set a savepoint'''
        stmt = self.database_impl.set_savepoint(name)
        if stmt:
            cursor = self.conn.cursor()
            cursor.execute(stmt)

    def rollback_savepoint(self, name='save_pt', release=True):
        '''rollback to a savepoint'''
        self.cursor = self.conn.cursor()
        stmt = self.database_impl.rollback_savepoint(name)
        if not stmt:
            return
        self.cursor.execute(stmt)
        if release:
            self.release_savepoint(name)

    def release_savepoint(self, name='save_pt'):
        if self.conn == True:
            return
        release_stmt = self.database_impl.release_savepoint(name)
        if not release_stmt:
            return
        if release_stmt:
            self.cursor.execute(release_stmt)
        

    
    def commit(self):
        '''commit the transaction'''
        self.transaction_count -= 1

        # only commit if transaction count = 0 to support embedded
        # transactions
        #if self.transaction_count == 0:
        if self.transaction_count <= 0:
            try:
                self.transaction_count = 0

                # NOTE: protect against database being already closed.
                # Note sure why it is being closed, but there are some
                # extreme circumstances where this will occur
                if not self.conn:
                    # reconnect
                    self.connect()
                else:
                    self.conn.commit()
                    
                sql_dict = DbContainer._get_sql_dict()
                database_name = self.get_database_name()
                sql_dict[database_name] = self

            except self.pgdb.OperationalError, e:
                raise SqlException(e.__str__())
            


    def rollback(self, force=False):
        '''rollback the transaction'''
        if force or self.transaction_count > 0:
            if self.conn:
                self.conn.rollback()
                self.transaction_count = 0

    def connect(self):
        '''connect to the database'''
        if not self.host:
            raise DatabaseException("Server setting is empty")

        # pgdb connection code
        auth = None
        try:
            import tzlocal_olson
            #tz_name = datetime.datetime.now(tzlocal()).tzname()
            # get olson timezone name as opposed to abv. tz name 
            tz_name = tzlocal_olson.get_localzone().zone
            
            if self.vendor == "PostgreSQL":
                # psycopg connection code
                if self.password == "" or self.password == "none":
                    password_str = ""
                else:
                    password_str = "password=%s" % self.password
                if not self.port:
                    self.port = 5432
                sslmode = "require"
                sslmode = "disable"
                auth = "host=%s port=%s dbname=%s sslmode=%s user=%s %s" % \
                    (self.host, self.port, self.database_name, sslmode, self.user, password_str)
                self.conn = self.pgdb.connect(auth)

                #TODO: check other db impl on timezone impl
                self.do_update("SET timezone='%s'"%tz_name)
            elif self.vendor == "Sqlite":

                db_dir = Config.get_value("database", "sqlite_db_dir")
                if not db_dir:
                    #install_dir = Environment.get_install_dir()
                    #db_dir = "%s/src/install/start/db" % install_dir
                    data_dir = Environment.get_data_dir()
                    db_dir = "%s/db" % data_dir

                # DEBUG: this -1 database seems to popup
                if self.database_name in [-1, '-1']:
                    raise DatabaseException("Database '-1' is not valid")
                auth = "%s/%s.db" % (db_dir, self.database_name)
                self.conn = sqlite.connect(auth, isolation_level="DEFERRED" )

                # immediately cache all of the columns in the database.  This
                # is because get_column_info in Sqlite requires a PRAGMA
                # statement which forces a transaction to commit
                from database_impl import SqliteImpl
                SqliteImpl.cache_database_info(self)


            elif self.vendor == "MySQL":
                encoding = Config.get_value("database", "encoding")
                charset = Config.get_value("database", "charset")
                if not encoding:
                    #encoding = 'utf8mb4'
                    encoding = 'utf8'
                if not charset:
                    charset = 'utf8'
                if not self.port:
                    self.port = 3306
                int_port = int(self.port)
                self.conn = MySQLdb.connect(  db=self.database_name,
                                            host=self.host,
                                            user=self.user,
                                            port=int_port,
                                            charset=charset,
                                            use_unicode=True,
                                            passwd=self.password )
                self.do_query("SET sql_mode='ANSI_QUOTES';SET NAMES %s"%encoding)

            elif self.vendor == "Oracle":
                # if we connect as a single user (like most databases, then
                # use the user name), otherwise if we connect by schema,
                # we use the database name.  This is determined by whether
                # or not the user field is empty
                if not self.user:
                    auth = '%s/%s@%s' % (self.database_name, self.password, self.host)
                else:
                    auth = '%s/%s@%s' % (self.user, self.password, self.host)
                self.conn = self.pgdb.connect(str(auth))

            elif self.vendor == "SQLServer":
                sqlserver_driver = '{SQL Server}'
                # pyodbc connection code
                if self.password == "" or self.password == "none":
                    password_str = ""
                else:
                    password_str = self.password
                # >>> cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=localhost,1433;DATABASE=my_db;UID=tactic;PWD=south123paw')
# 
                auth = "DRIVER=%s; SERVER=%s,%s; DATABASE=%s; UID=%s; PWD=%s" % \
                    (sqlserver_driver, self.host, self.port, self.database_name, self.user, password_str)
                self.conn = pyodbc.connect(auth)
                # set isolation level to prevent excessive read lock on tables
                self.do_update("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")
                
            elif self.vendor == "MongoDb":

                from mongodb import MongoDbConn
                self.conn = MongoDbConn(self.database_name)

            elif self.vendor == "Salesforce":

                database_impl = DatabaseImpl.get(self.vendor)
                #self.conn = database_impl.get_connection()

                from spt.tools.salesforce import SalesforceConn
                self.conn = SalesforceConn(self.database_name)

            elif self.vendor == "TACTIC":
                from pyasm.search import TacticImpl
                self.conn = TacticImpl()
                #raise DatabaseException("Database TACTIC not yet implemented")
                
            else:
                raise DatabaseException("Unsupported Database [%s]" % self.vendor)

        except Exception as e:
            #print("ERROR: connecting to database [%s, %s]" % (self.host, self.database_name), e.__str__())
            raise
            raise DatabaseException(e)

        assert self.conn

        return self



    # Resets sequence so that the next available ID number is exactly one greater than the highest existing ID
    # number of the given table
    #
    def reset_sequence_for_table(self, table, database=None):

        # FIXME: currently only available for the Oracle database 

        impl = self.get_database_impl()
        stmt = impl.get_reset_table_sequence_statement(table, database)
        from sql import DbContainer
        sql = DbContainer.get(self.get_database_name())
        results = sql.do_update(stmt)



    def modify_column(self, table, column, type, not_null=None):
        impl = self.get_database_impl()
        statements = impl.get_modify_column(table, column, type, not_null)
        from sql import DbContainer
        sql = DbContainer.get(self.get_database_name())
        for statement in statements:
            sql.do_update(statement)


    def clear_results(self):
        # MySQL uses tuples
        impl = self.get_database_impl()
        if impl.get_database_type() not in ['MySQL']:
            for i in range(0, len(self.results)):
                self.results[i] = None

        self.results = []


    # FIXME: is there any reason to have this function.  This should be 
    # incorporated into do_query.
    """
    def execute(self, query, num_attempts=0):
        '''execute a query'''

        #raise SqlException("FIXME: Incorporate into do_query")

        try:
            # in case of accidental loss of connection
            if not self.conn:
                # reconnect
                self.connect()

            self.query = query
            self.cursor = self.conn.cursor()
            self.cursor.execute(query)

            self.description = self.cursor.description
            return

        except pgdb.OperationalError, e:
            # A reconnect will only be attempted on the first query.
            # This is because subsequent could be in a transaction and
            # closing and reconnecting will completely mess up the transaction
            #
            first_query = Container.get("Sql::%s::first_query" % self.database_name)
            if first_query == False:
                raise SqlException("%s: %s\n%s" % (self.DO_QUERY_ERR, query,e.__str__()) )

            if num_attempts >= 3:
                print("ERROR: three failed attempts have been made to access [%s]" % self.database_name)
                raise SqlException("%s: %s\n%s" % (self.DO_QUERY_ERR, query,e.__str__()) )

            Container.put("Sql::first_query", False)

            # try to reconnect
            print("WARNING: a database error [%s] has been encountered: " % e.__class__.__name__)
            print(str(e))
            print("Attempting to reconnect and reissue query")
            # try closing: oracle throws an exception if you try to close
            # on an already closed connection
            try:
                self.close()
            except:
                pass
            self.connect()
            return self.do_query(query, num_attempts=num_attempts+1)

        except pgdb.Error, e:
            error_msg = str(e)
            print("ERROR: %s: "%self.DO_QUERY_ERR, error_msg, str(query))
            # don't include the error_msg in Exception to avoid decoding error 
            raise SqlException("%s: %s\n" % (self.DO_QUERY_ERR, query))
    """





    def do_query(self, query, num_attempts=0):
        '''execute a query'''

        self.clear_results()

        try:
            # in case of accidental loss of connection
            if not self.conn:
                # reconnect
                self.connect()


            vendor = self.get_vendor()
            if isinstance(query, Select):
                self.results = query.execute(self)
            else:

                #import time
                #start = time.time()
                #print(self.database_name, query)
                self.query = query
                self.cursor = self.conn.cursor()
                #import time
                #start = time.time()
                self.cursor.execute(query)

                self.description = self.cursor.description

                # copy the data structure because LOBs in Oracle become stale
                if self.get_database_type() == "Oracle":
                    import cx_Oracle
                    self.results = []
                    for x in self.cursor:
                        result = []
                        for y in x:
                            if isinstance(y, cx_Oracle.LOB):
                                result.append(str(y))
                            else:
                                result.append(y)
                        self.results.append(result)
                else:
                    self.results = self.cursor.fetchall()

                self.cursor.close()
                #print(time.time() - start)


            return self.results


        except self.pgdb.OperationalError, e:
            # A reconnect will only be attempted on the first query.
            # This is because subsequent could be in a transaction and
            # closing and reconnecting will completely mess up the transaction
            #
            key = "Sql::%s::%s::first_query" % (self.vendor, self.database_name)
            first_query = Container.get(key)
            if first_query == False:
                raise SqlException("%s: %s\n%s" % (self.DO_QUERY_ERR, query,e.__str__()) )

            if num_attempts >= 3:
                print("ERROR: three failed attempts have been made to access [%s]" % self.database_name)
                raise SqlException("%s: %s\n%s" % (self.DO_QUERY_ERR, query,e.__str__()) )

            Container.put("Sql::first_query", False)

            # try to reconnect
            print("WARNING: a database error [%s] has been encountered: " % e.__class__.__name__)
            print(str(e))
            print("Attempting to reconnect and reissue query")
            # try closing: oracle throws an exception if you try to close
            # on an already closed connection
            try:
                self.close()
            except:
                pass
            self.connect()
            return self.do_query(query, num_attempts=num_attempts+1)

        except self.pgdb.Error, e:
            error_msg = str(e)
            print("ERROR: %s: "%self.DO_QUERY_ERR, error_msg, str(query))
            # don't include the error_msg in Exception to avoid decoding error 
            raise SqlException("%s: %s\n" % (self.DO_QUERY_ERR, query))


    def get_value(self, query):
        '''convenience function when you know there will be only one result'''
        result = self.do_query(query)
        if len(result) > 0:
            value = result[0][0]
            if value == None:
                value = ""
        else:
            value = ""
        return value

    def get_int(self, query):
        return int(self.get_value(query))



    def do_update(self, query, quiet=False):
        """execute an update. If quiet = True, it doesn't print error causing sql"""
        if query =="":
            return

        try:
            if not self.conn:
                self.connect()

            # store the last query
            #print("[%s]" % self.database_name, query)

            self.query = query
            self.cursor = self.conn.cursor()

            #self.execute(query)
            from pyasm.security import Site
            self.cursor.execute(query)

            # remember the row count
            self.row_count = self.cursor.rowcount

            if self.vendor == 'Sqlite':
                self.last_row_id = self.cursor.lastrowid
            elif self.vendor == 'MySQL':
                self.last_row_id = self.conn.insert_id()
            else:
                self.last_row_id = 0

            self.cursor.close()


            # commit the transaction if there is no transaction
            if self.transaction_count == 0:
                self.transaction_count = 1
                self.commit()

        except self.pgdb.ProgrammingError, e:
            if str(e).find("already exists") != -1:
                return
            if isinstance(query, unicode):
                wrong_query = query.encode('utf-8')
            else:
                wrong_query = unicode(query, errors='ignore').encode('utf-8')

            print("Error with query (ProgrammingError): ", self.database_name, wrong_query)
            print(str(e))
            raise SqlException(str(e))
        except self.pgdb.Error, e:
            if not quiet:
                if isinstance(query, unicode):
                    wrong_query = query.encode('utf-8')
                else:
                    wrong_query = unicode(query, errors='ignore').encode('utf-8')
                print("Error with query (Error): ", self.database_name, wrong_query)
            raise SqlException(e.__str__())



    def update_single(self, statement_obj):
        '''insert/updates a single statement.  This is a convenience function
        which returns the id of the update row.  It also checks that
        only one row was actually affected'''

        id = 0

        is_insert = None
        if isinstance(statement_obj, Insert):
            is_insert = True
        elif isinstance(statement_obj, Update):
            is_insert = False
        else:
            raise SqlException("Cannot determine if this is an INSERT or and UPDATE [%s]" % statement_obj.statement)

        # get the update id
        if not is_insert:
            id_statement = statement_obj.get_id_statement()
            id = self.get_value(id_statement)


        # do the update
        statement = statement_obj.get_statement()
        self.do_update(statement)


        # check that one row and only one raw was affected
        if self.row_count == 0:
            raise SqlException("Statement [%s] did not affect any rows")

        if self.row_count > 1:
            raise SqlException("Statement [%s] affected any [%s] rows" % (statement, self.row_count) )

        # get the insert id
        if is_insert:
            id_statement = statement_obj.get_id_statement()
            id = self.get_value(id_statement)

        if id > 0:
            return id
            
        raise SqlException("Improper id return with statement [%s]" % statement)




    def close(self):
        if self.conn == None:
            return

        self.conn.close()
        self.conn = None



    def dump(self):
        print(self.results)


    # static functions
    def quote(value, has_outside_quotes=True, escape=False, unicode_escape=False):
        '''prepares a value so that it can be entered as a value in the
        database
            @param: 
                has_outside_quotes - refer to having single_quotes
                escape - if escape=True, set has_outside_quotes=False
                unicode_escape - N'some str' for SQLServer '''
        if value == None:
            return "NULL"

        # replace all single quotes with two single quotes
        value_type = type(value)
        if value_type in [types.ListType, types.TupleType]:
            if len(value) == 0:
                # Previously no check if list is empty, which is an issue
                # for trying to get 'value[0]' as it's not defined. Assuming
                # that if the list is empty, the intended value  is NULL
                return "NULL"
            value = value[0]
            value_type = type(value)

        if value_type == types.IntType or value_type == types.LongType:
            value = str(value)
        elif value_type == types.BooleanType:
            if value == True:
                value = "1"
            else:
                value = "0"
        elif value_type == types.ListType:
            value = value[0]
            value = value.replace("'", "''")
        elif value_type == types.MethodType:
            raise SqlException("Value passed in was an <instancemethod>")
        elif value_type in [types.FloatType, types.IntType]:
            pass
        elif isinstance(value, basestring) or value_type in [types.StringTypes]:
            value = value.replace("'", "''")
        elif isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
            value = str(value)
        elif isinstance(value, object):
            # NOTE:
            # Keep objects as they are ... this is for NoSQL which can take
            # objects ... however, this may need to be checked using
            # DatabaseImpl
            value = str(value)
        else:
            try:
                value = value.replace("'", "''")
            except Exception:
                #raise SqlException("Error with quoting [%s]" % value)
                print("WARNING: set_value(): ", value)
                print("type: ", type(value))
                raise

        if has_outside_quotes:
            if unicode_escape:
                return "N'%s'"% value
            else:
                return "'%s'" % value
        elif escape:
            # this is more for postgres.. If other db impl needs it, it can be added to DatabaseImpl
            return "E'%s'"% value
        else:
            return value
    quote = staticmethod(quote)


    # FIXME: this is highly PostgreSQL dependent
    def copy_table_schema(self, from_table, to_table):
        '''dump the table to a file.  This is pretty messy, but I couldn't
        find a better way to do this'''
        tmp_dir = Environment.get_tmp_dir()
        file_path = "%s/temp/%s__%s.sql" % (tmp_dir,self.database_name,from_table)
        if os.path.exists(file_path):
            os.unlink(file_path)
        if os.path.exists(file_path+".tmp"):
            os.unlink(file_path+".tmp")

        # find the schema
        if from_table.find(".") != -1:
            from_schema, from_table = from_table.split(".")
        else:
            from_schema = "public"

        if to_table.find(".") != -1:
            to_schema, to_table = to_table.split(".")
        else:
            to_schema = "public"

        # dump the table to a file
        cmd ="pg_dump -h %s -U %s -p %s -s --schema %s -t %s %s > %s" % \
            (self.host, self.user, self.port, from_schema, from_table, \
            self.database_name, file_path)

        os.system(cmd)

        # convert the name of the from table to the to_table
        file1 = open(file_path, "r")
        file2 = open(file_path+".tmp", "w")

        for line in file1.readlines():
            line = line.replace("search_path = %s" % from_schema, \
                                "search_path = %s" % to_schema)
            line = line.replace(from_table, to_table)
            file2.write(line)

        file1.close()
        file2.close()

        # read the file back in
        os.system("psql -e -h %s -U %s -p %s %s < %s" % \
              (self.host, self.user, self.port, self.database_name, file_path+".tmp") )

        os.unlink(file_path)
        os.unlink(file_path+".tmp")



    # some database introspection tools: note that a different module
    # is used here because it appears that pgdb (which is DB-API 2.0 compliant)
    # does not support database introspection (not sure why not)
    def get_tables(self):
        db_resource = self.get_db_resource()
        #key = "Sql:%s:tables"% db_resource
        #tables = Container.get(key)
        #if tables != None:
        #    return tables

        table_info = self.database_impl.get_table_info(db_resource)

        tables = table_info.keys()
        #Container.put(key, tables)
        return tables



    def clear_table_cache(cls, database=None):
        #if not database:
        #    database = Project.get().get_database_name()
        #key = "Sql:%s:tables"% database
        #Container.remove(key)
        DatabaseImpl.clear_table_cache()
    clear_table_cache = classmethod(clear_table_cache) 


    def table_exists(self, table):
        db_resource = self.get_db_resource()
        return self.database_impl.table_exists(db_resource, table)




class DbResource(Base):
    '''Define a database resource.  It contains the necessary
    information required to connect to a particular database'''

    DBRESOURCE_ID = 'DbResource'


    def __init__(self, database, host=None, port=None, vendor=None, user=None, password=None, **options):
        # MySQL does allow empty.  This is needed to create a database
        if vendor != "MySQL":
            assert database
        self.database = database
        self.host = host
        self.port = port
        self.vendor = vendor
        if not self.vendor:
            self.vendor = Sql.get_default_database_type()


        # check to see if vendor is supported
        try:
            impl = DatabaseImpl.get(self.vendor)
            if self.vendor not in VENDORS:
                VENDORS.append(self.vendor)
                DATABASE_DICT[self.vendor] = impl.get_module()
        except Exception as e:
            assert self.vendor in VENDORS

        self.user = user
        self.password = password

        # database specific extra options
        self.options = options

        if not self.host:
            self.host = Config.get_value("database", "server")
        if not self.host:
            self.host = 'localhost'


        # Fill in the defaults
        if self.vendor == 'MySQL':
            if not self.user:
                self.user = "root" 
        elif self.vendor == 'PostgreSQL':
            if not self.user:
                self.user = "postgres" 
            if not self.port:
                self.port = '5432'
        


    def __str__(self):
        return "DbResource:%s:%s:%s:%s" % (self.vendor, self.host, self.port, self.database)

    def get_database(self):
        return self.database

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_vendor(self):
        return self.vendor

    def get_user(self):
        return self.user

    def get_password(self):
        return self.password

    def get_key(self):
        if self.host:
            return "%s:%s:%s:%s" % (self.vendor, self.host, self.port, self.database)
        else:
            return self.database

    def get_database_type(self):
        return self.vendor


    def get_database_impl(self):
        impl = DatabaseImpl.get(self.vendor)
        return impl

    
    def exists(self):
        return self.get_database_impl().database_exists(self)


    def get_sql(self):
        return DbContainer.get(self)


    def get_search(self, table):
        from pyasm.search import Search
        search = Search.get_search_by_db_resource(self, table)
        return search



    def get_by_code(code, database):
        from pyasm.search import Search
        db_resource_sobj = Search.get_by_code("sthpw/db_resource", code)

        host = db_resource_sobj.get_value("host")
        port = db_resource_sobj.get_value("port")
        vendor = db_resource_sobj.get_value("vendor")
        user = db_resource_sobj.get_value("login")
        password = db_resource_sobj.get_value("password")

        db_resource = DbResource(database, host=host, port=port, vendor=vendor, user=user, password=password)
        return db_resource

    get_by_code = staticmethod(get_by_code)



    def clear_cache(cls):
        key = "Project:db_resource_cache"
        Container.put(key, None)
    clear_cache = classmethod(clear_cache)


    def get_default(cls, database, use_cache=True, use_config=False):
        # evaluate ticket
        #ticket = Environment.get_ticket()
        ticket = ""


        from pyasm.security import Site
        site_obj = Site.get()
        site = None
        if ticket:
            site = site_obj.get_by_ticket(ticket)
        if not site:
            site = site_obj.get_site()

        if site:
            key = "Project:db_resource_cache:%s" % site
        else:
            key = "Project:db_resource_cache"

        # NOTE: this should be moved DatabaseImpl
        if use_cache:
            #key = "Project:db_resource:%s"%database
            #db_resource = Container.get(key)
            #if db_resource != None:
            #    return db_resource

            db_resource_dict = Container.get(key)
            if not db_resource_dict:
                db_resource_dict = {}
                Container.put(key, db_resource_dict)

            db_resource = db_resource_dict.get(database)
            if db_resource != None:
                return db_resource


        data = None
        if not use_config and site:
            data = site_obj.get_connect_data(site)
            if data:
                host = data.get('host')
                port = data.get('port')
                vendor = data.get('vendor')
                user = data.get('user')
                password = data.get('password')

        # get the defaults
        if not data:
            host = Config.get_value("database", "host")
            port = Config.get_value("database", "port")
            vendor = Config.get_value("database", "vendor")
            user = Config.get_value("database", "user")

            #password = Config.get_value("database", "password")
            password = DbPasswordUtil.get_password()


        db_resource = DbResource(database, host=host, port=port, vendor=vendor, user=user, password=password)
        if use_cache:
            db_resource_dict[database] = db_resource


        return db_resource
    get_default = classmethod(get_default)



    def is_instance(inst):
        '''return True if it is an instance of DbResource'''
        if hasattr(inst, 'DBRESOURCE_ID'):
            return True
        else:
            return False
    is_instance = staticmethod(is_instance)





class DbContainer(Base):
    '''Class which maintains a pool of all of the connections
    to the database.  This allows global access to these
    connections from anywhere in the application'''


    def register_connection(sql):
        '''register the connection in the Transaction'''
        transaction = Transaction.get()
        if transaction and transaction.is_in_transaction():
            transaction.register_database(sql)
    register_connection = staticmethod(register_connection)

    # static function
    def get(cls, db_resource, connect=True):
        '''Get a connection the database.  This will reuse connections that
        are already open.
        
        @params
        db_resource - data structure with information to connect
        connect - flag to determine whether the Sql object returned should
            autoconnect

        @return:
        object - Sql object
        '''

        # STRICT ENFORCEMENT to ensure that only DbResources come through
        from sql import DbResource
        assert db_resource != None
        if db_resource != "sthpw":
            #print("DBCONTAINER what is", db_resource, type(db_resource))
            assert DbResource.is_instance(db_resource)
        else:
            db_resource = DbResource.get_default("sthpw")


        sql = cls.get_connection_pool_sql(db_resource)

        if sql and sql.get_connection():
            DbContainer.register_connection(sql) 

        # delete of Unittest environment requires this to be commented out
        #assert sql.get_connection()
        return sql

    get = classmethod(get)


    #
    # sql pooling methods
    #
    #session_sql_dict = {}
    #session_time_dict = {}
    #session_max_lifespan = 60 

    if Sql.get_default_database_type() == 'Sqlite':
        # Sqlite cannot share connections across threads
        pool_max_connections = 0
    else:
        pool_max_connections = Config.get_value("database", "pool_max_connections")
    if pool_max_connections != 0 and not pool_max_connections:
        pool_max_connections = 0
    else:
        pool_max_connections = int(pool_max_connections)


    # global connection pool
    connection_pool = {} 

    def get_global_connection_pool(cls):
        '''gets the global connection pool. Do not use this data structure
        for anything but diagnostic purposes'''
        return cls.connection_pool
    get_global_connection_pool = classmethod(get_global_connection_pool)


    def close_all_global_connections(cls):
        '''This doesn't close all of them in high volume because it is
        rather a simple implementation, however in periods of low volume,
        it should close all connections'''
        connection_pool = cls.get_global_connection_pool()
        for database, connections in connection_pool.items():
            number = len(connections)
            for i in range(0, number):
                sql = cls.get_connection_pool_sql(database)
                sql.close()
    close_all_global_connections = classmethod(close_all_global_connections)


    def get_connection_pool(cls):
        thread_pool = Container.get("DbContainer::thread_pool")
        return thread_pool
    get_connection_pool = classmethod(get_connection_pool)


    def get_connection_pool_sql(cls, db_resource):
        if DbResource.is_instance(db_resource):
            database_key = db_resource.get_key()
        else:
            database_key = db_resource

        # get from stored sqls in this thread
        thread_pool = Container.get("DbContainer::thread_pool")
        if thread_pool == None:
            thread_pool = {}
            Container.put("DbContainer::thread_pool", thread_pool)

        sql = thread_pool.get(database_key)
        if sql:
            return sql


        # otherwise get it from the connection pool.
        global_pool = cls.connection_pool.get(database_key)
        if global_pool == None:
            lock = thread.allocate_lock()
            lock.acquire()

            # check once again ( thread safe ) and create a new one if it doesn't exist

            global_pool = cls.connection_pool.get(database_key)
            if global_pool == None:
                # create a new global pool
                global_pool = []
                cls.connection_pool[database_key] = global_pool

            lock.release()
        
        # if the pool is empty, then open a new database connection
        lock = thread.allocate_lock()
        #lock = Lock()
        lock.acquire()

        sql = None
        try:
            if not global_pool:

                # before making a connection, make sure the user is even
                # allowed to do so based on site locking
                """
                ticket = Environment.get_ticket()
                site = "foo"
                host = "localhost"
                port = "5432"
                if db_resource.get_port() != port:
                    raise SQLException("Denied access to [%s]" % db_resource)
                if db_resource.get_host() != host:
                    raise SQLException("Denied access to [%s]" % db_resource)
                """

                sql = Sql(db_resource)
                sql.connect()

            else:

                # otherwise reuse one from the pool
                sql = global_pool.pop()
                #import thread as xx
                #print("CONNECT: reuse: ", database_key, sql, xx.get_ident())


            # remember for this thread
            thread_pool[database_key] = sql
        finally:
            lock.release()

        assert sql.get_connection()
        return sql
        
    get_connection_pool_sql = classmethod(get_connection_pool_sql)


    def close_thread_sql(cls):
        # abort all of the open connections in this thread
        thread_pool = Container.get("DbContainer::thread_pool")
        if not thread_pool:
            return
        for database_key, sql in thread_pool.items():
            sql.close()
        # clear the thread pool
        Container.put("DbContainer::thread_pool", {})
    close_thread_sql = classmethod(close_thread_sql)



    def commit_thread_sql(cls):
        
        # commit all of the open connections in this thread
        thread_pool = Container.get("DbContainer::thread_pool")
        if not thread_pool:
            return
        for database_key, sql in thread_pool.items():
            try:
                sql.commit()
                
            except Exception as e:
                print("WARNING: When trying to commit: ", e)
                del(thread_pool[database_key])
            finally:
                sql.close()

        # clear the thread pool
        Container.put("DbContainer::thread_pool", {})
    commit_thread_sql = classmethod(commit_thread_sql)



    def abort_thread_sql(cls, force=False):
        # abort all of the open connections in this thread
        thread_pool = Container.get("DbContainer::thread_pool")
        if not thread_pool:
            return
        for database_key, sql in thread_pool.items():
            try:
                sql.rollback(force=force)
            finally:
                sql.close()
        # clear the thread pool
        Container.put("DbContainer::thread_pool", {})
    abort_thread_sql = classmethod(abort_thread_sql)


    def release_thread_sql(cls):
        # release all of the open connections back to the pool
        #print("releasing: ", thread.get_ident())


        lock = Lock()
        lock.acquire()

        try:
            thread_pool = Container.get("DbContainer::thread_pool")
            if not thread_pool:
                return

            for database_key, sql in thread_pool.items():
                # failsafe commit. When a db is not available, there is nothing to commit
                # NOTE: implemented in 4.0
                try:
                    sql.commit()
                except SqlException as e:
                    print("WARNING: ", e.__str__())
                # Do not pool sqlite. SQLite does not like sharing connection
                # amongst threads
                if sql.get_database_type() == 'Sqlite':
                    sql.close()
                    continue

                # close any transactions
                global_pool = cls.connection_pool.get(database_key)

                if len(global_pool) < cls.pool_max_connections:
                    # return the sql connection to the pool
                    global_pool.append(sql)
                else:
                    # if the global pool is greater than a maximum / thread,
                    # just release it completely
                    sql.close()


            # clear the thread pool
            Container.put("DbContainer::thread_pool", {})

        finally:
            lock.release()

    release_thread_sql = classmethod(release_thread_sql)



    def remove(database_name):
        '''remove a connection to the database'''
        sql_dict = DbContainer._get_sql_dict()
        if sql_dict.has_key(database_name):
            sql_dict[database_name].close()
            del sql_dict[database_name]
    remove = staticmethod(remove)



    def rollback_all():
        '''rollback all connection to all databases'''
        sqls = Container.get("DbContainer:sql_seq")
        if sqls == None:
            return
        for sql in sqls:
            sql.rollback(force=True)
    rollback_all = staticmethod(rollback_all)


    def close_all():
        '''closes all connection to all databases'''
        sql_seq = Container.get_seq("DbContainer:sql_seq")
        for sql in sql_seq:
            sql.close()
        Container.put("DbContainer:sql_seq", [] )
        Container.put("DbContainer:sql_dict", {} )

        DbContainer.release_thread_sql()

    close_all = staticmethod(close_all)

    
    def _get_sql_dict():
        # get the connection from a container
        cache_name = "DbContainer:sql_dict"
        sql_dict = Container.get(cache_name)
        if sql_dict == None:
            sql_dict = {}
            Container.put(cache_name, sql_dict)
        return sql_dict
    _get_sql_dict = staticmethod(_get_sql_dict)

    def _reset_sql_dict():
        cache_name = "DbContainer:sql_dict"
        Container.put(cache_name, {})
    _reset_sql_dict = staticmethod(_reset_sql_dict)




class DbPasswordUtil(object):
    PASSWORD_KEY = (95954739753557611717677953802022772164074845338566937775470833735856469435381956125590339095236470675423085325686058278198918822369603350495319710499101888408708913117761396293217495020971217519968381713929946123203701342525363284439548065832975303252596220333775984191691412558233438061248397074525660377441L, 65537L, 86459851563652350384550994520912595050627092587897749508172538776108095169113253171923656930465295425867586777734914833516983601607791279024819865791735409407082275562168885331872720365063141292194732294024919434643862338969598324336994436079024289458730635475133273691824108450263457154881428072573317615473L)


    def get_password(cls):
        coded = Config.get_value("database", "password")

        """
        if Config.get_value("database", "vendor") == 'SQLServer':
            print("WARNING: SQLServer implementation does not support encoded keys for database passwords")
            return coded
        """
        if not coded or coded == "none":
            return ""

        if len(coded) < 64:
            return coded

        from pyasm.security import CryptoKey
        key = CryptoKey()
        key.set_private_key(cls.PASSWORD_KEY)

        password = key.decrypt(coded)

        return password
    get_password = classmethod(get_password)



    def set_password(cls, password):

        if password == "__EMPTY__":
            coded = ""
        else:
            from pyasm.security import CryptoKey
            key = CryptoKey()
            key.set_private_key(cls.PASSWORD_KEY)

            coded = key.encrypt(password)

        Config.set_value("database", "password", coded)


    set_password = classmethod(set_password)





# class that dynamically creates an select statement

class Select(object):
    '''A class to non-linearly build up an sql select statement'''

    def __init__(self):
        self.tables = []
        self.id_col = 'id'
        self.columns = []
        self.as_columns = []
        self.column_tables = []
        self.wheres = []
        self.filters = {}
        self.raw_filters = []
        self.filter_mode = "AND"
        self.group_bys = []
        self.havings = []
        self.order_bys = []
        self.order_by_columns = []
        self.limit = None
        self.offset = 0
        self.distinct = False
        self.distinct_col = None
        self.joins = []
        self.join_tables = set()

        # optional database knowledge
        self.sql = None
        self.database = None
        self.db_resource = None
        self.column_types = {}
        self.impl = DatabaseImpl.get()

        self.statement = None
        
        self.set_statement = None

        self.schema = ""

        self.quoted_mode = None


    def copy(self):
        select = Select()

        select.tables = self.tables[:]
        select.id_col = self.id_col
        select.columns = self.as_columns[:]
        select.column_tables = self.column_tables[:]
        select.wheres = self.wheres[:]
        select.filters = self.filters.copy()
        select.raw_filters = self.raw_filters[:]
        select.filter_mode = self.filter_mode
        select.group_bys = self.group_bys[:]
        select.havings = self.havings[:]
        select.order_bys = self.order_bys[:]
        select.order_by_columns = self.order_by_columns[:]
        select.limit = self.limit
        select.offset = self.offset
        select.distinct = self.distinct
        select.distinct_col = self.distinct_col
        select.joins = self.joins
        select.join_tables = self.join_tables.copy()

        select.schema = self.schema
        select.sql = self.sql
        select.database = self.database
        select.db_resource = self.db_resource
        select.impl = self.impl
        select.set_statement = self.set_statement


        return select


    def dumps(self):

        select = {}

        select['tables'] = self.tables[:]
        select['id_col'] = self.id_col
        select['columns'] = self.as_columns[:]
        select['column_tables'] = self.column_tables[:]
        select['wheres'] = self.wheres[:]
        select['filters'] = self.filters.copy()
        select['raw_filters'] = self.raw_filters[:]
        select['filter_mode'] = self.filter_mode
        select['group_bys'] = self.group_bys[:]
        select['havings'] = self.havings[:]
        select['order_bys'] = self.order_bys[:]
        select['order_by_columns'] = self.order_by_columns[:]
        select['limit'] = self.limit
        select['offset'] = self.offset
        select['distinct'] = self.distinct
        select['distinct_col'] = self.distinct_col
        select['joins'] = self.joins

        # This is a set ... cannot be json
        #select['join_tables'] = self.join_tables.copy()

        select['schema'] = self.schema
        #select['sql'] = self.sql
        select['database'] = self.database
        #select['db_resource'] = self.db_resource
        #select['impl'] = self.impl
        select['set_statement'] = self.set_statement

        return jsondumps(select)



    def loads(self, data):

        data = jsonloads(data)

        select = self

        select.tables = data.get("tables") or []
        select.id_col = data.get("id_col")
        select.columns = data.get("as_columns") or []
        select.column_tables = data.get("column_tables") or []
        select.wheres = data.get("wheres") or []
        select.filters = data.get("filters") or []
        select.raw_filters = data.get("raw_filters") or []
        select.filter_mode = data.get("filter_mode")
        select.group_bys = data.get("group_bys") or []
        select.havings = data.get("havings") or []
        select.order_bys = data.get("order_bys") or []
        select.order_by_column = data.get("order_by_columns") or []
        select.limit = data.get("limit")
        select.offset = data.get("offset")
        select.distinct = data.get("distinct")
        select.distinct_col = data.get("distinct_col")
        select.joins = data.get("joins") or []

        # This.s a set ... cannot be json
        #select.join_tables = data.get("join_tables")

        select.schema = data.get("schema")
        #select.sql = data.sql
        select.database = data.get("database")
        #select.db_resource = data.db_resource
        #select.impl = data.impl
        select.set_statement = data.get("set_statement")




    def execute(self, sql=None):
        '''Actually execute the statement'''
        if not sql:
            sql = self.sql
        if not sql:
            raise SqlException("No connector found to execute query")

        conn = sql.get_connection()
        db_resource = sql.get_db_resource()
        vendor = db_resource.get_vendor()

        if vendor == "MongoDb":
            impl = db_resource.get_database_impl()
            results = impl.execute_query(sql, self)

        else:

            statement = self.get_statement()
    
            # remember the cursor (needed for savepoints)
            self.cursor = conn.cursor()
            self.cursor.execute(statement)

            results = self.cursor.fetchall()
            self.cursor.close()

        return results


    def execute_count(self, sql=None):
        if not sql:
            sql = self.sql
        if not sql:
            raise SqlException("No connector found to execute query")

        conn = sql.get_connection()
        db_resource = sql.get_db_resource()
        vendor = db_resource.get_vendor()

        if vendor == "MongoDb":
            # TODO: slow
            results = self.execute()
            results = len(results)

        else:
            statement = self.get_count()
            results = sql.do_query(statement)
            if results:
                results = int(results[0][0])
            else:
                results = 0

        return results





    def __str__(self):
        return self.get_statement()


    def set_database(self, database):

        assert database == "sthpw" or not isinstance(database, basestring)

        if isinstance(database, basestring):
            self.sql = DbContainer.get(database)
            self.db_resource = DbResource.get_default(database)
        #elif isinstance(database, DbResource):
        elif DbResource.is_instance(database):
            self.sql = DbContainer.get(database)
            self.db_resource = database
            # set to database string internally
            database = database.get_database()
        elif isinstance(database, Sql):
            self.sql = database
            database = self.sql.get_database_name()
            self.db_resource = self.sql.get_db_resource()
        else:
            # NOTE: sometimes an object that is sql.Sql is not detected
            # by the above condition.  Note sure why, but this warning
            # becomes intrusive
            #print("WARNING: it should be Sql instance, but it is not detected as such")
            self.sql = database
            database = self.sql.get_database_name()
            self.db_resource = DbResource.get_default(database)
            

        self.database = database
        self.impl = self.sql.get_database_impl()

        database_type = self.impl.get_database_type()
        if database_type == 'PostgreSQL':
            self.schema = "public"
        elif database_type == 'SQLServer':
            self.schema = "dbo"
        elif database_type == 'Sqlite':
            self.database = None

    def set_statement(self, statement):
        '''special function which allows you to put in an arbitrary sql
        statement and dynamically add operations to it.  There are limitations
        to this'''
        self.tables.append("( %s )" % statement)
        self.set_statement = statement


    
    def add_table(self, table):
        if table == "": return
        self.tables.append(table)

    def get_tables(self):
        return self.tables
        
    def get_table(self):
        return self.tables[0]
    
    def set_id_col(self, id_col):
        self.id_col = id_col

    def add_join(self, table1, table2=None, column=None, column2=None, join="LEFT OUTER", database=None, database2=None):
        '''
        SELECT *
        FROM "job"

        RIGHT OUTER JOIN "request"
        ON "request
        '''
        join = join.upper()
        assert join in ['LEFT OUTER', 'INNER', 'RIGHT OUTER']

        if not table2:
            table2 = table1
            table1 = self.tables[0]

        # ensure that the join only occurs once
        if table1 in self.join_tables:
            return
        self.join_tables.add(table1)


        if column and column2:
            column1 = column
        elif not column:
            column1 = "%s_id" % table2
            columns =  self.impl.get_column_info(self.db_resource, table1).keys()
            if column1 not in columns:
                column1 = "id"
                column2 = "%s_id" % table1
            else:
                column2 = "id"
        else:
            column1 = column
            column2 = "id"

        # handle the database scoping
        if not database:
            database1 = self.database
        else:
            database1 = database
        parts = []
        if database1:
            parts.append('"%s"' % database1)
        if self.schema:
            parts.append('"%s"' % self.schema)
        prefix1 = ".".join(parts)

        if prefix1:
            prefix1 = "%s." % prefix1
 

        # handle the database scoping
        if not database2:
            database2 = self.database
        parts = []
        if database2:
            parts.append('"%s"' % database2)
        if self.schema:
            parts.append('"%s"' % self.schema)
        prefix2 = ".".join(parts)
 
        # add a trailing point.  this is needed so that implementations with
        # not prefix can be accomodated (ie: Sqlite)
        if prefix2:
            prefix2 = "%s." % prefix2
 

        expr = '''%s JOIN %s"%s" ON "%s"."%s" = "%s"."%s"''' % (join, prefix2, table2, table1, column1, table2, column2)

        if self.impl.get_database_type() == 'SQLServer':
            expr = '''%s JOIN %s"%s" ON "%s"."%s" = %s"%s"."%s"''' % (join, prefix2, table2, table1, column1, prefix2, table2, column2)
        # NOTE: there should be no need to database specfic joins
        """
        if self.impl.get_database_type() == 'Oracle':
            # do fully qualified table names (i.e. include schema prefix) for Oracle SQL ... needed
            # for use with set-ups that use a service user to access the Oracle DB
            schema = self.database
            expr = '''%s JOIN %s."%s" ON %s."%s"."%s" = %s."%s"."%s"''' % \
                    (join, schema, table2, schema, table1, column1, schema, table2, column2)
        elif self.impl.get_database_type() == 'SQLServer':
            expr = '''%s JOIN [%s] ON [%s].[%s] = [%s].[%s]''' % \
                (join, table2, \
                table1, column1, \
                table2, column2)
        else:
            expr = '''%s JOIN "%s" ON "%s"."%s" = "%s"."%s"''' % (join, table2, table1, column1, table2, column2)
        """

        self.joins.append(expr)


    def set_quoted_mode(self, mode):
        self.quoted_mode = mode


    def add_column(self, column, distinct=False, table=None, as_column=None):
        if (column == "" or column in self.columns) and column != '*':
            return
        # This doesn't make sense, comment out for now
        # SQL Server specific: We automatically add the ID column as the sequence.
        # Prevent adding the ID column again.
        #if column == 'id':
        #    return
        self.columns.append(column)
        self.as_columns.append(as_column)

        if table:
            self.column_tables.append(table)
        else:
            self.column_tables.append(self.tables[0])

        if distinct:
            self.distinct_col = column

        self.distinct = distinct


    def set_distinct_col(self, column):
        self.distinct = True
        self.distinct_col = column



    def get_columns(self):
        columns = []
        for column, as_column in zip(self.columns, self.as_columns):
            if as_column:
                columns.append(as_column)
            else:
                columns.append(column)

        return columns


    def set_filter_mode(self, mode):
        assert mode in ['and', 'or']
        self.filter_mode = mode.upper()



    def add_where(self, where):
        self.wheres.append(where)



    def add_op(self, op, idx=None):
        assert op in ['and', 'or', 'begin']
        if idx == None:
            # TODO: determine if this is needed later
            #if self.wheres and op != "begin" and self.wheres[-1] == "begin":
            #    self.wheres.pop()
            #else:
            #    self.wheres.append(op)
            self.wheres.append(op)
        else:
            self.wheres.insert(idx, op)


    def get_wheres(self):
        return self.wheres

    def remove_where(self, where):
        try:
            self.wheres.remove(where)
        except:
            pass


    def _convert_to_database_boolean(self, value):
        if not self.impl.get_database_type() == 'SQLServer':
            return value

        if value == 'true' or value == 'TRUE':
            return '1'
        else:
            if value == 'false' or value == 'FALSE':
                return '0'
        return value

    def add_filter(self, column, value, column_type="", op='=', quoted=None, table=''):
        assert self.tables

        # store all the raw filter data
        self.raw_filters.append( {
                'column': column,
                'value': value,
                'column_type': column_type,
                'op': op,
                'quoted': quoted,
                'table': table
        } )



        if self.quoted_mode == "none":
            where = "%s %s '%s'" % (column, op, value)
            self.add_where(where)
            return




        if not table:
            table = self.tables[0]

        if column == 'id' and value == None:
            where = "\"%s\".\"%s\" is NULL" % (table, column)
            self.add_where(where)
            return

        if value == None:
            where = "\"%s\".\"%s\" is NULL" % (table, column)
            self.add_where(where)
            return

        if quoted == "column":
            value = '"%s"' % value
            quoted = False



        # This check added to handle cases where a list is empty,
        # as 'value[0]' is not defined in that case. We assume in this
        # case that the intended value is NULL
        if type(value) == types.ListType and len(value) == 0:
            where = "\"%s\" is NULL" % column
            self.add_where(where)
            return


        # on simple building of select statements, db_resource could be null
        if not self.db_resource:
            column_type = "varchar"
        elif not column_type:
            column_types = self.impl.get_column_types(self.db_resource, self.tables[0])
            column_type = column_types.get(column)


        # if quoted is not explicitly set
        if quoted == None:
            quoted = True

            if not column_type and self.sql:
                # get column type from database
                column_types = self.impl.get_column_types(self.db_resource, self.tables[0])
                column_type = column_types.get(column)

            info = self.impl.process_value(column, value, column_type)

            if info:
                value = info.get("value")
                value = self._convert_to_database_boolean(value)
                quoted = info.get("quoted")
            else:
                quoted = True


        if quoted:
            value = Sql.quote(value)

        if table:
            where = "\"%s\".\"%s\" %s %s" % (table, column, op, value)
        else:
            where = "\"%s\" %s %s" % (column, op, value)
        self.add_where(where)



    def add_filters(self, column, values, table='', op='in'):

        quoted = False
        column_type = ''

        # store all the raw filter data
        self.raw_filters.append( {
                'column': column,
                'value': values,
                'column_type': column_type,
                'op': op,
                'quoted': quoted,
                'table': table
        } )

        assert op in ['in', 'not in', '@@']


        if op == "@@":
            # full text search requires that the filters be added one by one
            self.add_op("begin")
            for value in values:
                self.add_filter(column, value, table, op)
            self.add_op("or")
            return



        if op == "@@":
            # full text search requires that the filters be added one by one
            self.add_op("begin")
            for value in values:
                self.add_filter(column, value, table, op)
            self.add_op("or")
            return



        if not table:
            table = self.tables[0]


        filter = ''
        if not values or values == ['']:
            if table:
                where = '"%s"."%s" is NULL' % (table, self.id_col)
            else:
                where = "%s is NULL" %self.id_col
        else:
            list = [ Sql.quote(value) for value in values ]
            if table:
                where = '"%s"."%s" %s (%s)' % ( table, column, op, ", ".join(list) )
            else:
                where = '"%s" %s (%s)' % ( column, op, ", ".join(list) )

        self.add_where(where)



    def add_group_aggregate_filter(self, group_cols, column='id', aggregate='max'):
        '''This does a co-related subselect which finds the result of an
        aggregate function over a list of grouped columns

        Searching for the max version for each context of a snapshot.
        This is called by:

        select.add_group_aggregate_filter(['search_type','search_id','context'], "version")

        This producess the following sql:

        select * from snapshot where version = (select max(version) from snapshot as f where f.search_type = snapshot.search_type and f.search_id = snapshot.search_id and f.context = snapshot.context) order by search_type, search_id;

        Reference:
        http://www.xaprb.com/blog/2006/12/07/how-to-select-the-firstleastmax-row-per-group-in-sql/

        '''
        if not group_cols:
            return

        if isinstance(group_cols, basestring):
            group_cols = [group_cols]

        table = self.get_table()

        # have to build the sql from scratch because Select can't handle
        # the complexity required
        subselect = []
        subselect.append( "SELECT")
        # NOTE: note allowed to scope by table in aggregate (Postgresql)
        #subselect.append( '%s("%s"."%s")' % (aggregate, table, column) )
        subselect.append( '%s("%s")' % (aggregate, column) )
        subselect.append( "FROM")

        if self.impl.get_database_type() == 'SQLServer':
            subselect.append( '[%s] as xxx' % table)
        else:
            subselect.append( '"%s" as xxx' % table)

        subselect.append( "WHERE")

        wheres = []
        for group_col in group_cols:
            
            if self.impl.get_database_type() == 'SQLServer':
                #wheres.append( 'xxx."%s" = %s.[%s].[%s]' % (group_col, self.database, table, group_col))
                wheres.append( 'xxx."%s" = [%s].[%s]' % (group_col, table, group_col))
            else:
                wheres.append( 'xxx."%s" = "%s"."%s"' % (group_col, table, group_col))


        wheres = " AND ".join(wheres)
        subselect.append(wheres)

        statement = " ".join(subselect)

        if  self.impl.get_database_type() == 'SQLServer':
            self.add_where('[%s].[%s] = (%s)' % (table, column, statement))
        else:
            self.add_where('"%s"."%s" = (%s)' % (table, column, statement))

    # Full text search filtering
    # NOTE: Only Postgres and SQLServer impl so far.  This likely will not work
    # on any other database
    #
    def add_text_search_filter(self, column, keywords, table=None, op='&'):
        '''This will do full text searching on any column.  It is pretty
        brute force as it will convert each row to a ts_vector.
        '''
        if not table:
            # usually it's the only table in the list
            table = self.tables[0]
        column_types = self.impl.get_column_types(self.db_resource, table)
        column_type = column_types.get(column)
        
        where = self.impl.get_text_search_filter(column, keywords, column_type, table=table, op=op)
        self.add_where(where)



    def add_select_filter(self, column, select, op='in', table=''):
        '''combines results of one search filter with another search filter
        as a subselect

        example:

        SELECT * FROM "request" WHERE "id" in ( SELECT "request_id" FROM "job" WHERE "code" = '123MMS' )
        '''
        assert op in ['in','not in']
        statement = select.get_statement()
        self.add_filter(column, "( %s )" % statement, op=op, quoted=False, table=table)


    def add_group_by(self, group_by):
        if group_by == "": return
        self.group_bys.append(group_by)

    def add_having(self, having):
        if having == "": return
        self.havings.append(having)
        
    def add_order_by(self, order_by, direction='', table=''):
        if order_by == "": return

        if order_by.find("->") != -1:
            parts = order_by.split(" ")
            parts2 = parts[0].split("->")
            parts2[1] = parts2[1].strip("'")
            order_by = '"%s"->\'%s\'' % (parts2[0], parts2[1])

        elif table:
            order_by = '"%s"."%s"' % (table, order_by)

        # we need to store the order_by_column name to maintain uniqueness so MS SQL doesn't error 
        if direction and not order_by.endswith(' desc') and not order_by.endswith(' asc'):
            if order_by not in self.order_by_columns:
                self.order_by_columns.append(order_by)
            else:
                return
            order_by = '%s %s' % (order_by, direction)
        
        elif order_by.endswith(' desc') or order_by.endswith(' asc'):
            tmps = order_by.split(' ')
            if tmps[0] not in self.order_by_columns:
                self.order_by_columns.append(tmps[0])
            else:
                return
        else: # for cases when asc is not specified (implied)
            if order_by not in self.order_by_columns:
                self.order_by_columns.append(order_by)
            else:
                return


        if order_by not in self.order_bys:
            self.order_bys.append(order_by)


    def add_enum_order_by(self, column, values, table=''):
        '''orders by a list of values.
        takes a list of values and creates a case statement out of it'''
        if not values:
            return

        expr = []
        if table:
            expr.append( "( CASE \"%s\".\"%s\"" % (table,column) )
        else:
            expr.append( "( CASE \"%s\"" % column )

        count = 1
        for value in values:
            if type(value) in types.StringTypes:
                value = "'%s'" % value
            expr.append( "WHEN %s THEN %d " % (value, count) )
            count += 1
        expr.append("ELSE %d END )" % count )
        self.add_order_by( "\n".join(expr) )


    def add_limit(self, limit):
        '''deprecated: use set_limit'''
        self.limit = limit

    def set_limit(self, limit):
        self.limit = limit

    def set_offset(self, offset):
        self.offset = offset

    def get_statement(self, mode="normal"):
        if self.set_statement:
            return self.set_statement

        if self.impl:
            database_type = self.impl.get_database_type()
        else:
            database_type = Sql.get_default_database_type()


        # setup regex searches for direction (ascending or descending) of sort order (ignoring case)
        regex_asc = re.compile(' asc$', re.I)
        regex_desc = re.compile(' desc$', re.I)
        
        statement = []
        statement.append("SELECT");


        is_oracle = False
        if database_type == 'Oracle' and self.tables[0] not in ['USER_OBJECTS','ALL_TABLES']:
            is_oracle = True

        if mode == "count":
            if database_type=='PostgreSQL' and self.distinct_col:
                statement.append("count(DISTINCT %s)"%self.distinct_col)
            else:
                statement.append("count(*)")
        elif mode == "normal":
            if database_type =='SQLServer' and self.limit != None:
                total = int(self.limit) + self.offset
                statement.append("TOP %s " %total)
            if not self.columns:
                if is_oracle:
                    expr = '%s."%s".*' % (self.database, self.tables[0])
                    statement.append(expr)
                else:
                    if database_type=='PostgreSQL' and self.distinct_col:
                        statement.append("DISTINCT ON(%s) *"%self.distinct_col)
                    else:
                        #expr = '"%s".*' % (self.tables[0])
                        column_parts = []
                        if self.database:
                            column_parts.append('"%s"' % self.database)
                        if self.schema:
                            column_parts.append('"%s"' % self.schema)
                        column_parts.append('"%s"' % self.tables[0])
                        column_parts.append("*")
                        expr = ".".join(column_parts)

                        statement.append(expr)
            else:
                quoted_cols = []
                for i, column in enumerate(self.columns):
                    #FIXME: distinct in SQLServer should only appear once before the column names
                    if column == self.distinct_col:

                        parts = []
                        if self.database:
                            parts.append('"%s"' % self.database)
                        if self.schema:
                            parts.append('"%s"' % self.schema)
                        parts.append('"%s"' % self.column_tables[i])
                        prefix = ".".join(parts)
                        quoted_col = 'distinct %s."%s"' % (prefix, column)

                        #quoted_col = 'distinct "%s"."%s"' % (self.column_tables[i],column)

                    elif self.quoted_mode == "none":
                        quoted_col = column

                    else:
                        #if column == '*':
                        #    quoted_col ='"%s".*' % (self.column_tables[i])
                        #else:
                        #    quoted_col = '"%s"."%s"' % (self.column_tables[i],column)
                        parts = []
                        if self.database:
                            parts.append('"%s"' % self.database)
                        if self.schema:
                            parts.append('"%s"' % self.schema)
                        parts.append('"%s"' % self.column_tables[i])
                        if column == '*':
                            parts.append(column)
                        else:
                            parts.append('"%s"' % column)
                        quoted_col = ".".join(parts)


                    # handle columns that have different names specified
                    if self.as_columns[i]:
                        quoted_col = "%s as \"%s\"" % (quoted_col, self.as_columns[i])

                    quoted_cols.append(quoted_col)


                statement.append(", ".join(quoted_cols) )

            if database_type =='SQLServer' and self.limit != None:
                order_by = 'ORDER BY id'
                order_bys = []
                for order_by in self.order_bys:
                    if order_by.startswith("( CASE"):
                        order_bys.append(order_by)
                    elif regex_asc.search(order_by) or regex_desc.search(order_by) :
                        parts = order_by.split(" ")
                        parts[0] = parts[0].strip('"')
                        parts[0] = '"%s"' % parts[0]
                        order_bys.append( " ".join(parts) )
                    elif database_type == 'SQLServer':
                        order_by = order_by.strip('"')
                        order_bys.append('"%s"' % order_by)

                if order_bys:
                    order_by = "ORDER BY %s" % ", ".join( order_bys )
                statement.append(", ROW_NUMBER() over(%s) as %s " %(order_by, self.impl.get_temp_column_name()))

        if not self.tables:
            raise SqlException("No tables defined")

        clauses = []
        if self.tables[0].startswith('('):
            clauses.append('FROM %s' % self.tables[0] )
        elif self.database and is_oracle:
            clauses.append("FROM " + ", ".join( ['"%s"."%s"' % (self.database,x) for x in self.tables] ))
        # NOTE: There really is no reason for SQLServer to be different here.
        #elif self.database and database_type == 'SQLServer':
        #    clauses.append("FROM " + ", ".join( ['[%s]' % x for x in self.tables] ))
        else:
            #clauses.append("FROM " + ", ".join( ['"%s"."%s"."%s"' % (self.database,self.schema,x) for x in self.tables] ))

            # build full table string
            tables = []
            for table in self.tables:
                if self.quoted_mode == "none":
                   tables.append(table)
                   continue

                parts = []
                if self.database:
                    parts.append(self.database)
                if self.schema:
                    parts.append(self.schema)
                parts.append(table)
                table = ".".join( ['"%s"' % x for x in parts] )
                tables.append(table)

            clauses.append("FROM " + ", ".join(tables) )


        if self.joins:
            clauses.extend(self.joins)

        if len(self.filters):
            #self.wheres = self.filters.values()
            filters = self.filters.values()
            expanded = []
            for filter in filters:
                if len(filter) == 1:
                    expr = filter[0]
                else:
                    expr = '(%s)' % (' %s ' % self.filter_mode).join(filter)
                expanded.append(expr)
                
            self.wheres = expanded

       
        if len(self.wheres) > 0:
            wheres_copy = self.wheres[:]
            new_expr = self.process_wheres(wheres_copy)
            if new_expr:
                clauses.append("WHERE %s" % new_expr)
       
        #order_bys = []
        if mode == "normal":
            if len(self.group_bys) > 0:
                for item in self.order_bys:
                    if regex_asc.search(item) or regex_desc.search(item):
                        parts = order_by.split(" ")
                        item = parts[0]
                        
                    if item not in self.group_bys:
                        self.group_bys.append(item)

                group_by_stmt = ", ".join( ['"%s"' % x for x in self.group_bys] )
                
                clauses.append("GROUP BY %s" %group_by_stmt )

            if len(self.havings) > 0:
                # these are having expressions, no double quotes
                clauses.append("HAVING %s" % " AND ".join( self.havings ) )
                #clauses.append("HAVING %s" % ", ".join( ['"%s"' % x for x in self.havings] ))
               
            if not self.distinct and len(self.order_bys) > 0:
                order_bys = []
                for order_by in self.order_bys:
                    if order_by.startswith("( CASE"):
                        order_bys.append(order_by)
                    elif regex_asc.search(order_by) or regex_desc.search(order_by) and order_by.find("->") == -1:
                        parts = order_by.split(" ")
                        parts[0] = parts[0].strip('"')
                        parts[0] = '"%s"' % parts[0]
                        order_bys.append( " ".join(parts) )
                    elif database_type == 'SQLServer':
                        order_by = order_by.strip('"')
                        order_bys.append('"%s"' % order_by)

                    else:
                        if order_by.find("->") != -1:
                            order_bys.append('"%s".%s' % (self.tables[0],order_by))
                        elif order_by.find(".") == -1:
                            order_bys.append('"%s"."%s"' % (self.tables[0],order_by))
                        else:
                            order_bys.append(order_by)
                
                clauses.append("ORDER BY %s" % ", ".join( order_bys ))
            
            #if database_type == "PostgreSQL":
            #   page = self.impl.get_page(self.limit, self.offset, self.tables[0]) 
            #   if page:
            #       clauses.append(page)

            if database_type not in ["Oracle", "SQLServer"]:
                page = self.impl.get_page(self.limit, self.offset) 
                if page:
                    clauses.append(page)

                #if self.limit != 0:
                #    clauses.append("LIMIT %s" % self.limit )
                #if self.offset != 0:
                #    clauses.append("OFFSET %s" % self.offset )
 

        clause = " ".join(clauses)
        statement.append(clause)
        statement = " ".join(statement)


        # NOTE: oracle and SQLServer uses the limit in the "where" clause
        # pre-orderg in, so have to do a subselect
        if mode != "count" and self.limit != None:
            if database_type in  ["Oracle",'SQLServer']:
                statement = self.impl.handle_pagination(statement, self.limit, self.offset)
        return statement




    def process_wheres(self, wheres):
        if not wheres:
            return

        # if there is no begin at the beginning, then add one
        if wheres[0] != 'begin':
            wheres.insert(0, "begin")

        # if there is no op at the end, then add "and"
        if wheres[-1].lower() not in ['and','or']:
            wheres.append("and")


        # count the begins and ops .. they must match
        count_begin = 0
        count_op = 0
        for item in wheres:
            if item == 'begin':
                count_begin += 1
            elif item in ['and','or']:
                count_op += 1

        
        if count_begin > count_op:
            wheres.append("and")


        cur_stack = []

        self.stack_index = 0
        while self.stack_index < len(wheres):
            expr = self._handle_stack_item(cur_stack, wheres)
            cur_stack = [expr]

        # strip out the outside brackets

        if not expr:
            return None

        if expr.startswith("( ") and expr.endswith(" )"):
            expr = expr[2:-2]

        return expr




    def _handle_stack_item(self, cur_stack, wheres):

        while 1:
            if self.stack_index >= len(wheres):
                #op = " AND " 
                #expr = "( %s )" % op.join(cur_stack)
                #return expr
                return " AND ".join(cur_stack)

            item = wheres[self.stack_index]
            self.stack_index += 1

            if item == "begin":

                # create a new stack
                new_stack = []
                # add it to the current stack
                cur_stack.append(new_stack)

                # go down a level
                expr = self._handle_stack_item(new_stack, wheres)

                cur_stack.pop()
                if expr:
                    cur_stack.append(expr)

            elif item in ['and','or']:

                # create an expression from the current stack
                if not cur_stack:
                    expr = None
                elif len(cur_stack) == 1:
                    expr = cur_stack[0]
                else:
                    op = " %s " % item.upper()
                    expr = "( %s )" % op.join(cur_stack)

                # we're done with this stack
                # return with the expression
                return expr

            elif item:
                cur_stack.append(item)



    def get_count(self):
        '''special statement that counts how many rows this query would
        return if executed.  This ignores the limit and offset tags'''
        statement = self.get_statement(mode="count")
        return statement


    def get_interval_where(time_interval, name="timestamp"):
        ''' get the where sql statement for search '''
        # this method is used by DateFilterWdg as well
        # handle special case for today
        from pyasm.biz import Project
        impl = Project.get_database_impl()
        database_type = impl.get_database_type()
        time_interval = time_interval.lower()

        # FIXME: put this somehow in implmentation classes
        # Use of Search.get_database_impl().get_timestamp_now() is preferred
        if database_type == "Oracle":
            if time_interval == 'today':
                return "\"%s\" >= TO_TIMESTAMP(SYSDATE)" % name
            else:
                offset, unit = time_interval.split(" ")
                if unit in ["week", "Week"]:
                    unit = "day"
                    offset = int(offset) * 7
                return "\"%s\" >= SYSTIMESTAMP - INTERVAL '%s' %s" % (name, offset, unit)
        elif database_type == "SQLServer":
            if time_interval == 'today':
                return "%s >= CONVERT(date, GETDATE())" % name
                #return "%s >= CAST(FLOOR(CAST ( GETDATE() as FLOAT )) as DATETIME)" % name
            else:
                offset_time, unit = time_interval.split()
                offset = impl.get_timestamp_now(offset=offset_time, type=unit, op='-')
                return "%s >=  %s" %(name, offset)
            """
            elif time_interval.lower() == '1 hour':
                return  '%s >= DATEADD(hour,-1, GETDATE())' %(name)
            elif time_interval.lower() == '1 day':
                return  '%s >= DATEADD(day,-1, GETDATE())' %(name)
            elif time_interval.lower() == '1 week':
                return  '%s >= DATEADD(week,-1, GETDATE())' %(name)
            elif time_interval.lower() == '1 month':
                return  '%s >= DATEADD(month,-1, GETDATE())' %(name)
            """
        elif database_type == 'MySQL':
            if time_interval == 'today':
                return "%s >= CURDATE()" %name
            else:
                offset_time, unit = time_interval.split()
                offset_time = int(offset_time)
                offset = impl.get_timestamp_now(offset=offset_time, type=unit, op='-')
                return "%s >= %s" %(name, offset)
        elif database_type == 'Sqlite':
            if time_interval == 'today':
                return "%s >= date('now')" %name
            else:
                offset_time, unit = time_interval.split()
                offset_time = int(offset_time)
                offset = impl.get_timestamp_now(offset=offset_time, type=unit, op='-')
                return "%s >= %s" %(name, offset)

        else:
            if time_interval == 'today':
                return "%s >= 'today'::timestamp" % name
            else:
                return "%s >= now() - '%s'::interval" % (name, time_interval)

    get_interval_where = staticmethod(get_interval_where)






# class that dynamically creates an insert statement

class Insert(object):
    '''A class to non-linearly build up an sql insert statement'''

    def __init__(self):
        self.table = None
        self.data = {}
        self.unquoted_cols = []
        self.escape_quoted_cols = []
        # optional database knowledge
        self.sql = None
        self.database = None
        self.column_types = {}
        self.impl = DatabaseImpl.get()

        self.schema = ""

    def __str__(self):
        return self.get_statement()



    def execute(self, sql=None):
        '''Actually execute the statement'''
        if not sql:
            sql = self.sql
        if not sql:
            raise SqlException("No connector found to execute query")

        conn = sql.get_connection()
        db_resource = sql.get_db_resource()
        vendor = db_resource.get_vendor()
        if vendor == "MongoDb":
            impl = db_resource.get_database_impl()
            impl.execute_insert(sql, self)




    def set_database(self, database):

        assert database == "sthpw" or not isinstance(database, basestring)

        if isinstance(database, basestring):
            self.sql = DbContainer.get(database)
            self.db_resource = DbResource.get_default(database)
        elif DbResource.is_instance(database):
        #elif isinstance(database, DbResource):
            self.sql = DbContainer.get(database)
            self.db_resource = database
            # set to database string internally
            database = database.get_database()
        elif isinstance(database, Sql):
            self.sql = database
            database = self.sql.get_database_name()
            self.db_resource = self.sql.get_db_resource()
        else:
            print("WARNING: it should be Sql instance, but it is not detected as such")
            self.sql = database
            database = self.sql.get_database_name()
            self.db_resource = DbResource.get_default(database)
            

        self.database = database
        self.impl = self.sql.get_database_impl()

        database_type = self.impl.get_database_type()
        if database_type == 'PostgreSQL':
            self.schema = "public"
        elif database_type == 'SQLServer':
            self.schema = "dbo"
        elif database_type == 'Sqlite':
            self.database = None



    def set_table(self, table):
        self.table = table

    def set_value(self, column, value, quoted=True, column_type="", escape_quoted=False):
        '''@params:
            quoted - determines whether the value needs to be quoted
        in the sql statement. 
            escape_quoted - more for PostgreSQL for now to do the E'' style quote'''
        if value == None:
            value = 'NULL'
            quoted = False

        if not column_type and self.sql:
            # get column type from database
            column_types = self.impl.get_column_types(self.db_resource, self.table)
            column_type = column_types.get(column)

          
            info = self.impl.process_value(column, value, column_type)
            if info:
                value = info.get("value")
                quoted = info.get("quoted")

        self.data[column] = value;

       
        if escape_quoted == True:
            self.escape_quoted_cols.append(column)
        elif not quoted:
            self.unquoted_cols.append(column)

    def get_data(self):
        return self.data


    def get_statement(self):
        database_type = self.impl.get_database_type()

        self.impl.preprocess_sql(self.data, self.unquoted_cols)

        # quote the values
        values = self.data.values()
        cols = self.data.keys()

        #if not cols:
        #    # add an empty row
        #    # FIXME: what is this??
        #    statement = "INSERT INTO \"%s\" (\"id\") values (default)" % self.table
        #    return statement

        statement = []


        if self.database and database_type == "Oracle":
            statement.append('INSERT INTO %s."%s"' % (self.database, self.table))
        #elif database_type == "SQLServer":
        #    statement.append('INSERT INTO [%s]' % self.table)
        else:
            #statement.append('INSERT INTO "%s"' % self.table)
            parts = []
            if self.database:
                parts.append('"%s"' % self.database)
            if self.schema:
                parts.append('"%s"' % self.schema)
            parts.append('"%s"' % self.table)
            table = ".".join(parts)

            statement.append('INSERT INTO %s' % table)


        quoted_values = []

        for i in range(0, len(cols)):
            unicode_escape = False
            value = values[i]

            if cols[i] in self.unquoted_cols:
                quoted_values.append( str(values[i]) )
            elif cols[i] in self.escape_quoted_cols:
                quoted_values.append(Sql.quote(values[i], has_outside_quotes=False, escape=True))
            else:

                if database_type == 'SQLServer':
                    unicode_escape = True
                quoted_values.append( Sql.quote(values[i], unicode_escape=unicode_escape) )
        # This is Oracle specific.  In Oracle, there is no auto increment
        # without creating triggers all over the place.
        if database_type == "Oracle" and "id" not in cols:
            cols.insert(0, "id")
            sequence_name = self.impl.get_sequence_name(self.table, self.database)
            #quoted_values.insert(0, '%s."%s".nextval' % (self.database,sequence_name))
            quoted_values.insert(0, '%s.nextval' % (sequence_name))

        statement.append( "(%s)" % ", ".join(['"%s"'%x for x in cols]) )
        statement.append( "VALUES (%s)" % ", ".join(quoted_values) )
        
      

        encoded_statements = []

                
        for x in statement:
            if isinstance(x, str):
                x = x.decode('string_escape')

                #if os.name != 'nt':
                try:
                    x = x.decode('utf-8')
                except UnicodeDecodeError, e:
                    x = x.decode('iso-8859-1')
                       
                # this only works in Linux can causes error with windows xml parser down the road
                #x = unicode(x, encoding='utf-8')
                encoded_statements.append(x)
            else:
                encoded_statements.append(x)
                 
        statement = " ".join(encoded_statements)

        statement = self.impl.postprocess_sql(statement)

        return statement


    def get_id_statement(self):
        '''get the id from the last update. This should be called after
        the insert'''
        sequence = self.impl.get_sequence_name(self.table)
        return self.impl.get_currval_select(sequence)

 

        
class Update(object):
    '''class that non-linearly builds up an update statement'''

    def __init__(self):
        self.table = None
        self.data = {}
        self.filters = {}
        self.raw_filters = []
        self.wheres = []
        self.unquoted_cols = []
        self.escape_quoted_cols = []

        # optional database knowledge
        self.sql = None
        self.database = None
        self.column_types = {}

        self.impl = DatabaseImpl.get()

        self.schema = ""

    def __str__(self):
        return self.get_statement()




    def execute(self, sql=None):
        '''Actually execute the statement'''
        if not sql:
            sql = self.sql
        if not sql:
            raise SqlException("No connector found to execute query")

        conn = sql.get_connection()
        db_resource = sql.get_db_resource()
        vendor = db_resource.get_vendor()
        if vendor == "MongoDb":
            impl = db_resource.get_database_impl()
            impl.execute_update(sql, self)



    def set_database(self, database):

        assert database == "sthpw" or not isinstance(database, basestring)

        if isinstance(database, basestring):
            self.sql = DbContainer.get(database)
            self.db_resource = DbResource.get_default(database)
        #elif isinstance(database, DbResource):
        elif DbResource.is_instance(database):
            self.sql = DbContainer.get(database)
            self.db_resource = database
            # set to database string internally
            database = database.get_database()
        elif isinstance(database, Sql):
            self.sql = database
            database = self.sql.get_database_name()
            self.db_resource = self.sql.get_db_resource()
        else:
            print("WARNING: it should be Sql instance, but it is not detected as such")
            self.sql = database
            database = self.sql.get_database_name()
            self.db_resource = DbResource.get_default(database)
            

        self.database = database
        self.impl = self.sql.get_database_impl()

        database_type = self.impl.get_database_type()
        if database_type == 'PostgreSQL':
            self.schema = "public"
        elif database_type == 'SQLServer':
            self.schema = "dbo"
        elif database_type == 'Sqlite':
            self.database = None


    def set_table(self, table):
        self.table = table

    def set_value(self, column, value, quoted = True, column_type="", escape_quoted=False):
        '''quoted determines whether the value needs to be quoted
        in the sql statement. escape_quoted is more for PostgreSQL for now to do the E'' style quote'''

        if value == None:
            value = 'NULL'
            quoted = False

        if not column_type and self.sql:
            # get column type from database
            column_types = self.impl.get_column_types(self.db_resource, self.table)
            column_type = column_types.get(column)

            info = self.impl.process_value(column, value, column_type)
            if info:
                value = info.get("value")
                quoted = info.get("quoted")
        self.data[column] = value;
        if escape_quoted == True:
            self.escape_quoted_cols.append(column)
        elif quoted == False:
            self.unquoted_cols.append(column)

    def get_data(self):
        return self.data

    def add_where(self, where):
        if where == "":
            return
        self.filters[where] = where

    def remove_filter(self, name):
        #raise Exception("Sql.add_filter() is deprecated")
        if self.filters.get(name):
            self.filters.pop(name)


    def add_filter(self, column, value, column_type="", table="", quoted=None):
        assert self.table


        # store all the raw filter data
        self.raw_filters.append( {
                'column': column,
                'value': value,
                'column_type': column_type,
                #'op': op,
                #'table': table
                'quoted': quoted,
        } )


        if not column_type and self.sql:
            # get column type from database
            column_types = self.impl.get_column_types(self.db_resource, self.table)
            column_type = column_types.get(column)

            info = self.impl.process_value(column, value, column_type)
            if info:
                value = info.get("value")
                quoted = info.get("quoted")
        else:
            quoted = True

        if quoted == None:
            value = Sql.quote(value)

        if table:
            where = "\"%s\".\"%s\" = %s" % (table, column, value)
        else:
            where = "\"%s\" = %s" % (column, value)

        self.add_where(where)


    def get_statement(self):
        impl = self.impl
        database_type = impl.get_database_type()

        impl.preprocess_sql(self.data, self.unquoted_cols)


        if isinstance(self.db_resource, basestring):
            database_name = self.db_resource
        else:
            database_name = self.db_resource.get_database()

        statement = []
        if self.database and database_type == "Oracle":
            statement.append('UPDATE "%s"."%s" SET' % (database_name, self.table))
        #elif self.database and database_type == "SQLServer":
        #    statement.append('UPDATE [%s] SET' % self.table)
        else:
            #statement.append('UPDATE "%s" SET' % self.table)
            parts = []
            if self.database:
                parts.append('"%s"' % self.database)
            if self.schema:
                parts.append('"%s"' % self.schema)
            parts.append('"%s"' % self.table)
            table = ".".join(parts)

            statement.append('UPDATE %s SET' % table)




        # quote the values
        values = self.data.values()
        cols = self.data.keys()

        quoted_values = []


        for i in range(0, len(cols)):
            unicode_escape = False
            if cols[i] in self.unquoted_cols:
                quoted_values.append(values[i])
            elif cols[i] in self.escape_quoted_cols:
                quoted_values.append(Sql.quote(values[i], has_outside_quotes=False, escape=True))
            else:
                if database_type == 'SQLServer':
                    unicode_escape = True
                quoted_values.append( Sql.quote(values[i], unicode_escape=unicode_escape) )

        pairs = []
        for i in range(0, len(cols)):
            pairs.append( '"%s" = %s' % (cols[i], quoted_values[i]) )

        # if there are not updates, return an empty string
        if len(pairs) == 0:
            return ""

        statement.append(", ".join(pairs))


        if len(self.filters):
            self.wheres = self.filters.values()
            statement.append("WHERE %s" % ", ".join( self.wheres ))


        statement = " ".join(statement)
        statement = impl.postprocess_sql(statement)
        # build the statement
        return statement


    def get_id_statement(self):
        select = Select()
        select.add_column("id")
        select.add_table(self.table)

        if self.filters:
            self.wheres = self.filters.values()
            for where in self.wheres:
                select.add_where(where)

        return select.get_statement()




class Delete(object):

    def __init__(self):
        self.impl = None
        self.database = None
        self.table = ""

        self.raw_filters = []


    def set_database(self, database):

        assert database == "sthpw" or not isinstance(database, basestring)

        if isinstance(database, basestring):
            self.sql = DbContainer.get(database)
            self.db_resource = DbResource.get_default(database)
        #elif isinstance(database, DbResource):
        elif DbResource.is_instance(database):
            self.sql = DbContainer.get(database)
            self.db_resource = database
            # set to database string internally
            database = database.get_database()
        elif isinstance(database, Sql):
            self.sql = database
            database = self.sql.get_database_name()
            self.db_resource = self.sql.get_db_resource()
        else:
            print("WARNING: it should be Sql instance, but it is not detected as such")
            self.sql = database
            database = self.sql.get_database_name()
            self.db_resource = DbResource.get_default(database)
            

        self.database = database
        self.impl = self.sql.get_database_impl()

        #sql.do_update('DELETE from "ticket" where "code" is NULL;')


    def set_table(self, table):
        self.table = table


    def add_filter(self, name, value, op='='):
        self.raw_filters.append( {
            'name': name,
            'value': value,
            'op': op
        })


    def get_statement(self):

        parts = []

        parts.append("DELETE FROM")
        parts.append('''"%s"''' % self.table)
        parts.append("WHERE")

        for filter in self.raw_filters:
            expr = '"%s" %s \'%s\'' % (filter.get("name"), filter.get("op"), filter.get("value"))
            parts.append(expr)
            parts.append("AND")

        statement = " ".join(parts)
        return statement




class CreateTable(Base):
    '''Class to nonlinearly build up a create table statement'''

    def __init__(self, search_type=None):

        from pyasm.biz import Project
        if search_type:
            from search import SearchType
            search_type_sobj = SearchType.get(search_type)

            project = Project.get_by_search_type(search_type)
            self.db_resource = project.get_project_db_resource()

            self.table = search_type_sobj.get_table()

            sql = DbContainer.get(self.db_resource)
            self.impl = sql.get_database_impl()
        else:
            self.table = None
            from pyasm.search import DatabaseImpl
            self.impl = DatabaseImpl.get()

            project = Project.get()
            self.db_resource = project.get_project_db_resource()

        self.database = self.db_resource.get_database()

        self.columns = []
        self.primary_key = None
        self.constraints = []

        self.data = {}


    def set_table(self, table):
        self.table = table

    def get_table(self):
        return self.table


    def get_database(self):
        return self.db_resource.get_database()


    def add(self, name, type, length=None, not_null=False, primary_key=False):
        if type == "text":
            expr = self.impl.get_text(not_null=not_null)
        elif type == "char":
            expr = self.impl.get_char(length=length, not_null=not_null)
        elif type == "varchar":
            expr = self.impl.get_varchar(length=length, not_null=not_null)
        elif type == "int":
            expr = self.impl.get_int(not_null=not_null)
        elif type == "timestamp":
            expr = self.impl.get_timestamp(not_null=not_null)
        elif type == "boolean":
            expr = self.impl.get_boolean(not_null=not_null)
        elif type == "serial":
            expr = self.impl.get_serial(not_null=not_null)
        elif type in ["json", "jsonb"]:
            expr = self.impl.get_json(not_null=not_null)


            
        # SQL Server
        elif type == "uniqueidentifier":
            expr = self.impl.get_text(not_null=not_null)
        elif type in ["datetime", "datetime2"]:
            expr = self.impl.get_timestamp(not_null=not_null)
        elif type.startswith("datetimeoffset"):
            expr = self.impl.get_timestamp(not_null=not_null, timezone=True)
        elif type == "nvarchar":
            expr = self.impl.get_nvarchar(length=length, not_null=not_null)

        else:
            expr = type

        col_data = {
            'type': expr,
            'length': length,
            'not_null': not_null,
            'primary_key': primary_key
        }
        self.data[name] = col_data
        if primary_key:
            self.primary_key = name


    def add_column(self, name, type, length=None, not_null=False, primary_key=False):
        return self.add(name, type, length, not_null, primary_key=primary_key)


    def set_primary_key(self, name):
        if self.primary_key:
            raise TacticException("Primary key is already set")
        self.data[name]['primary_key'] = True
        self.primary_key = name



    def add_constraint(self, columns, mode="UNIQUE"):
        constraint = {
            'columns': columns,
            'mode': mode
        }
        self.constraints.append(constraint)



    
    def get_statement(self):
        if self.impl.get_database_type() == 'SQLServer':
            statement = 'CREATE TABLE [%s] (\n' % self.table
        else:
            statement = 'CREATE TABLE "%s" (\n' % self.table

        expressions = []
        for column, col_data in self.data.items():

            type = col_data.get('type')
            length = col_data.get('length')
            not_null = col_data.get('not_null')
            primary_key = col_data.get('primary_key')

            if type == "text":
                expr = self.impl.get_text(not_null=not_null)
            elif type == "varchar":
                expr = self.impl.get_varchar(length=length, not_null=not_null)
            elif type == "nvarchar":
                expr = self.impl.get_nvarchar(length=length, not_null=not_null)
            elif type == "int":
                expr = self.impl.get_int(not_null=not_null)
            elif type == "timestamp":
                expr = self.impl.get_timestamp(not_null=not_null,default='now')
            elif type == "boolean":
                expr = self.impl.get_boolean(not_null=not_null)
            elif type == "serial":
                expr = self.impl.get_serial()
            else:
                expr = type

            if primary_key:
                expr = "%s PRIMARY KEY" % expr

                if self.impl.get_database_type() in ['Sqlite']:
                    expr = "%s AUTOINCREMENT" % expr


            expression = '    "%s" %s' % (column, expr)
            expressions.append(expression)

        #if self.primary_key != None:
        #    expressions.append('    PRIMARY KEY ("%s")' % self.primary_key)


        for constraint in self.constraints:
            columns = constraint.get("columns")
            mode = constraint.get("mode")
            suffix = 'idx'
            if mode.upper() =='UNIQUE':
                suffix = 'unique'
            # could be a dangling constraint
            if not columns:
                continue
            name = "%s_%s_%s" % (self.table, "_".join(columns), suffix )
            expr = '    CONSTRAINT "%s" %s (%s)' % (name, mode, ", ".join(columns))
            expressions.append(expr)

            # FIXME: not sure about this. Bad merge?  Besides, this is handled
            # above
            #primary_key_stmt = self.impl.get_constraint('PRIMARY KEY', columns=[self.primary_key], table=self.table)
            #expressions.append('    PRIMARY KEY ("%s")' % self.primary_key)
            #expressions.append('   %s' %primary_key_stmt)

        statement += ",\n".join(expressions)
        statement += "\n"
        statement += ");\n"

        return statement



    def commit(self, sql=None):
        '''create a standard tactic table'''
        assert sql or self.database

        if sql:
            self.database = sql.get_database_name()
            db_resource = sql.get_db_resource()

        else:
            sql = DbContainer.get(self.db_resource)
            db_resource = self.db_resource

        impl = sql.get_database_impl()
        exists = impl.table_exists(db_resource, self.table)
        if not exists:


            if sql.get_vendor() == "MongoDb":
                impl.execute_create_table(sql, self)
            else:
                statement = self.get_statement()
                sql.do_update(statement)

            sql.clear_table_cache(self.database)

        else:
            print("WARNING: table [%s] exists ... skipping" % self.table)
            defined_cols = set( sql.get_column_info(self.table).keys() )
            desired_cols = set( [x[0] for x in self.columns] )
            diff1 = defined_cols.difference(desired_cols)
            if diff1:
                print("... extra columns in database: ", diff1)
            diff2 = desired_cols.difference(defined_cols)
            if diff2:
                print("... new columns in definition: ", diff2)
            if not diff1 and not diff2:
                print("... definition the same as in the database")

        # create a sequence for the id
        try:
            if impl.__class__.__name__ == 'OracleImpl': 
                sequence = impl.get_sequence_name(self.table)
                statement = self.impl.get_create_sequence(sequence)
                sql.do_update(statement)
        except Exception as e:
            print("WARNING: ", str(e))



class DropTable(Base):

    def __init__(self, search_type=None):
        
        self.search_type = search_type
        # derive db from search_type_obj
        from search import SearchType
        from pyasm.biz import Project
        self.db_resource = Project.get_db_resource_by_search_type(self.search_type)
        
        self.database = self.db_resource.get_database()

        search_type_obj = SearchType.get(search_type)
        assert self.database
        self.table = search_type_obj.get_table()
        self.statement = self.get_statement()
        

    def get_statement(self):
        sql = DbContainer.get(self.db_resource)
        if sql.get_database_type() == 'SQLServer':
            statement = 'DROP TABLE [%s]' % self.table
        else:        
            statement = 'DROP TABLE "%s"' % self.table

        return statement

    def commit(self):
   
        
        sql = DbContainer.get(self.db_resource)
        if not sql.table_exists(self.table):
            print("WARNING: table [%s] does not exist in database [%s]" % (self.table, self.database))
            return

        # dump table into sql first
        tmp_dir = Environment.get_tmp_dir()
        schema_path = "%s/cache/drop_%s_%s.sql" % \
            (tmp_dir, self.database, self.table)

        if os.path.exists(schema_path):
            os.unlink(schema_path)


        # dump the table to a file and store it in cache
        from sql_dumper import TableSchemaDumper
        dumper = TableSchemaDumper(self.search_type)
        try:
            # should i use mode='sobject'? it defaults to 'sql'
            dumper.dump_to_tactic(path=schema_path)
        except SqlException as e:
            print("SqlException: ", e)
            raise

        impl = sql.get_database_impl()
        if impl.commit_on_schema_change():
            DbContainer.commit_thread_sql()
            
        sql.do_update(self.statement)
        sql.clear_table_cache()



class AlterTable(CreateTable):
    '''Class to nonlinearly build up an alter table statement'''

    def __init__(self, search_type=None):
        super(AlterTable, self).__init__(search_type)
        """
        self.search_type = search_type
        # derive db from search_type_obj
        from search import SearchType
        search_type_obj = SearchType.get(search_type)
        self.database = search_type_obj.get_database()
        """
        assert self.database
        self.drop_columns = []

    def drop(self, name):
        #TODO: check if this column exists
        #print("COL NAME ", name)
        self.drop_columns.append(name)

    def verify_table(self):
        from search import SearchType
        if not self.table and self.search_type:
            search_type_obj = SearchType.get(self.search_type)
            self.table = search_type_obj.get_table()

    def modify(self, name, type, length=256, not_null=False):
        # must store not_null separately,
        is_not_null = not_null
        if type == "text":
            expr = self.impl.get_text(not_null=False)
        elif type == "varchar":
            expr = self.impl.get_varchar(length=length, not_null=False)
        elif type == "int":
            expr = self.impl.get_int(not_null=False)
        elif type == "float":
            expr = self.impl.get_float(not_null=False)
        elif type == "timestamp":
            if self.impl.get_database_type() == 'SQLServer':
                expr = self.impl.get_timestamp(not_null=False, default=None)
            else:
                expr = self.impl.get_timestamp(not_null=False)
        elif type == "boolean":
            expr = self.impl.get_boolean(not_null=False)
        else:
            expr = type

        self.columns.append( (name, expr, is_not_null) )

    def get_statements(self):
        self.verify_table()

        statements = []
        for value in self.columns:
            statement = self.impl.get_modify_column(self.table, value[0], value[1], value[2])
            statements.extend(statement)

        for value in self.drop_columns:

            # TODO: The following should be decided in DatabaseImpl()
            from pyasm.search.sql import Sql
            if self.impl.get_database_type() == 'SQLServer':
                statement = 'ALTER TABLE [%s] DROP COLUMN [%s]' \
                    % (self.table, value)
            else:
                statement = 'ALTER TABLE "%s" DROP "%s"' \
                    % (self.table, value)

            statements.append(statement)
        return statements


    # TEST
    def xxx_drop_column(self, column):

        sql = DbContainer.get("sthpw")
        columns = sql.get_columns(self.table)
        columns.remove(column)
        columns_str = ", ".join(columns)

        statement = '''
        CREATE TABLE __%(table)s_new (
          foo  TEXT PRIMARY KEY,
          bar  TEXT,
          baz  INTEGER
        );

        INSERT INTO __%(table)s_new SELECT %(columns)s FROM %(table)s;
        DROP TABLE %(table)s;
        ALTER TABLE __%(table)s_new RENAME TO %(table)s;
        ''' % {'table': self.table, 'columns': columns_str}

        return statement



    def commit(self):
        '''Commit one or more alter table statements'''
        sql = DbContainer.get(self.db_resource)
        impl = sql.get_database_impl()
        #database = sql.get_database_name()
        exists = impl.table_exists(self.db_resource, self.table)

        # check to see if autocommit should be on
        if impl.commit_on_schema_change():
            DbContainer.commit_thread_sql()
        
        if exists:
            statements = self.get_statements()
            for statement in statements:
                sql.do_update(statement)
        else:
            print("WARNING: table [%s] does not exist ... skipping" % self.table)



class CreateView(Base):


    def __init__(self, search_type=None, query=None, search=None):

        if query:
            self.query = query
        else:
            self.query = search.get_statement()

        assert self.query

        from pyasm.biz import Project
        if search_type:
            from search import SearchType
            search_type_sobj = SearchType.get(search_type)

            self.view = search_type_sobj.get_table()

            from search import SearchType
            search_type_sobj = SearchType.get(search_type)

            project = Project.get_by_search_type(search_type)
            self.db_resource = project.get_project_db_resource()

            self.table = search_type_sobj.get_table()

            sql = DbContainer.get(self.db_resource)
            self.impl = sql.get_database_impl()
        else:
            self.view = None

            from pyasm.search import DatabaseImpl
            self.impl = DatabaseImpl.get()

            project = Project.get()
            self.db_resource = project.get_project_db_resource()

        self.database = self.db_resource.get_database()



    def set_view(self, view):
        self.view = view




    def get_statement(self):

        statement = []

        #if self.impl.get_database_type() == 'SQLServer':

        statement.append( 'CREATE VIEW "%s"' % self.view )

        statement.append( 'AS' )
        
        statement.append( self.query )

        statement = " ".join(statement)

        return statement

 
    def commit(self, sql=None):
        '''Commit one or more alter table statements'''

        if sql:
            self.database = sql.get_database_name()
            db_resource = sql.get_db_resource()

        else:
            sql = DbContainer.get(self.db_resource)
            db_resource = self.db_resource

        impl = sql.get_database_impl()

        
        statement = self.get_statement()
        sql.do_update(statement)

        sql.clear_table_cache(self.database)








