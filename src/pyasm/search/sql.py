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

__all__ = ["SqlException", "DatabaseException", "Sql", "DbContainer", "DbResource", "DbPasswordUtil", "Select", "Insert", "Update", "Delete", "CreateTable", "DropTable", "AlterTable"]


import os, types, thread, sys
import re, datetime

from threading import Lock

from pyasm.common import Config, TacticException, Environment


# import database libraries
DATABASE_DICT = {}

try:
    import pyodbc
    DATABASE_DICT["SQLServer"] = pyodbc
    #Config.set_value("database", "vendor", "SQLServer")
except ImportError, e:
    pass

try:
    import psycopg2
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
        raise TacticException("ERROR: database library for [%s] is not installed" % DATABASE)


set_default_vendor()


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

    def __init__(my, database_name, host=None, user=None, password=None, vendor=None, port=None):
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
        my.database_name = database_name
        #my.database_name = "schema_test"

        # get the database from the config file
        if host:
            my.host = host
        else:
            my.host = Config.get_value("database", "server")

        if user:
            my.user = user
        else:
            my.user = Config.get_value("database", "user")
        if port: my.port = port
        else: my.port = Config.get_value("database", "port")
       
        if password:
            my.password = password
        # get from encrypted file
        else:
            my.password = DbPasswordUtil.get_password()

        if not my.host:
            my.host = "localhost"

        my.vendor = vendor
        if not my.vendor:
            my.vendor = Config.get_value("database", "vendor")

        my.database_impl = DatabaseImpl.get(my.vendor)
        my.pgdb = DATABASE_DICT.get(my.vendor)
        if not my.pgdb:
            raise TacticException("ERROR: database library for [%s] is not installed" % my.vendor)


        my.cursor = None
        my.results = ()
        my.conn = None
        my.last_query = None
        my.row_count = -1

        my.transaction_count = 0
        my.description = None


    def get_db_resource(my):
        db_resource = DbResource(my.database_name, host=my.host, port=my.port, vendor=my.vendor, user=my.user, password=my.password)
        return db_resource


    def set_default_vendor(vendor):
        set_default_vendor(vendor)
    set_default_vendor = staticmethod(set_default_vendor)



    #def __del__(my):
    #    print "CONNECT: delete: ", my


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
    def get_database_version(my):
        return my.get_database_impl().get_version()

    def get_database_type(my):
        return my.vendor

    def get_database_impl(my):
        return my.database_impl


    def get_timestamp_now(my):
        return my.database_impl.get_timestamp_now()




    def get_table_description(my):
        return my.description


    def get_database_name(my):
        return my.database_name

    def get_host(my):
        return my.host

    def get_user(my):
        return my.user

    def get_password(my):
        return my.password

    def get_vendor(my):
        return my.vendor



    def get_connection(my):
        '''get the underlying database connection'''
        return my.conn



    def get_columns_from_description(my):
        columns = []
        for description in my.description:
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




    def get_columns(my,table=None,use_cache=True):
        '''Returns a list of string ordered columns contained in this table
        '''
        db_resource = my.get_db_resource()
        database = my.get_database_name()

        key = '%s:%s' %(db_resource, table)
        if use_cache:
            columns = Container.get_dict("Sql:table_columns", key)
            if columns:
                return columns[:]
                #return columns

            # use global cache
            if database == 'sthpw':
                from pyasm.biz import CacheContainer
                cache = CacheContainer.get("sthpw_column_info")
                if cache:
                    columns = cache.get_value_by_key("columns", table)
                    if columns != None:
                        return columns[:]
                        #return columns

        impl = my.get_database_impl()
        columns = impl.get_columns(db_resource, table)

        if use_cache:
            Container.put_dict("Sql:table_columns", key, columns)
 
        return columns[:]


    def get_table_info(my):
        impl = my.get_database_impl()
        info = impl.get_table_info(my.get_db_resource()) 
        return info


 
    def get_column_info(my, table, column=None, use_cache=True):
        impl = my.get_database_impl()
        info = impl.get_column_info(my.get_db_resource(), table)
        if not column:
            return info
        else:
            return info.get(column)

  
    def get_column_types(my, table):
        impl = my.get_database_impl()
        return impl.get_column_types(my.get_db_resource(), table) 

    def get_column_nullables(my, table):
        impl = my.get_database_impl()
        return impl.get_column_nullables(my.get_db_resource(), table) 


    def is_in_transaction(my):
        '''Returns a boolean showing whether the database is in transaction
        or not'''
        if my.transaction_count <= 0:
            return False
        else:
            return True

    def get_row_count(my):
        '''returns the number of rows effected in the last update'''
        return my.row_count


    def start(my):
        '''start a transaction'''
        my.transaction_count += 1

    def set_savepoint(my, name='save_pt'):
        '''set a savepoint'''
        stmt = my.database_impl.set_savepoint(name)
        if stmt:
            cursor = my.conn.cursor()
            cursor.execute(stmt)

    def rollback_savepoint(my, name='save_pt', release=True):
        '''rollback to a savepoint'''
        my.cursor = my.conn.cursor()
        stmt = my.database_impl.rollback_savepoint(name)
        if not stmt:
            return
        my.cursor.execute(stmt)
        if release:
            my.release_savepoint(name)

    def release_savepoint(my, name='save_pt'):
        release_stmt = my.database_impl.release_savepoint(name)
        if not release_stmt:
            return
        if release_stmt:
            my.cursor.execute(release_stmt)
        

    
    def commit(my):
        '''commit the transaction'''
        my.transaction_count -= 1

        # only commit if transaction count = 0 to support embedded
        # transactions
        #if my.transaction_count == 0:
        if my.transaction_count <= 0:
            try:
                my.transaction_count = 0

                # NOTE: protect against database being already closed.
                # Note sure why it is being closed, but there are some
                # extreme circumstances where this will occur
                if not my.conn:
                    # reconnect
                    my.connect()
                else:
                    my.conn.commit()
                    
                sql_dict = DbContainer._get_sql_dict()
                database_name = my.get_database_name()
                sql_dict[database_name] = my

            except my.pgdb.OperationalError, e:
                raise SqlException(e.__str__())
            


    def rollback(my, force=False):
        '''rollback the transaction'''
        if force or my.transaction_count > 0:
            if my.conn:
                my.conn.rollback()
                my.transaction_count = 0

    def connect(my):
        '''connect to the database'''
        if not my.host:
            raise DatabaseException("Server setting is empty")

        # pgdb connection code
        auth = None
        try:
            if my.vendor == "PostgreSQL":
                # psycopg connection code
                if my.password == "" or my.password == "none":
                    password_str = ""
                else:
                    password_str = "password=%s" % my.password
                if not my.port:
                    my.port = 5432
                sslmode = "require"
                sslmode = "disable"
                auth = "host=%s port=%s dbname=%s sslmode=%s user=%s %s" % \
                    (my.host, my.port, my.database_name, sslmode, my.user, password_str)
                my.conn = my.pgdb.connect(auth)

            elif my.vendor == "Sqlite":

                db_dir = Config.get_value("database", "sqlite_db_dir")
                if not db_dir:
                    #install_dir = Environment.get_install_dir()
                    #db_dir = "%s/src/install/start/db" % install_dir
                    data_dir = Environment.get_data_dir()
                    db_dir = "%s/db" % data_dir

                # DEBUG: this -1 database seems to popup
                if my.database_name in [-1, '-1']:
                    raise DatabaseException("Database '-1' is not valid")
                auth = "%s/%s.db" % (db_dir, my.database_name)
                my.conn = sqlite.connect(auth, isolation_level="DEFERRED" )

                # immediately cache all of the columns in the database.  This
                # is because get_column_info in Sqlite requires a PRAGMA
                # statement which forces a transaction to commit
                from database_impl import SqliteImpl
                SqliteImpl.cache_database_info(my)


            elif my.vendor == "MySQL":
                encoding = Config.get_value("database", "encoding")
                charset = Config.get_value("database", "charset")
                if not encoding:
                    #encoding = 'utf8mb4'
                    encoding = 'utf8'
                if not charset:
                    charset = 'utf8'
                my.conn = MySQLdb.connect(  db=my.database_name,
                                            host=my.host,
                                            user=my.user,
                                            charset=charset,
                                            use_unicode=True,
                                            passwd=my.password )
                my.do_query("SET sql_mode='ANSI_QUOTES';SET NAMES %s"%encoding);

            elif my.vendor == "Oracle":
                # if we connect as a single user (like most databases, then
                # use the user name), otherwise if we connect by schema,
                # we use the database name.  This is determined by whether
                # or not the user field is empty
                if not my.user:
                    auth = '%s/%s@%s' % (my.database_name, my.password, my.host)
                else:
                    auth = '%s/%s@%s' % (my.user, my.password, my.host)
                my.conn = my.pgdb.connect(str(auth))

            elif my.vendor == "SQLServer":
                sqlserver_driver = '{SQL Server}'
                # pyodbc connection code
                if my.password == "" or my.password == "none":
                    password_str = ""
                else:
                    password_str = my.password
                # >>> cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=localhost,1433;DATABASE=my_db;UID=tactic;PWD=south123paw')
# 
                auth = "DRIVER=%s; SERVER=%s,%s; DATABASE=%s; UID=%s; PWD=%s" % \
                    (sqlserver_driver, my.host, my.port, my.database_name, my.user, password_str)
                my.conn = pyodbc.connect(auth)

            elif my.vendor == "MongoDb":

                from mongodb import MongoDbConn
                my.conn = MongoDbConn(my.database_name)


            elif my.vendor == "TACTIC":
                from pyasm.search import TacticImpl
                my.conn = TacticImpl()
                #raise DatabaseException("Database TACTIC not yet implemented")
                
            else:
                raise DatabaseException("Unsupported Database [%s]" % my.vendor)

        except Exception, e:
            #print "ERROR: connecting to database [%s, %s]" % (my.host, my.database_name), e.__str__()
            raise
            raise DatabaseException(e)

        assert my.conn

        return my



    # Resets sequence so that the next available ID number is exactly one greater than the highest existing ID
    # number of the given table
    #
    def reset_sequence_for_table(my, table, database=None):

        # FIXME: currently only available for the Oracle database 

        impl = my.get_database_impl()
        stmt = impl.get_reset_table_sequence_statement(table, database)
        from sql import DbContainer
        sql = DbContainer.get(my.get_database_name())
        results = sql.do_update(stmt)



    def modify_column(my, table, column, type, not_null=None):
        impl = my.get_database_impl()
        statements = impl.get_modify_column(table, column, type, not_null)
        from sql import DbContainer
        sql = DbContainer.get(my.get_database_name())
        for statement in statements:
            sql.do_update(statement)


    def clear_results(my):
        # MySQL uses tuples
        impl = my.get_database_impl()
        if impl.get_database_type() not in ['MySQL']:
            for i in range(0, len(my.results)):
                my.results[i] = None

        my.results = []


    # FIXME: is there any reason to have this function.  This should be 
    # incorporated into do_query.
    """
    def execute(my, query, num_attempts=0):
        '''execute a query'''

        #raise SqlException("FIXME: Incorporate into do_query")

        try:
            # in case of accidental loss of connection
            if not my.conn:
                # reconnect
                my.connect()

            my.query = query
            my.cursor = my.conn.cursor()
            my.cursor.execute(query)

            my.description = my.cursor.description
            return

        except pgdb.OperationalError, e:
            # A reconnect will only be attempted on the first query.
            # This is because subsequent could be in a transaction and
            # closing and reconnecting will completely mess up the transaction
            #
            first_query = Container.get("Sql::%s::first_query" % my.database_name)
            if first_query == False:
                raise SqlException("%s: %s\n%s" % (my.DO_QUERY_ERR, query,e.__str__()) )

            if num_attempts >= 3:
                print "ERROR: three failed attempts have been made to access [%s]" % my.database_name
                raise SqlException("%s: %s\n%s" % (my.DO_QUERY_ERR, query,e.__str__()) )

            Container.put("Sql::first_query", False)

            # try to reconnect
            print "WARNING: a database error [%s] has been encountered: " % e.__class__.__name__
            print str(e)
            print "Attempting to reconnect and reissue query"
            # try closing: oracle throws an exception if you try to close
            # on an already closed connection
            try:
                my.close()
            except:
                pass
            my.connect()
            return my.do_query(query, num_attempts=num_attempts+1)

        except pgdb.Error, e:
            error_msg = str(e)
            print "ERROR: %s: "%my.DO_QUERY_ERR, error_msg, str(query)
            # don't include the error_msg in Exception to avoid decoding error 
            raise SqlException("%s: %s\n" % (my.DO_QUERY_ERR, query))
    """





    def do_query(my, query, num_attempts=0):
        '''execute a query'''

        my.clear_results()

        try:
            # in case of accidental loss of connection
            if not my.conn:
                # reconnect
                my.connect()


            vendor = my.get_vendor()
            #if vendor == "MongoDb":
            if isinstance(query, Select):
                my.results = query.execute(my)
            else:

                #import time
                #start = time.time()
                #print my.database_name, query
                my.query = query
                my.cursor = my.conn.cursor()
                #import time
                #start = time.time()
                my.cursor.execute(query)

                my.description = my.cursor.description

                # copy the data structure because LOBs in Oracle become stale
                if my.get_database_type() == "Oracle":
                    import cx_Oracle
                    my.results = []
                    for x in my.cursor:
                        result = []
                        for y in x:
                            if isinstance(y, cx_Oracle.LOB):
                                result.append(str(y))
                            else:
                                result.append(y)
                        my.results.append(result)
                else:
                    my.results = my.cursor.fetchall()

                my.cursor.close()
                #print time.time() - start


            return my.results


        except my.pgdb.OperationalError, e:
            # A reconnect will only be attempted on the first query.
            # This is because subsequent could be in a transaction and
            # closing and reconnecting will completely mess up the transaction
            #
            key = "Sql::%s::%s::first_query" % (my.vendor, my.database_name)
            first_query = Container.get(key)
            if first_query == False:
                raise SqlException("%s: %s\n%s" % (my.DO_QUERY_ERR, query,e.__str__()) )

            if num_attempts >= 3:
                print "ERROR: three failed attempts have been made to access [%s]" % my.database_name
                raise SqlException("%s: %s\n%s" % (my.DO_QUERY_ERR, query,e.__str__()) )

            Container.put("Sql::first_query", False)

            # try to reconnect
            print "WARNING: a database error [%s] has been encountered: " % e.__class__.__name__
            print str(e)
            print "Attempting to reconnect and reissue query"
            # try closing: oracle throws an exception if you try to close
            # on an already closed connection
            try:
                my.close()
            except:
                pass
            my.connect()
            return my.do_query(query, num_attempts=num_attempts+1)

        except my.pgdb.Error, e:
            error_msg = str(e)
            print "ERROR: %s: "%my.DO_QUERY_ERR, error_msg, str(query)
            # don't include the error_msg in Exception to avoid decoding error 
            raise SqlException("%s: %s\n" % (my.DO_QUERY_ERR, query))


    def get_value(my, query):
        '''convenience function when you know there will be only one result'''
        result = my.do_query(query)
        if len(result) > 0:
            value = result[0][0]
            if value == None:
                value = ""
        else:
            value = ""
        return value

    def get_int(my, query):
        return int(my.get_value(query))



    def do_update(my, query, quiet=False):
        """execute an update. If quiet = True, it doesn't print error causing sql"""
        if query =="":
            return

        try:
            if not my.conn:
                my.connect()

            # store the last query
            #print "[%s]" % my.database_name, query

            my.query = query
            my.cursor = my.conn.cursor()

            #my.execute(query)
            #print "update: ", query
            my.cursor.execute(query)

            # remember the row count
            my.row_count = my.cursor.rowcount

            if my.vendor == 'Sqlite':
                my.last_row_id = my.cursor.lastrowid
            elif my.vendor == 'MySQL':
                my.last_row_id = my.conn.insert_id()
            else:
                my.last_row_id = 0

            my.cursor.close()


            # commit the transaction if there is no transaction
            if my.transaction_count == 0:
                my.transaction_count = 1
                my.commit()

        except my.pgdb.ProgrammingError, e:
            if str(e).find("already exists") != -1:
                return
            if isinstance(query, unicode):
                wrong_query = query.encode('utf-8')
            else:
                wrong_query = unicode(query, errors='ignore').encode('utf-8')

            print "Error with query (ProgrammingError): ", my.database_name, wrong_query
            print str(e)
            raise SqlException(str(e))
        except my.pgdb.Error, e:
            if not quiet:
                if isinstance(query, unicode):
                    wrong_query = query.encode('utf-8')
                else:
                    wrong_query = unicode(query, errors='ignore').encode('utf-8')
                print "Error with query (Error): ", my.database_name, wrong_query
            raise SqlException(e.__str__())



    def update_single(my, statement_obj):
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
            id = my.get_value(id_statement)


        # do the update
        statement = statement_obj.get_statement()
        my.do_update(statement)


        # check that one row and only one raw was affected
        if my.row_count == 0:
            raise SqlException("Statement [%s] did not affect any rows")

        if my.row_count > 1:
            raise SqlException("Statement [%s] affected any [%s] rows" % (statement, my.row_count) )

        # get the insert id
        if is_insert:
            id_statement = statement_obj.get_id_statement()
            id = my.get_value(id_statement)

        if id > 0:
            return id
            
        raise SqlException("Improper id return with statement [%s]" % statement)




    def close(my):
        if my.conn == None:
            return

        my.conn.close()
        my.conn = None



    def dump(my):
        print(my.results)


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
                print "WARNING: set_value(): ", value
                print "type: ", type(value)
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
    def copy_table_schema(my, from_table, to_table):
        '''dump the table to a file.  This is pretty messy, but I couldn't
        find a better way to do this'''
        tmp_dir = Environment.get_tmp_dir()
        file_path = "%s/temp/%s__%s.sql" % (tmp_dir,my.database_name,from_table)
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
            (my.host, my.user, my.port, from_schema, from_table, \
            my.database_name, file_path)

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
              (my.host, my.user, my.port, my.database_name, file_path+".tmp") )

        os.unlink(file_path)
        os.unlink(file_path+".tmp")



    # some database introspection tools: note that a different module
    # is used here because it appears that pgdb (which is DB-API 2.0 compliant)
    # does not support database introspection (not sure why not)
    def get_tables(my):
        db_resource = my.get_db_resource()
        #key = "Sql:%s:tables"% db_resource
        #tables = Container.get(key)
        #if tables != None:
        #    return tables

        table_info = my.database_impl.get_table_info(db_resource)

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


    def table_exists(my, table):
        db_resource = my.get_db_resource()
        return my.database_impl.table_exists(db_resource, table)




class DbResource(Base):
    '''Define a database resource.  It contains the necessary
    information required to connect to a particular database'''

    DBRESOURCE_ID = 'DbResource'


    def __init__(my, database, host=None, port=None, vendor=None, user=None, password=None, **options):
        # MySQL does allow empty.  This is needed to create a database
        if vendor != "MySQL":
            assert database
        my.database = database
        my.host = host
        my.port = port
        my.vendor = vendor
        if not my.vendor:
            my.vendor = Sql.get_default_database_type()

        assert my.vendor in VENDORS

        my.user = user
        my.password = password

        # database specific extra options
        my.options = options

        if not my.host:
            my.host = Config.get_value("database", "server")
        if not my.host:
            my.host = 'localhost'


        # Fill in the defaults
        if my.vendor == 'MySQL':
            if not my.user:
                my.user = "root" 
        elif my.vendor == 'PostgreSQL':
            if not my.user:
                my.user = "postgres" 
            if not my.port:
                my.port = '5432'
        


    def __str__(my):
        return "DbResource:%s:%s:%s:%s" % (my.vendor, my.host, my.port, my.database)

    def get_database(my):
        return my.database

    def get_host(my):
        return my.host

    def get_port(my):
        return my.port

    def get_vendor(my):
        return my.vendor

    def get_user(my):
        return my.user

    def get_password(my):
        return my.password

    def get_key(my):
        if my.host:
            return "%s:%s:%s:%s" % (my.vendor, my.host, my.port, my.database)
        else:
            return my.database

    def get_database_type(my):
        return my.vendor


    def get_database_impl(my):
        impl = DatabaseImpl.get(my.vendor)
        return impl

    
    def exists(my):
        return my.get_database_impl().database_exists(my)


    def get_sql(my):
        return DbContainer.get(my)


    def get_search(my, table):
        from pyasm.search import Search
        search = Search.get_search_by_db_resource(my, table)
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


        # evaluate ticket
        ticket = Environment.get_ticket()

        from pyasm.security import Site
        site_obj = Site.get()
        site = None
        if ticket:
            site = site_obj.get_by_ticket(ticket)
        if not site:
            site = site_obj.get_site()

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
            #print "DBCONTAINER what is", db_resource, type(db_resource)
            assert DbResource.is_instance(db_resource)
        else:
            db_resource = DbResource.get_default("sthpw")

        sql = cls.get_connection_pool_sql(db_resource)

        if sql and sql.get_connection():
            DbContainer.register_connection(sql) 

        assert sql.get_connection()
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
        pool_max_connections = 1
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
                #print "CONNECT: reuse: ", database_key, sql, xx.get_ident()


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
                
            except Exception, e:
                print "WARNING: When trying to commit: ", e
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
        #print "releasing: ", thread.get_ident()


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
                except SqlException, e:
                    print "WARNING: ", e.__str__()
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
            print "WARNING: SQLServer implementation does not support encoded keys for database passwords"
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

    def __init__(my):
        my.tables = []
        my.id_col = 'id'
        my.columns = []
        my.as_columns = []
        my.column_tables = []
        my.wheres = []
        my.filters = {}
        my.raw_filters = []
        my.filter_mode = "AND"
        my.group_bys = []
        my.havings = []
        my.order_bys = []
        my.order_by_columns = []
        my.limit = None
        my.offset = 0
        my.distinct = False
        my.distinct_col = None
        my.joins = []
        my.join_tables = set()

        # optional database knowledge
        my.sql = None
        my.database = None
        my.db_resource = None
        my.column_types = {}
        my.impl = DatabaseImpl.get()

        my.statement = None
        
        my.set_statement = None

        my.schema = ""


    def execute(my, sql=None):
        '''Actually execute the statement'''
        if not sql:
            sql = my.sql
        if not sql:
            raise SqlException("No connector found to execute query")

        conn = sql.get_connection()
        db_resource = sql.get_db_resource()
        vendor = db_resource.get_vendor()

        if vendor == "MongoDb":
            impl = db_resource.get_database_impl()
            results = impl.execute_query(sql, my)
            """
            table = my.tables[0]
            collection = conn.get_collection(table)
            my.cursor = collection.find(my.raw_filters)
            if my.order_bys:
                sort_list = []
                for order_by in my.order_bys:
                    parts = order_by.split(" ")
                    order_by = parts[0]
                    if len(parts) == 2:
                        direction = parts[1]
                    else:
                        direction = "asc"

                    if direction == "desc":
                        sort_list.append( [order_by, -1] )
                    else:
                        sort_list.append( [order_by, 1] )

                    my.cursor.sort(sort_list)

            results = []
            for result in my.cursor:
                results.append(result)
            """

        else:

            statement = my.get_statement()
    
            # remember the cursor (needed for savepoints)
            my.cursor = conn.cursor()
            my.cursor.execute(statement)

            results = my.cursor.fetchall()
            my.cursor.close()

        return results


    def execute_count(my, sql=None):
        if not sql:
            sql = my.sql
        if not sql:
            raise SqlException("No connector found to execute query")

        conn = sql.get_connection()
        db_resource = sql.get_db_resource()
        vendor = db_resource.get_vendor()

        if vendor == "MongoDb":
            # TODO: slow
            results = my.execute()
            results = len(results)

        else:
            statement = my.get_count()
            results = sql.do_query(statement)
            if results:
                results = int(results[0][0])
            else:
                results = 0

        return results





    def __str__(my):
        return my.get_statement()


    def set_database(my, database):

        assert database == "sthpw" or not isinstance(database, basestring)

        if isinstance(database, basestring):
            my.sql = DbContainer.get(database)
            my.db_resource = DbResource.get_default(database)
        #elif isinstance(database, DbResource):
        elif DbResource.is_instance(database):
            my.sql = DbContainer.get(database)
            my.db_resource = database
            # set to database string internally
            database = database.get_database()
        elif isinstance(database, Sql):
            my.sql = database
            database = my.sql.get_database_name()
            my.db_resource = my.sql.get_db_resource()
        else:
            # NOTE: sometimes an object that is sql.Sql is not detected
            # by the above condition.  Note sure why, but this warning
            # becomes intrusive
            #print "WARNING: it should be Sql instance, but it is not detected as such"
            my.sql = database
            database = my.sql.get_database_name()
            my.db_resource = DbResource.get_default(database)
            

        my.database = database
        my.impl = my.sql.get_database_impl()

        database_type = my.impl.get_database_type()
        if database_type == 'PostgreSQL':
            my.schema = "public"
        elif database_type == 'SQLServer':
            my.schema = "dbo"
        elif database_type == 'Sqlite':
            my.database = None

    def set_statement(my, statement):
        '''special function which allows you to put in an arbitrary sql
        statement and dynamically add operations to it.  There are limitations
        to this'''
        my.tables.append("( %s )" % statement)
        my.set_statement = statement


    
    def add_table(my, table):
        if table == "": return
        my.tables.append(table)

    def get_tables(my):
        return my.tables
        
    def get_table(my):
        return my.tables[0]
    
    def set_id_col(my, id_col):
        my.id_col = id_col

    def add_join(my, table1, table2=None, column=None, column2=None, join="LEFT OUTER", database=None, database2=None):
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
            table1 = my.tables[0]

        # ensure that the join only occurs once
        if table1 in my.join_tables:
            return
        my.join_tables.add(table1)


        if column and column2:
            column1 = column
        elif not column:
            column1 = "%s_id" % table2
            columns =  my.impl.get_column_info(my.db_resource, table1).keys()
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
            database1 = my.database
        else:
            database1 = database
        parts = []
        if database1:
            parts.append('"%s"' % database1)
        if my.schema:
            parts.append('"%s"' % my.schema)
        prefix1 = ".".join(parts)

        if prefix1:
            prefix1 = "%s." % prefix1
 

        # handle the database scoping
        if not database2:
            database2 = my.database
        parts = []
        if database2:
            parts.append('"%s"' % database2)
        if my.schema:
            parts.append('"%s"' % my.schema)
        prefix2 = ".".join(parts)
 
        # add a trailing point.  this is needed so that implementations with
        # not prefix can be accomodated (ie: Sqlite)
        if prefix2:
            prefix2 = "%s." % prefix2
 

        expr = '''%s JOIN %s"%s" ON "%s"."%s" = "%s"."%s"''' % (join, prefix2, table2, table1, column1, table2, column2)

        if my.impl.get_database_type() == 'SQLServer':
            expr = '''%s JOIN %s"%s" ON "%s"."%s" = %s"%s"."%s"''' % (join, prefix2, table2, table1, column1, prefix2, table2, column2)
        # NOTE: there should be no need to database specfic joins
        """
        if my.impl.get_database_type() == 'Oracle':
            # do fully qualified table names (i.e. include schema prefix) for Oracle SQL ... needed
            # for use with set-ups that use a service user to access the Oracle DB
            schema = my.database
            expr = '''%s JOIN %s."%s" ON %s."%s"."%s" = %s."%s"."%s"''' % \
                    (join, schema, table2, schema, table1, column1, schema, table2, column2)
        elif my.impl.get_database_type() == 'SQLServer':
            expr = '''%s JOIN [%s] ON [%s].[%s] = [%s].[%s]''' % \
                (join, table2, \
                table1, column1, \
                table2, column2)
        else:
            expr = '''%s JOIN "%s" ON "%s"."%s" = "%s"."%s"''' % (join, table2, table1, column1, table2, column2)
        """

        my.joins.append(expr)



    def add_column(my, column, distinct=False, table=None, as_column=None):
        if (column == "" or column in my.columns) and column != '*':
            return
        # This doesn't make sense, comment out for now
        # SQL Server specific: We automatically add the ID column as the sequence.
        # Prevent adding the ID column again.
        #if column == 'id':
        #    return
        my.columns.append(column)
        my.as_columns.append(as_column)

        if table:
            my.column_tables.append(table)
        else:
            my.column_tables.append(my.tables[0])

        if distinct:
            my.distinct_col = column

        my.distinct = distinct


    def set_distinct_col(my, column):
        my.distinct = True
        my.distinct_col = column



    def get_columns(my):
        columns = []
        for column, as_column in zip(my.columns, my.as_columns):
            if as_column:
                columns.append(as_column)
            else:
                columns.append(column)

        return columns


    def set_filter_mode(my, mode):
        assert mode in ['and', 'or']
        my.filter_mode = mode.upper()



    def add_where(my, where):
        my.wheres.append(where)



    def add_op(my, op, idx=None):
        assert op in ['and', 'or', 'begin']
        if idx == None:
            # TODO: determine if this is needed later
            #if my.wheres and op != "begin" and my.wheres[-1] == "begin":
            #    my.wheres.pop()
            #else:
            #    my.wheres.append(op)
            my.wheres.append(op)
        else:
            my.wheres.insert(idx, op)


    def get_wheres(my):
        return my.wheres

    def remove_where(my, where):
        try:
            my.wheres.remove(where)
        except:
            pass


    def _convert_to_database_boolean(my, value):
        if not my.impl.get_database_type() == 'SQLServer':
            return value

        if value == 'true' or value == 'TRUE':
            return '1'
        else:
            if value == 'false' or value == 'FALSE':
                return '0'
        return value

    def add_filter(my, column, value, column_type="", op='=', quoted=None, table=''):
        assert my.tables

        # store all the raw filter data
        my.raw_filters.append( {
                'column': column,
                'value': value,
                'column_type': column_type,
                'op': op,
                'quoted': quoted,
                'table': table
        } )


        if not table:
            table = my.tables[0]

        if column == 'id' and value == None:
            where = "\"%s\".\"%s\" is NULL" % (table, column)
            my.add_where(where)
            return

        if value == None:
            where = "\"%s\".\"%s\" is NULL" % (table, column)
            my.add_where(where)
            return

        if quoted == "column":
            value = '"%s"' % value
            quoted = False



        # This check added to handle cases where a list is empty,
        # as 'value[0]' is not defined in that case. We assume in this
        # case that the intended value is NULL
        if type(value) == types.ListType and len(value) == 0:
            where = "\"%s\" is NULL" % column
            my.add_where(where)
            return


        # on simple building of select statements, db_resource could be null
        if not my.db_resource:
            column_type = "varchar"
        elif not column_type:
            column_types = my.impl.get_column_types(my.db_resource, my.tables[0])
            column_type = column_types.get(column)


        # if quoted is not explicitly set
        if quoted == None:
            quoted = True

            if not column_type and my.sql:
                # get column type from database
                column_types = my.impl.get_column_types(my.db_resource, my.tables[0])
                column_type = column_types.get(column)

                info = my.impl.process_value(column, value, column_type)

                if info:
                    value = info.get("value")
                    value = my._convert_to_database_boolean(value)
                    quoted = info.get("quoted")
            else:
                quoted = True


        if quoted:
            value = Sql.quote(value)

        if table:
            where = "\"%s\".\"%s\" %s %s" % (table, column, op, value)
        else:
            where = "\"%s\" %s %s" % (column, op, value)
        my.add_where(where)



    def add_filters(my, column, values, table='', op='in'):

        quoted = False
        column_type = ''

        # store all the raw filter data
        my.raw_filters.append( {
                'column': column,
                'value': values,
                'column_type': column_type,
                'op': op,
                'quoted': quoted,
                'table': table
        } )


        if not table:
            table = my.tables[0]


        assert op in ['in', 'not in']
        filter = ''
        if not values or values == ['']:
            where = "%s is NULL" %my.id_col
            #where = "NULL"
        else:
            list = [ Sql.quote(value) for value in values ]
            if table:
                where = '"%s"."%s" %s (%s)' % ( table, column, op, ", ".join(list) )
            else:
                where = '"%s" %s (%s)' % ( column, op, ", ".join(list) )

        my.add_where(where)



    def add_group_aggregate_filter(my, group_cols, column='id', aggregate='max'):
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

        table = my.get_table()

        # have to build the sql from scratch because Select can't handle
        # the complexity required
        subselect = []
        subselect.append( "SELECT")
        # NOTE: note allowed to scope by table in aggregate (Postgresql)
        #subselect.append( '%s("%s"."%s")' % (aggregate, table, column) )
        subselect.append( '%s("%s")' % (aggregate, column) )
        subselect.append( "FROM")

        if my.impl.get_database_type() == 'SQLServer':
            subselect.append( '[%s] as xxx' % table)
        else:
            subselect.append( '"%s" as xxx' % table)

        subselect.append( "WHERE")

        wheres = []
        for group_col in group_cols:
            
            if my.impl.get_database_type() == 'SQLServer':
                #wheres.append( 'xxx."%s" = %s.[%s].[%s]' % (group_col, my.database, table, group_col))
                wheres.append( 'xxx."%s" = [%s].[%s]' % (group_col, table, group_col))
            else:
                wheres.append( 'xxx."%s" = "%s"."%s"' % (group_col, table, group_col))


        wheres = " AND ".join(wheres)
        subselect.append(wheres)

        statement = " ".join(subselect)

        if  my.impl.get_database_type() == 'SQLServer':
            my.add_where('[%s].[%s] = (%s)' % (table, column, statement))
        else:
            my.add_where('"%s"."%s" = (%s)' % (table, column, statement))

    # Full text search filtering
    # NOTE: Only Postgres and SQLServer impl so far.  This likely will not work
    # on any other database
    #
    def add_text_search_filter(my, column, keywords, table=None):
        '''This will do full text searching on any column.  It is pretty
        brute force as it will convert each row to a ts_vector.
        '''
        if not table:
            # usually it's the only table in the list
            table = my.tables[0]
        column_types = my.impl.get_column_types(my.db_resource, table)
        column_type = column_types.get(column)
        
        where = my.impl.get_text_search_filter(column, keywords, column_type, table=table)
        my.add_where(where)



    def add_select_filter(my, column, select, op='in', table=''):
        '''combines results of one search filter with another search filter
        as a subselect

        example:

        SELECT * FROM "request" WHERE "id" in ( SELECT "request_id" FROM "job" WHERE "code" = '123MMS' )
        '''
        assert op in ['in','not in']
        statement = select.get_statement()
        my.add_filter(column, "( %s )" % statement, op=op, quoted=False, table=table)


    def add_group_by(my, group_by):
        if group_by == "": return
        my.group_bys.append(group_by)

    def add_having(my, having):
        if having == "": return
        my.havings.append(having)
        
    def add_order_by(my, order_by, direction='', table=''):
        if order_by == "": return

        if table:
            order_by = '"%s"."%s"' % (table, order_by)

        # we need to store the order_by_column name to maintain uniqueness so MS SQL doesn't error 
        if direction and not order_by.endswith(' desc') and not order_by.endswith(' asc'):
            if order_by not in my.order_by_columns:
                my.order_by_columns.append(order_by)
            else:
                return
            order_by = '%s %s' % (order_by, direction)
        
        elif order_by.endswith(' desc') or order_by.endswith(' asc'):
            tmps = order_by.split(' ')
            if tmps[0] not in my.order_by_columns:
                my.order_by_columns.append(tmps[0])
            else:
                return
        else: # for cases when asc is not specified (implied)
            if order_by not in my.order_by_columns:
                my.order_by_columns.append(order_by)
            else:
                return


        if order_by not in my.order_bys:
            my.order_bys.append(order_by)


    def add_enum_order_by(my, column, values, table=''):
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
        my.add_order_by( "\n".join(expr) )


    def add_limit(my, limit):
        '''deprecated: use set_limit'''
        my.limit = limit

    def set_limit(my, limit):
        my.limit = limit

    def set_offset(my, offset):
        my.offset = offset

    def get_statement(my, mode="normal"):
        if my.set_statement:
            return my.set_statement

        if my.impl:
            database_type = my.impl.get_database_type()
        else:
            database_type = Sql.get_default_database_type()


        # setup regex searches for direction (ascending or descending) of sort order (ignoring case)
        regex_asc = re.compile(' asc$', re.I)
        regex_desc = re.compile(' desc$', re.I)
        
        statement = []
        statement.append("SELECT");


        is_oracle = False
        if database_type == 'Oracle' and my.tables[0] not in ['USER_OBJECTS','ALL_TABLES']:
            is_oracle = True

        if mode == "count":
            if database_type=='PostgreSQL' and my.distinct_col:
                statement.append("count(DISTINCT %s)"%my.distinct_col)
            else:
                statement.append("count(*)")
        elif mode == "normal":
            if database_type =='SQLServer' and my.limit != None:
                total = int(my.limit) + my.offset
                statement.append("TOP %s " %total)
            if not my.columns:
                if is_oracle:
                    expr = '%s."%s".*' % (my.database, my.tables[0])
                    statement.append(expr)
                else:
                    if database_type=='PostgreSQL' and my.distinct_col:
                        statement.append("DISTINCT ON(%s) *"%my.distinct_col)
                    else:
                        #expr = '"%s".*' % (my.tables[0])
                        column_parts = []
                        if my.database:
                            column_parts.append('"%s"' % my.database)
                        if my.schema:
                            column_parts.append('"%s"' % my.schema)
                        column_parts.append('"%s"' % my.tables[0])
                        column_parts.append("*")
                        expr = ".".join(column_parts)

                        statement.append(expr)
            else:
                quoted_cols = []
                for i, column in enumerate(my.columns):
                    #FIXME: distinct in SQLServer should only appear once before the column names
                    if column == my.distinct_col:

                        parts = []
                        if my.database:
                            parts.append('"%s"' % my.database)
                        if my.schema:
                            parts.append('"%s"' % my.schema)
                        parts.append('"%s"' % my.column_tables[i])
                        prefix = ".".join(parts)
                        quoted_col = 'distinct %s."%s"' % (prefix, column)

                        #quoted_col = 'distinct "%s"."%s"' % (my.column_tables[i],column)
                    else:
                        #if column == '*':
                        #    quoted_col ='"%s".*' % (my.column_tables[i])
                        #else:
                        #    quoted_col = '"%s"."%s"' % (my.column_tables[i],column)
                        parts = []
                        if my.database:
                            parts.append('"%s"' % my.database)
                        if my.schema:
                            parts.append('"%s"' % my.schema)
                        parts.append('"%s"' % my.column_tables[i])
                        if column == '*':
                            parts.append(column)
                        else:
                            parts.append('"%s"' % column)
                        quoted_col = ".".join(parts)

                    # handle columns that have different names specified
                    if my.as_columns[i]:
                        quoted_col = "%s as \"%s\"" % (quoted_col, my.as_columns[i])

                    quoted_cols.append(quoted_col)


                statement.append(", ".join(quoted_cols) )

            if database_type =='SQLServer' and my.limit != None:
                order_by = 'ORDER BY id'
                order_bys = []
                for order_by in my.order_bys:
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
                statement.append(", ROW_NUMBER() over(%s) as %s " %(order_by, my.impl.get_temp_column_name()))

        if not my.tables:
            raise SqlException("No tables defined")

        clauses = []
        if my.tables[0].startswith('('):
            clauses.append("FROM %s" % my.tables[0] )
        elif my.database and is_oracle:
            clauses.append("FROM " + ", ".join( ['%s."%s"' % (my.database,x) for x in my.tables] ))
        # NOTE: There really is no reason for SQLServer to be different here.
        #elif my.database and database_type == 'SQLServer':
        #    clauses.append("FROM " + ", ".join( ['[%s]' % x for x in my.tables] ))
        else:
            #clauses.append("FROM " + ", ".join( ['"%s"."%s"."%s"' % (my.database,my.schema,x) for x in my.tables] ))

            # build full table string
            tables = []
            for table in my.tables:
                parts = []
                if my.database:
                    parts.append(my.database)
                if my.schema:
                    parts.append(my.schema)
                parts.append(table)
                table = ".".join( ['"%s"' % x for x in parts] )
                tables.append(table)

            clauses.append("FROM " + ", ".join(tables) )


        if my.joins:
            clauses.extend(my.joins)

        if len(my.filters):
            #my.wheres = my.filters.values()
            filters = my.filters.values()
            expanded = []
            for filter in filters:
                if len(filter) == 1:
                    expr = filter[0]
                else:
                    expr = '(%s)' % (' %s ' % my.filter_mode).join(filter)
                expanded.append(expr)
                
            my.wheres = expanded

       
        if len(my.wheres) > 0:
            wheres_copy = my.wheres[:]
            new_expr = my.process_wheres(wheres_copy)
            if new_expr:
                clauses.append("WHERE %s" % new_expr)
       
        #order_bys = []
        if mode == "normal":
            if len(my.group_bys) > 0:
                for item in my.order_bys:
                    if regex_asc.search(item) or regex_desc.search(item):
                        parts = order_by.split(" ")
                        item = parts[0]
                        
                    if item not in my.group_bys:
                        my.group_bys.append(item)

                group_by_stmt = ", ".join( ['"%s"' % x for x in my.group_bys] )
                
                clauses.append("GROUP BY %s" %group_by_stmt )

            if len(my.havings) > 0:
                # these are having expressions, no double quotes
                clauses.append("HAVING %s" % " AND ".join( my.havings ) )
                #clauses.append("HAVING %s" % ", ".join( ['"%s"' % x for x in my.havings] ))
               
            if not my.distinct and len(my.order_bys) > 0:
                order_bys = []
                for order_by in my.order_bys:
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

                    else:
                        if order_by.find(".") == -1:
                            order_bys.append('"%s"."%s"' % (my.tables[0],order_by))
                        else:
                            order_bys.append(order_by)
                
                clauses.append("ORDER BY %s" % ", ".join( order_bys ))
            
            #if database_type == "PostgreSQL":
            #   page = my.impl.get_page(my.limit, my.offset, my.tables[0]) 
            #   if page:
            #       clauses.append(page)

            if database_type not in ["Oracle", "SQLServer"]:
                page = my.impl.get_page(my.limit, my.offset) 
                if page:
                    clauses.append(page)

                #if my.limit != 0:
                #    clauses.append("LIMIT %s" % my.limit )
                #if my.offset != 0:
                #    clauses.append("OFFSET %s" % my.offset )
 

        clause = " ".join(clauses)
        statement.append(clause)
        statement = " ".join(statement)


        # NOTE: oracle and SQLServer uses the limit in the "where" clause
        # pre-orderg in, so have to do a subselect
        if mode != "count" and my.limit != None:
            if database_type in  ["Oracle",'SQLServer']:
                statement = my.impl.handle_pagination(statement, my.limit, my.offset)
        return statement




    def process_wheres(my, wheres):
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

        my.stack_index = 0
        while my.stack_index < len(wheres):
            expr = my._handle_stack_item(cur_stack, wheres)
            cur_stack = [expr]

        # strip out the outside brackets

        if not expr:
            return None

        if expr.startswith("( ") and expr.endswith(" )"):
            expr = expr[2:-2]

        return expr




    def _handle_stack_item(my, cur_stack, wheres):

        while 1:
            if my.stack_index >= len(wheres):
                #op = " AND " 
                #expr = "( %s )" % op.join(cur_stack)
                #return expr
                return " AND ".join(cur_stack)

            item = wheres[my.stack_index]
            my.stack_index += 1

            if item == "begin":

                # create a new stack
                new_stack = []
                # add it to the current stack
                cur_stack.append(new_stack)

                # go down a level
                expr = my._handle_stack_item(new_stack, wheres)

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



    def get_count(my):
        '''special statement that counts how many rows this query would
        return if executed.  This ignores the limit and offset tags'''
        statement = my.get_statement(mode="count")
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

    def __init__(my):
        my.table = None
        my.data = {}
        my.unquoted_cols = []
        my.escape_quoted_cols = []
        # optional database knowledge
        my.sql = None
        my.database = None
        my.column_types = {}
        my.impl = DatabaseImpl.get()

        my.schema = ""

    def __str__(my):
        return my.get_statement()



    def execute(my, sql=None):
        '''Actually execute the statement'''
        if not sql:
            sql = my.sql
        if not sql:
            raise SqlException("No connector found to execute query")

        conn = sql.get_connection()
        db_resource = sql.get_db_resource()
        vendor = db_resource.get_vendor()
        if vendor == "MongoDb":
            impl = db_resource.get_database_impl()
            impl.execute_insert(sql, my)




    def set_database(my, database):

        assert database == "sthpw" or not isinstance(database, basestring)

        if isinstance(database, basestring):
            my.sql = DbContainer.get(database)
            my.db_resource = DbResource.get_default(database)
        elif DbResource.is_instance(database):
        #elif isinstance(database, DbResource):
            my.sql = DbContainer.get(database)
            my.db_resource = database
            # set to database string internally
            database = database.get_database()
        elif isinstance(database, Sql):
            my.sql = database
            database = my.sql.get_database_name()
            my.db_resource = my.sql.get_db_resource()
        else:
            print "WARNING: it should be Sql instance, but it is not detected as such"
            my.sql = database
            database = my.sql.get_database_name()
            my.db_resource = DbResource.get_default(database)
            

        my.database = database
        my.impl = my.sql.get_database_impl()

        database_type = my.impl.get_database_type()
        if database_type == 'PostgreSQL':
            my.schema = "public"
        elif database_type == 'SQLServer':
            my.schema = "dbo"
        elif database_type == 'Sqlite':
            my.database = None



    def set_table(my, table):
        my.table = table

    def set_value(my, column, value, quoted=True, column_type="", escape_quoted=False):
        '''@params:
            quoted - determines whether the value needs to be quoted
        in the sql statement. 
            escape_quoted - more for PostgreSQL for now to do the E'' style quote'''
        if value == None:
            value = 'NULL'
            quoted = False

        if not column_type and my.sql:
            # get column type from database
            column_types = my.impl.get_column_types(my.db_resource, my.table)
            column_type = column_types.get(column)

          
            info = my.impl.process_value(column, value, column_type)
            if info:
                value = info.get("value")
                quoted = info.get("quoted")

        my.data[column] = value;

       
        if escape_quoted == True:
            my.escape_quoted_cols.append(column)
        elif not quoted:
            my.unquoted_cols.append(column)

    def get_data(my):
        return my.data


    def get_statement(my):
        database_type = my.impl.get_database_type()

        my.impl.preprocess_sql(my.data, my.unquoted_cols)

        # quote the values
        values = my.data.values()
        cols = my.data.keys()

        #if not cols:
        #    # add an empty row
        #    # FIXME: what is this??
        #    statement = "INSERT INTO \"%s\" (\"id\") values (default)" % my.table
        #    return statement

        statement = []


        if my.database and database_type == "Oracle":
            statement.append('INSERT INTO %s."%s"' % (my.database, my.table))
        #elif database_type == "SQLServer":
        #    statement.append('INSERT INTO [%s]' % my.table)
        else:
            #statement.append('INSERT INTO "%s"' % my.table)
            parts = []
            if my.database:
                parts.append('"%s"' % my.database)
            if my.schema:
                parts.append('"%s"' % my.schema)
            parts.append('"%s"' % my.table)
            table = ".".join(parts)

            statement.append('INSERT INTO %s' % table)


        quoted_values = []

        for i in range(0, len(cols)):
            unicode_escape = False
            value = values[i]

            if cols[i] in my.unquoted_cols:
                quoted_values.append( str(values[i]) )
            elif cols[i] in my.escape_quoted_cols:
                quoted_values.append(Sql.quote(values[i], has_outside_quotes=False, escape=True))
            else:

                if database_type == 'SQLServer':
                    unicode_escape = True
                quoted_values.append( Sql.quote(values[i], unicode_escape=unicode_escape) )
        # This is Oracle specific.  In Oracle, there is no auto increment
        # without creating triggers all over the place.
        if database_type == "Oracle" and "id" not in cols:
            cols.insert(0, "id")
            sequence_name = my.impl.get_sequence_name(my.table, my.database)
            #quoted_values.insert(0, '%s."%s".nextval' % (my.database,sequence_name))
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

        statement = my.impl.postprocess_sql(statement)

        return statement


    def get_id_statement(my):
        '''get the id from the last update. This should be called after
        the insert'''
        sequence = my.impl.get_sequence_name(my.table)
        return my.impl.get_currval_select(sequence)

 

        
class Update(object):
    '''class that non-linearly builds up an update statement'''

    def __init__(my):
        my.table = None
        my.data = {}
        my.filters = {}
        my.raw_filters = []
        my.wheres = []
        my.unquoted_cols = []
        my.escape_quoted_cols = []

        # optional database knowledge
        my.sql = None
        my.database = None
        my.column_types = {}

        my.impl = DatabaseImpl.get()

        my.schema = ""

    def __str__(my):
        return my.get_statement()




    def execute(my, sql=None):
        '''Actually execute the statement'''
        if not sql:
            sql = my.sql
        if not sql:
            raise SqlException("No connector found to execute query")

        conn = sql.get_connection()
        db_resource = sql.get_db_resource()
        vendor = db_resource.get_vendor()
        if vendor == "MongoDb":
            impl = db_resource.get_database_impl()
            impl.execute_update(sql, my)



    def set_database(my, database):

        assert database == "sthpw" or not isinstance(database, basestring)

        if isinstance(database, basestring):
            my.sql = DbContainer.get(database)
            my.db_resource = DbResource.get_default(database)
        #elif isinstance(database, DbResource):
        elif DbResource.is_instance(database):
            my.sql = DbContainer.get(database)
            my.db_resource = database
            # set to database string internally
            database = database.get_database()
        elif isinstance(database, Sql):
            my.sql = database
            database = my.sql.get_database_name()
            my.db_resource = my.sql.get_db_resource()
        else:
            print "WARNING: it should be Sql instance, but it is not detected as such"
            my.sql = database
            database = my.sql.get_database_name()
            my.db_resource = DbResource.get_default(database)
            

        my.database = database
        my.impl = my.sql.get_database_impl()

        database_type = my.impl.get_database_type()
        if database_type == 'PostgreSQL':
            my.schema = "public"
        elif database_type == 'SQLServer':
            my.schema = "dbo"
        elif database_type == 'Sqlite':
            my.database = None


    def set_table(my, table):
        my.table = table

    def set_value(my, column, value, quoted = True, column_type="", escape_quoted=False):
        '''quoted determines whether the value needs to be quoted
        in the sql statement. escape_quoted is more for PostgreSQL for now to do the E'' style quote'''

        if value == None:
            value = 'NULL'
            quoted = False

        if not column_type and my.sql:
            # get column type from database
            column_types = my.impl.get_column_types(my.db_resource, my.table)
            column_type = column_types.get(column)

            info = my.impl.process_value(column, value, column_type)
            if info:
                value = info.get("value")
                quoted = info.get("quoted")
        my.data[column] = value;
        if escape_quoted == True:
            my.escape_quoted_cols.append(column)
        elif quoted == False:
            my.unquoted_cols.append(column)

    def get_data(my):
        return my.data

    def add_where(my, where):
        if where == "":
            return
        my.filters[where] = where

    def remove_filter(my, name):
        #raise Exception("Sql.add_filter() is deprecated")
        if my.filters.get(name):
            my.filters.pop(name)


    def add_filter(my, column, value, column_type="", table="", quoted=None):
        assert my.table


        # store all the raw filter data
        my.raw_filters.append( {
                'column': column,
                'value': value,
                'column_type': column_type,
                #'op': op,
                #'table': table
                'quoted': quoted,
        } )


        if not column_type and my.sql:
            # get column type from database
            column_types = my.impl.get_column_types(my.db_resource, my.table)
            column_type = column_types.get(column)

            info = my.impl.process_value(column, value, column_type)
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

        my.add_where(where)


    def get_statement(my):
        impl = my.impl
        database_type = impl.get_database_type()

        impl.preprocess_sql(my.data, my.unquoted_cols)


        statement = []
        if my.database and database_type == "Oracle":
            statement.append('UPDATE %s."%s" SET' % (my.db_resource, my.table))
        #elif my.database and database_type == "SQLServer":
        #    statement.append('UPDATE [%s] SET' % my.table)
        else:
            #statement.append('UPDATE "%s" SET' % my.table)
            parts = []
            if my.database:
                parts.append('"%s"' % my.database)
            if my.schema:
                parts.append('"%s"' % my.schema)
            parts.append('"%s"' % my.table)
            table = ".".join(parts)

            statement.append('UPDATE %s SET' % table)




        # quote the values
        values = my.data.values()
        cols = my.data.keys()

        quoted_values = []


        for i in range(0, len(cols)):
            unicode_escape = False
            if cols[i] in my.unquoted_cols:
                quoted_values.append(values[i])
            elif cols[i] in my.escape_quoted_cols:
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


        if len(my.filters):
            my.wheres = my.filters.values()
            statement.append("WHERE %s" % ", ".join( my.wheres ))


        statement = " ".join(statement)
        statement = impl.postprocess_sql(statement)
        # build the statement
        return statement


    def get_id_statement(my):
        select = Select()
        select.add_column("id")
        select.add_table(my.table)

        if my.filters:
            my.wheres = my.filters.values()
            for where in my.wheres:
                select.add_where(where)

        return select.get_statement()




class Delete(object):

    def __init__(my):
        my.impl = None
        my.database = None
        my.table = ""

        my.raw_filters = []


    def set_database(my, database):

        assert database == "sthpw" or not isinstance(database, basestring)

        if isinstance(database, basestring):
            my.sql = DbContainer.get(database)
            my.db_resource = DbResource.get_default(database)
        #elif isinstance(database, DbResource):
        elif DbResource.is_instance(database):
            my.sql = DbContainer.get(database)
            my.db_resource = database
            # set to database string internally
            database = database.get_database()
        elif isinstance(database, Sql):
            my.sql = database
            database = my.sql.get_database_name()
            my.db_resource = my.sql.get_db_resource()
        else:
            print "WARNING: it should be Sql instance, but it is not detected as such"
            my.sql = database
            database = my.sql.get_database_name()
            my.db_resource = DbResource.get_default(database)
            

        my.database = database
        my.impl = my.sql.get_database_impl()

        #sql.do_update('DELETE from "ticket" where "code" is NULL;')


    def set_table(my, table):
        my.table = table


    def add_filter(my, name, value, op='='):
        my.raw_filters.append( {
            'name': name,
            'value': value,
            'op': op
        })


    def get_statement(my):

        parts = []

        parts.append("DELETE FROM")
        parts.append('''"%s"''' % my.table)
        parts.append("WHERE")

        for filter in my.raw_filters:
            expr = '"%s" %s \'%s\'' % (filter.get("name"), filter.get("op"), filter.get("value"))
            parts.append(expr)
            parts.append("AND")

        statement = " ".join(parts)
        return statement




class CreateTable(Base):
    '''Class to nonlinearly build up a create table statement'''

    def __init__(my, search_type=None):

        from pyasm.biz import Project
        if search_type:
            from search import SearchType
            search_type_sobj = SearchType.get(search_type)


            project = Project.get_by_search_type(search_type)
            my.db_resource = project.get_project_db_resource()

            my.table = search_type_sobj.get_table()

            sql = DbContainer.get(my.db_resource)
            my.impl = sql.get_database_impl()
        else:
            my.table = None
            from pyasm.search import DatabaseImpl
            my.impl = DatabaseImpl.get()

            project = Project.get()
            my.db_resource = project.get_project_db_resource()

        my.database = my.db_resource.get_database()

        my.columns = []
        my.primary_key = None
        my.constraints = []

        my.data = {}


    def set_table(my, table):
        my.table = table

    def get_table(my):
        return my.table


    def get_database(my):
        return my.db_resource.get_database()


    def add(my, name, type, length=None, not_null=False, primary_key=False):
        if type == "text":
            expr = my.impl.get_text(not_null=not_null)
        elif type == "char":
            expr = my.impl.get_char(length=length, not_null=not_null)
        elif type == "varchar":
            expr = my.impl.get_varchar(length=length, not_null=not_null)
        elif type == "int":
            expr = my.impl.get_int(not_null=not_null)
        elif type == "timestamp":
            expr = my.impl.get_timestamp(not_null=not_null)
        elif type == "boolean":
            expr = my.impl.get_boolean(not_null=not_null)
        elif type == "serial":
            expr = my.impl.get_serial(not_null=not_null)

            
        # SQL Server
        elif type == "uniqueidentifier":
            expr = my.impl.get_text(not_null=not_null)
        elif type in ["datetime", "datetime2"]:
            expr = my.impl.get_timestamp(not_null=not_null)
        elif type.startswith("datetimeoffset"):
            expr = my.impl.get_timestamp(not_null=not_null, timezone=True)
        elif type == "nvarchar":
            expr = my.impl.get_nvarchar(length=length, not_null=not_null)

        else:
            expr = type

        col_data = {
            'type': expr,
            'length': length,
            'not_null': not_null,
            'primary_key': primary_key
        }
        my.data[name] = col_data
        if primary_key:
            my.primary_key = name


    def add_column(my, name, type, length=None, not_null=False, primary_key=False):
        return my.add(name, type, length, not_null, primary_key=primary_key)


    def set_primary_key(my, name):
        if my.primary_key:
            raise TacticException("Primary key is already set")
        my.data[name]['primary_key'] = True
        my.primary_key = name



    def add_constraint(my, columns, mode="UNIQUE"):
        constraint = {
            'columns': columns,
            'mode': mode
        }
        my.constraints.append(constraint)



    
    def get_statement(my):
        if my.impl.get_database_type() == 'SQLServer':
            statement = 'CREATE TABLE [%s] (\n' % my.table
        else:
            statement = 'CREATE TABLE "%s" (\n' % my.table

        expressions = []
        for column, col_data in my.data.items():

            type = col_data.get('type')
            length = col_data.get('length')
            not_null = col_data.get('not_null')
            primary_key = col_data.get('primary_key')

            if type == "text":
                expr = my.impl.get_text(not_null=not_null)
            elif type == "varchar":
                expr = my.impl.get_varchar(length=length, not_null=not_null)
            elif type == "nvarchar":
                expr = my.impl.get_nvarchar(length=length, not_null=not_null)
            elif type == "int":
                expr = my.impl.get_int(not_null=not_null)
            elif type == "timestamp":
                expr = my.impl.get_timestamp(not_null=not_null,default='now')
            elif type == "boolean":
                expr = my.impl.get_boolean(not_null=not_null)
            elif type == "serial":
                expr = my.impl.get_serial()
            else:
                expr = type

            if primary_key:
                expr = "%s PRIMARY KEY" % expr

                if my.impl.get_database_type() in ['Sqlite']:
                    expr = "%s AUTOINCREMENT" % expr


            expression = '    "%s" %s' % (column, expr)
            expressions.append(expression)

        #if my.primary_key != None:
        #    expressions.append('    PRIMARY KEY ("%s")' % my.primary_key)


        for constraint in my.constraints:
            columns = constraint.get("columns")
            mode = constraint.get("mode")
            suffix = 'idx'
            if mode.upper() =='UNIQUE':
                suffix = 'unique'
            # could be a dangling constraint
            if not columns:
                continue
            name = "%s_%s_%s" % (my.table, "_".join(columns), suffix )
            expr = '    CONSTRAINT "%s" %s (%s)' % (name, mode, ", ".join(columns))
            expressions.append(expr)

            # FIXME: not sure about this. Bad merge?  Besides, this is handled
            # above
            #primary_key_stmt = my.impl.get_constraint('PRIMARY KEY', columns=[my.primary_key], table=my.table)
            #expressions.append('    PRIMARY KEY ("%s")' % my.primary_key)
            #expressions.append('   %s' %primary_key_stmt)

        statement += ",\n".join(expressions)
        statement += "\n"
        statement += ");\n"

        return statement



    def commit(my, sql=None):
        '''create a standard tactic table'''
        assert sql or my.database

        if sql:
            my.database = sql.get_database_name()
            db_resource = sql.get_db_resource()

        else:
            sql = DbContainer.get(my.db_resource)
            db_resource = my.db_resource

        impl = sql.get_database_impl()
        exists = impl.table_exists(db_resource, my.table)
        if not exists:

            if sql.get_vendor() == "MongoDb":
                impl.execute_create_table(sql, my)
            else:
                statement = my.get_statement()
                sql.do_update(statement)

            sql.clear_table_cache(my.database)

        else:
            print "WARNING: table [%s] exists ... skipping" % my.table
            defined_cols = set( sql.get_column_info(my.table).keys() )
            desired_cols = set( [x[0] for x in my.columns] )
            diff1 = defined_cols.difference(desired_cols)
            if diff1:
                print "... extra columns in database: ", diff1
            diff2 = desired_cols.difference(defined_cols)
            if diff2:
                print "... new columns in definition: ", diff2
            if not diff1 and not diff2:
                print "... definition the same as in the database"

        # create a sequence for the id
        try:
            if impl.__class__.__name__ == 'OracleImpl': 
                sequence = impl.get_sequence_name(my.table)
                statement = my.impl.get_create_sequence(sequence)
                sql.do_update(statement)
        except Exception, e:
            print "WARNING: ", str(e)



class DropTable(Base):
    def __init__(my, search_type=None):
        my.search_type = search_type
        # derive db from search_type_obj
        from search import SearchType
        from pyasm.biz import Project
        my.db_resource = Project.get_db_resource_by_search_type(my.search_type)
        my.database = my.db_resource.get_database()

        search_type_obj = SearchType.get(search_type)
        assert my.database
        my.table = search_type_obj.get_table()
        my.statement = my.get_statement()

    def get_statement(my):
        sql = DbContainer.get(my.db_resource)
        if sql.get_database_type() == 'SQLServer':
            statement = 'DROP TABLE [%s]' % my.table
        else:        
            statement = 'DROP TABLE "%s"' % my.table

        return statement

    def commit(my):
        sql = DbContainer.get(my.db_resource)
        if not sql.table_exists(my.table):
            print "WARNING: table [%s] does not exist in database [%s]" % (my.table, my.database)
            return

        # dump table into sql first
        tmp_dir = Environment.get_tmp_dir()
        schema_path = "%s/cache/drop_%s_%s.sql" % \
            (tmp_dir, my.database, my.table)

        if os.path.exists(schema_path):
            os.unlink(schema_path)

        # dump the table to a file and store it in cache
        from sql_dumper import TableSchemaDumper
        dumper = TableSchemaDumper(my.search_type)
        try:
            # should i use mode='sobject'? it defaults to 'sql'
            dumper.dump_to_tactic(path=schema_path)
        except SqlException, e:
            print "SqlException: ", e
            raise

        sql.do_update(my.statement)
        sql.clear_table_cache()




class AlterTable(CreateTable):
    '''Class to nonlinearly build up an alter table statement'''

    def __init__(my, search_type=None):
        super(AlterTable, my).__init__(search_type)
        """
        my.search_type = search_type
        # derive db from search_type_obj
        from search import SearchType
        search_type_obj = SearchType.get(search_type)
        my.database = search_type_obj.get_database()
        """
        assert my.database
        my.drop_columns = []

    def drop(my, name):
        #TODO: check if this column exists
        #print "COL NAME ", name
        my.drop_columns.append(name)

    def verify_table(my):
        from search import SearchType
        if not my.table and my.search_type:
            search_type_obj = SearchType.get(my.search_type)
            my.table = search_type_obj.get_table()

    def modify(my, name, type, length=256, not_null=False):
        # must store not_null separately,
        is_not_null = not_null
        if type == "text":
            expr = my.impl.get_text(not_null=False)
        elif type == "varchar":
            expr = my.impl.get_varchar(length=length, not_null=False)
        elif type == "int":
            expr = my.impl.get_int(not_null=False)
        elif type == "float":
            expr = my.impl.get_float(not_null=False)
        elif type == "timestamp":
            if my.impl.get_database_type() == 'SQLServer':
                expr = my.impl.get_timestamp(not_null=False, default=None)
            else:
                expr = my.impl.get_timestamp(not_null=False)
        elif type == "boolean":
            expr = my.impl.get_boolean(not_null=False)
        else:
            expr = type

        my.columns.append( (name, expr, is_not_null) )

    def get_statements(my):
        my.verify_table()

        statements = []
        for value in my.columns:
            statement = my.impl.get_modify_column(my.table, value[0], value[1], value[2])
            statements.extend(statement)

        for value in my.drop_columns:

            # TODO: The following should be decided in DatabaseImpl()
            from pyasm.search.sql import Sql
            if my.impl.get_database_type() == 'SQLServer':
                statement = 'ALTER TABLE [%s] DROP COLUMN [%s]' \
                    % (my.table, value)
            else:
                statement = 'ALTER TABLE "%s" DROP "%s"' \
                    % (my.table, value)

            statements.append(statement)
        return statements


    # TEST
    def xxx_drop_column(my, column):

        sql = DbContainer.get("sthpw")
        columns = sql.get_columns(my.table)
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
        ''' % {'table': my.table, 'columns': columns_str}

        return statement



    def commit(my):
        '''Commit one or more alter table statements'''
        sql = DbContainer.get(my.db_resource)
        impl = sql.get_database_impl()
        #database = sql.get_database_name()
        exists = impl.table_exists(my.db_resource, my.table)
        
        if exists:
            statements = my.get_statements()
            for statement in statements:
                sql.do_update(statement)
        else:
            print "WARNING: table [%s] does not exist ... skipping" % my.table




