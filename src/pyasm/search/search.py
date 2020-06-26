#################################################################
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

__all__ = [ "SearchException", "SearchInputException", "SObjectException", "SObjectValueException", "Search", "SObject", "SearchType", "SObjectFactory", "SObjectUndo", "SearchKey" ]


import string, types, re, sys
import decimal
import uuid
from pyasm.common import *
from pyasm.common.spt_date import SPTDate

from .sobject_config import *
from .transaction import Transaction
from .sobject_mapping import *
from .database_impl import DatabaseImpl

import six
basestring = six.string_types

IS_Pv3 = sys.version_info[0] > 2

# Need to import this way because of how DbResource needs to get imported
from pyasm.search.sql import SqlException, DatabaseException, Sql, DbResource, DbContainer, DbPasswordUtil, Select, Insert, Update, CreateTable, DropTable, AlterTable

import datetime
from dateutil import parser

# this is done for performance reasons
from datetime import datetime as datetimeclass


class SearchException(TacticException):
    pass

class SearchInputException(TacticException):
    '''Error out for invalid data in SearchWdg'''
    pass

class SObjectException(TacticException):
    pass

class SObjectValueException(SObjectException):
    pass



# for dyanmically importing into this namespace
gl = globals()
lc = locals()




class Search(Base):
    '''Search engine using named search types.  The search returns a list of sobjects, which are the base class for entities retrieved from the database.

    Basic usage:

    search_type = "prod/asset"
    search = Search(search_type)
    serach.add_filter("asset_library", "chr")
    sobjects = search.get_sobjects()
    '''
    def __init__(self, search_type, project_code=None, sudo=False):
        # storage for result
        self.is_search_done = False
        self.sobjects = []


        # retired asset flag - retired assets are never shown by default
        self.show_retired_flag = False

        self.filter_mode = 'and'

        # flag that when set, returns empty
        self.null_filter = False
        self.security_filter = False

        protocol = 'local'
        if isinstance(search_type, basestring):
            # project is *always* local.  This prevents an infinite loop
            from pyasm.biz import Project
            if search_type != "sthpw/project":
                try:
                    from pyasm.security import Site
                    site = Site.get_site()
                    key = "Search:resource:%s:%s" % (site, search_type)
                    parts = Container.get(key)
                    if not parts:
                        if not project_code:
                            project_code = Project.extract_project_code(search_type)
                        project = Project.get_by_code(project_code)
                        #assert(project)
                        if not project:
                            raise SearchException("Cannot find project [%s]" % project_code)

                        resource = project.get_resource()
                        protocol = resource.get_protocol()

                        xx = resource.get_project()
                        if xx:
                            project_code = xx

                        parts = [project_code, protocol]
                        Container.put(key, parts)
                    else:
                        cached_project_code, protocol = parts
                        if not project_code:
                            project_code = cached_project_code
                        

                    if protocol == 'xmlrpc':
                        self.select = RemoteSearch(search_type)
                        # build a dummy search_type object.  Should this be
                        # build from the real remote info?
                        self.search_type_obj = SearchType.create("sthpw/search_object")
                        self.search_type_obj.set_value("search_type", search_type)
                        return

                except Exception as e:
                    print("WARNING [%s]: Search constructor:" % search_type, str(e))
                    raise


        if search_type == None:
            raise SearchException("search_type is None")


        # get the search type sobject for the search
        if isinstance(search_type, type):
            # get search defined in the class
            search_type = search_type.SEARCH_TYPE
            self.search_type_obj = SearchType.get(search_type)

        elif isinstance(search_type, basestring):
            self.search_type_obj = SearchType.get(search_type)
        else:
            self.search_type_obj = search_type
            search_type = self.search_type_obj.get_base_key()

        from pyasm.biz import Project
        if project_code:
            self.project_code = project_code
        else:
            self.project_code = Project.extract_project_code(search_type)

        base_search_type = SearchKey.extract_base_search_type(search_type)

        if not sudo:
            self.check_security()
       
        # Put in a security check for search types that are not sthpw
        # or config.
        # The "sthpw" and "config" namespaces are always searchable (or
        # TACTIC won't function)
        #
        from pyasm.security import get_security_version
        security = Environment.get_security()
        security_version = get_security_version()
        if security_version >= 2:
            # special conditions of task, note and work_hour
            if search_type in ['sthpw/task', 'sthpw/note','sthpw/work_hour']:
                current_project_code = Project.get_project_code()
                key = { "code": base_search_type }
                key2 = { "code": base_search_type, "project": current_project_code }
                key3 = { "code": "*" }
                key4 = { "code": "*", "project": current_project_code }
                keys = [key, key2, key3, key4]
                default = "allow"
                if not security.check_access("search_type", keys, "view", default=default):
                    print("WARNING: User [%s] security failed for search type [%s]" % (Environment.get_login().get_code(), search_type))
                    self.set_null_filter()

            elif not search_type.startswith("sthpw/") and not search_type.startswith("config/"):
                key = { "code": base_search_type }
                key2 = { "code": base_search_type, "project": self.project_code }
                key3 = { "code": "*" }
                key4 = { "code": "*", "project": self.project_code }
                keys = [key, key2, key3, key4]
                default = "deny"
                if not security.check_access("search_type", keys, "view", default=default):
                    print("WARNING: User [%s] security failed for search type [%s]" % (Environment.get_login().get_code(), search_type))
                    self.set_null_filter()

        else:
            # special conditions of task, note and work_hour
            if search_type in ['sthpw/task', 'sthpw/note','sthpw/work_hour']:
                current_project_code = Project.get_project_code()
            else:
                current_project_code = self.project_code
            key = {
                'project' : current_project_code,
                'search_type' : base_search_type
            }
            security = Environment.get_security()
            if not security.check_access("sobject", key, "view"):
                self.set_null_filter()


 
       
        # provide the project_code kwarg here
        self.full_search_type = Project.get_full_search_type(search_type, project_code=self.project_code)

        self.db_resource = Project.get_db_resource_by_search_type(self.full_search_type)

        #self.db_resource = None
        if self.db_resource:
            self.database = self.db_resource.get_database()
            self.host = self.db_resource.get_host()
        else:
            self.database = Project.get_database_by_search_type(self.full_search_type)
            self.host = Project.extract_host(self.full_search_type)
            self.db_resource = DbResource(database=self.database, host=self.host)

        # verify this db exists
        db_exists = self.db_resource.exists()
        if not db_exists:
            raise SearchException('This database [%s] does not exist' %self.database)
        self.database_impl = self.db_resource.get_database_impl()


        self.select = Select()
        self.select.set_database(self.db_resource)
        self.select.set_id_col(self.get_id_col())

        assert DbResource.is_instance(self.db_resource)


        table = self.search_type_obj.get_table()
        exists = self.database_impl.table_exists(self.db_resource, table)   

        if not search_type == 'sthpw/virtual' and not exists:
            raise SearchException('This table [%s] does not exist for database [%s]' %(table, self.database))

        # add the table
        self.select.add_table(table)

        
        # remember the order bys
        self.order_bys = []
        # order_by is applied by default if available
        self.order_by = True



    def check_security(self):
        from pyasm.security import Sudo
        user = Environment.get_user_name()

        search_type = self.get_base_search_type()
        api_mode = Environment.get_api_mode()

        if api_mode in ['open', '', None]:
            return

        # Commented our for testing
        if user in ['admin']:
            return

        if Sudo.is_sudo():
            return


        if search_type in {
                'sthpw/login',
                'sthpw/login_in_group',
                'sthpw/login_group',
                'sthpw/transaction_log',
                'sthpw/change_timestamp',
                'sthpw/exception_log',
                'sthpw/ticket',
                #'sthpw/search_object'
                #'config/project_settings',
        }:
            raise Exception("Search Permission Denied [%s]" % search_type)




    def copy(self):
        search = Search(self.full_search_type)

        # copy the select
        search.select = self.select.copy()

        search.order_bys = self.order_bys[:]
        search.order_by = self.order_by

        return search




    def set_search_done(self, flag=True):
        self.is_search_done = flag


    def get_database_impl(self):
        return self.database_impl


    def get_sql(self):
        return self.db_resource.get_sql()


       

    def get_project(self):
        from pyasm.biz import Project
        return Project.get_by_code(self.project_code)

    def get_select(self):
        '''returns the select object'''
        return self.select


    def get_project_code(self):
        return self.project_code

    def get_database(self):
        '''get the database that represents this Search'''
        return self.database

    def get_db_resource(self):
        return self.db_resource


    def set_filter_mode(self, mode):
        self.select.set_filter_mode(mode)


    def get_search_type(self):
        return self.full_search_type


    def get_table(self):
        return self.search_type_obj.get_table()


    def get_full_search_type(self):
        return self.full_search_type

    def get_search_type_obj(self):
        return self.search_type_obj


    def get_base_search_type(self):
        return self.search_type_obj.get_base_key()



    def get_id_col(self):
        '''returns the column which stores the id of the sobject'''
        search_type = self.full_search_type
        key = "SObject::%s::id_col" % search_type
        id_col = Container.get(key)
        if not id_col:
            database_impl = self.db_resource.get_database_impl()
            id_col =  database_impl.get_id_col(self.db_resource, search_type)
            Container.put(key, id_col)

        return id_col



    def get_code_col(self):
        '''returns the column which stores the id of the sobject'''
        database_impl = self.db_resource.get_database_impl()
        search_type = self.full_search_type
        return database_impl.get_code_col(self.db_resource, search_type)



    def get_statement(self):
        return self.select.get_statement()

    def add_column(self, column, distinct=False, table=None, as_column=None):
        self.select.add_column(column, distinct, table=table, as_column=as_column)


    def get_columns(self, table=None, show_hidden=False):
        #database = self.get_database()
        sql = DbContainer.get(self.db_resource)

        if not table:
            table = self.search_type_obj.get_table()
        columns = sql.get_columns(table)
        #columns = self.remove_temp_column(columns, sql) 

        return columns


    def set_distinct_col(self, column):
        self.select.set_distinct_col(column)


    def get_column_info(self):
        table_name = self.search_type_obj.get_table()
        info = self.database_impl.get_column_info(self.db_resource, table_name)
        return info

    def column_exists(self, column):
        column_info = self.get_column_info()
        has_column = column_info.get(column) != None
        return has_column


    # DEPRECATED: this should not be used as it assumes an SQL database
    def add_where(self, filter):
        '''add an explicit where clause'''
        self.select.add_where(filter)

    # DEPRECATED: Still called in self.skip_retired()
    def remove_where(self, filter):
        '''add an explicit where clause'''
        self.select.remove_where(filter)


    def add_regex_filter(self, name, regex, op='EQI'):
        '''add a regular expression filter
            EQ = equal case-sensitive
            EQI = equal case-insensitive
            NEQ = not equal case-sensitive
            NEQI = not equal case-insensitive '''
        #self.select.add_filter(name, Search.get_regex_filter(name, regex, op))
        self.select.add_where(Search.get_regex_filter(name, regex, op, self.database_impl))
      

    def get_regex_filter(name, regex, op='EQI', impl=None):
        if regex:
            regex = re.sub(r"'", r"''", regex)
        else:
            regex = ''

        if not impl:
            impl = DatabaseImpl.get()
        return impl.get_regex_filter(name, regex, op)
      
    get_regex_filter = staticmethod(get_regex_filter)



    def set_null_filter(self):
        self.null_filter = True

    def set_security_filter(self):
        '''set it after Security has done alter_search()'''
        self.security_filter = True



    def add_filter(self, name, value, op='=', quoted=None, table=''):
        if name == None:
            raise SearchException("Cannot add null as a name in filter")
        #filter = self.get_filter(name, value, op)
        #self.select.add_where(filter)

        if value == "__ALL__":
            return

        self.select.add_filter(name, value, op=op, quoted=quoted, table=table)


    def add_filters(self, name, values, table='', op='in'):
        ''' add a where name in (val1, val2, ...) '''
        self.select.add_filters(name, values, op=op, table=table)



    def add_null_filter(self, name):
        self.add_filter(name, "NULL", quoted=False, op="is")


    def add_empty_filter(self, name):
        self.add_op("begin")
        self.add_filter(name, "NULL", quoted=False, op="is")
        self.add_filter(name, "", op="=")
        self.add_op("or")
        print("sss: ", self.get_statement())


    def add_search_filter(self, name, search, op='in', table=''):
        '''combines results of one search filter with another search filter
        as a subselect

        example:

        SELECT * FROM "request" WHERE "id" in ( SELECT "request_id" FROM "job" WHERE "code" = '123MMS' )
        '''
        select = search.get_select()

        search_type = self.get_search_type()
        related_type = search.get_search_type()

        search_type_obj = SearchType.get(search_type)
        related_type_obj = SearchType.get(related_type)


        can_join = DatabaseImpl.can_search_types_join(search_type, related_type)
        if not can_join:
            column = select.columns[0]
            sobjects = search.get_sobjects()
            values = SObject.get_values(sobjects, column, unique=True)
            self.add_filters(name, values)
        else:
            self.select.add_select_filter(name, select, op, table=table)

    def add_op(self, op, idx=None):
        '''add operator like begin, and, or. with an idx number, it will be inserted instead of appended'''
        self.select.add_op(op, idx=idx)

    def is_expr(value):
        '''return True if it is an expression based on starting chars'''
        if not isinstance(value, basestring):
            value = str(value)
        is_expr = re.search("^(@|\$\w|{@|{\$\w)", value)
        return is_expr

    is_expr = staticmethod(is_expr)


    def add_op_filters(self, filters):
        '''method to add many varied filters to search.  This is used in
        the Client API, for example.'''

        if isinstance(filters, basestring):
            filters =  filters.replace("&gt;", ">")
            filters =  filters.replace("&lt;", "<")
            filters = jsonloads(filters)

        for filter in filters:
            if not filter:
                continue
            if isinstance(filter, basestring) or len(filter) == 1:
                # straight where clause not allowed
                if isinstance(filter, basestring):
                    where = filter
                else:
                    where = filter[0]
                if where in ['begin','and','or']:
                    self.add_where(where)
                else:
                    raise SearchException('Single argument filter is no longer supported. Try to use 2 or 3 arguments.')

            elif len(filter) == 2:
                name, value = filter
               
                table = ""
                if name.find(".") != -1:
                    parts = name.split(".")
                    table = parts[0]
                    name = parts[1]

                if name.startswith("@"):
                    if name == '@ORDER_BY':
                        self.add_order_by(filter[1])
                    elif name == '@LIMIT':
                        self.set_limit(filter[1])
                    elif name == '@OFFSET':
                        self.set_offset(filter[1])
                    elif name == '@UNIQUE':
                        self.add_column(filter[1], distinct=True)


                elif isinstance(value, basestring):
                    # <name> = '<value>'
                    if self.is_expr(value):
                        value = Search.eval(value, single=True)
                    self.add_filter(name, value, table=table)
                    #print('name: [%s],[%s]' % (name, value))
                elif isinstance(value, (int, float, bool)):
                    # <name> = '<value>'
                    self.add_filter(name, value, table=table)
                else:
                    # <name> in ('<value1>', '<value2>')
                    self.add_filters(name, value, table=table)

            elif len(filter) == 4:
                name, op, start, end = filter

                table = ""
                if name.find(".") != -1:
                    parts = name.split(".")
                    table = parts[0]
                    name = parts[1]



                if op in ["in between", "between"]:
                    self.add_date_range_filter(name, start, end, table=table)


            elif len(filter) == 3:
                name, op, value = filter
               
                op = op.replace("lte", "<=")
                op = op.replace("gte", ">=")
                op = op.replace("lt", "<")
                op = op.replace("gt", ">")
                if self.is_expr(value):
                    value = Search.eval(value, single=True)



                table = ""
                if name.find(".") != -1:
                    parts = name.split(".")
                    table = parts[0]
                    name = parts[1]

                if isinstance(value, basestring) and value.startswith("{") and value.endswith("}"):
                    value = Search.eval(value, single=True)


                assert op in ('like', 'not like', '<=', '>=', '>', '<', 'is','is not', '~', '!~','~*','!~*','=','!=','in','not in','EQ','NEQ','EQI','NEQI','is after','is before','is on','@@')
                #self.add_where( "\"%s\" %s '%s'" % (name,op,value))
                if op in ('in', 'not in'):
                    if isinstance(value, basestring):
                        values = value.split('|')
                    else:
                        values = value
                    #avoid empty value
                    values  = [x for x in values if x]
                    self.add_filters(name, values, op=op, table=table)
                elif op in ['EQ','NEQ','EQI','NEQI']:
                    self.add_regex_filter(name, value, op)
                elif op in ['@@']:
                    value = value.replace('"', "'")
                    self.add_text_search_filter(name, value, table=table)

                else:
                    if op == 'is after':
                        op = '>='
                    elif op == 'is before':
                        op = '<='
                    
                    quoted = True
                    if isinstance(value, int) or isinstance(value, float):
                        quoted = False

                    # special case for NULL
                    if value == 'NULL':
                        quoted = False
                    if op == 'is on':
                        self.add_day_filter(name, value)
                    else:
                        self.add_filter( name, value, op=op, quoted=quoted, table=table)


    def add_day_filter(self, name, value):
        ''' is on a particular day'''
        date = Date(db_date=value)
        value = date.get_db_date()
        date.add_days(1)
        end_value = date.get_db_date()
        self.add_filter(name, value, op='>=')
        self.add_filter(name, end_value, op='<')


    def add_interval_filter(self, name, value):
        self.add_where( Select.get_interval_where(value,name) )


    def add_sobject_filter(self, sobject, prefix="", op=None):
        '''convenience function to add a filter for the given sobject'''
        self.add_filter("%ssearch_type" % prefix, sobject.get_search_type() )

        if SearchType.column_exists(sobject.get_search_type(), "code") and \
            SearchType.column_exists(self.get_search_type(), "%ssearch_code" % prefix):
            search_code = sobject.get_value("code")
            if not op:
                op = '='
            self.add_filter("%ssearch_code" % prefix, search_code, op=op )
        else:
            if not op:
                op = '='
            self.add_filter("%ssearch_id" % prefix, sobject.get_id(), op=op )



    def add_sobjects_filter(self, sobjects, prefix="", op='in'):
        '''convenience function to add a filter for the given sobjects'''

        if not sobjects:
            return

        search_type = sobjects[0].get_search_type()
        self.add_filter("%ssearch_type" % prefix, search_type )

        # assume they are of the same type
        sobject = sobjects[0]
        if self.column_exists("%ssearch_code" % prefix):
            search_codes = [x.get_value("code") for x in sobjects if x]
            self.add_filters("%ssearch_code" % prefix, search_codes, op=op )
        else:
            search_ids = [str(x.get_id()) for x in sobjects if x]
            self.add_filters("%ssearch_id" % prefix, search_ids, op=op )



    def add_parent_filter(self, parent, relationship=None):
        '''use the schema to determine the relationship and then add the
        appropriate filter'''
        if not parent:
            self.add_id_filter(0)
            return

        if isinstance(parent, basestring):
            parent = Search.get_by_search_key(parent)

        #parent_search_type = parent.get_base_search_type()
        #search_type = self.get_base_search_type()
        parent_search_type = parent.get_search_type()
        search_type = self.get_search_type()

        if parent_search_type == search_type:
            print("WARNING: parent type and search type are the same for [%s]" % parent_search_type)
            self.add_id_filter(parent.get_id())
            return

        from pyasm.biz import Schema

        schema = Schema.get(project_code=self.project_code)

        if not relationship:
            relationship = schema.get_relationship(parent_search_type, search_type)

        if not relationship:
            raise SearchException("Search type [%s] is not related to search_type [%s]" % ( parent_search_type, search_type) )

        attrs = schema.get_relationship_attrs(parent_search_type, search_type, path=None)
        if relationship == "code":
            self.add_relationship_filter(parent)
            #self.add_filter(parent.get_foreign_key(), parent.get_code() )
        elif relationship == "id":
            self.add_relationship_filter(parent)
            #self.add_filter(parent.get_foreign_key(), parent.get_id() )
        elif relationship == "parent_code":
            self.add_filter("parent_code", parent.get_code() )
        elif relationship in ["search_type", "search_code", "search_id"]:

            if relationship == "search_type":
                full_parent_search_type = parent.get_search_type()
                full_search_type = self.get_search_type()
                relationship = schema.resolve_search_type_relationship(attrs, full_parent_search_type, full_search_type)

            prefix = attrs.get("prefix")
            if prefix:
                prefix = "%s_" % prefix
            else:
                prefix = ""
            self.add_filter("%ssearch_type" % prefix, parent.get_search_type() )
            #self.add_filter("%ssearch_id" % prefix, parent.get_id() )
            self.add_filter("%ssearch_code" % prefix, parent.get_code() )





    def add_relationship_filter(self, sobject, path=None):
        '''adds a filter to the current search that are related to the passed
        in sobject.  The schema takes care of figuring out how to relate
        the two search_types
        '''
        base_search_type = self.get_base_search_type()
        #related_type = sobject.get_base_search_type()
        search_type = self.get_search_type()
        related_type = sobject.get_search_type()
        
        if search_type == related_type:
            print("WARNING: related type and search type are the same for [%s]" % search_type)
            self.add_id_filter(sobject.get_id())
            return

        from pyasm.biz import Schema

        if self.project_code == 'sthpw':
            related_project_code = sobject.get_project_code()
            schema = Schema.get(project_code=related_project_code)
        else:
            schema = Schema.get(project_code=self.project_code)
        
        attrs = schema.get_relationship_attrs(search_type, related_type, path)
        if not attrs:
            raise SearchException("Search type [%s] is not related to search_type [%s]" % ( search_type, related_type) )

        if attrs.get("disabled") == True:
            self.null_filter = True
            return


        relationship = attrs.get('relationship')
        my_is_from = attrs['from'] in [base_search_type, '*']

        from_col = attrs.get('from_col')
        to_col = attrs.get('to_col')

        if relationship == "search_type":
            relationship = schema.resolve_search_type_relationship(attrs, search_type, related_type)
        
        if relationship in ['id', 'code']:
            if my_is_from:
                value = sobject.get_value(to_col)
                if not value:
                    self.null_filter = True
                    return
                self.add_filter(from_col, value )
            else:
                value = sobject.get_value(from_col)
                if not value:
                    self.null_filter = True
                    return
                self.add_filter(to_col, value )
        elif relationship in ['search_id']:

            prefix = attrs.get("prefix")
            if prefix:
                prefix = "%s_" % prefix
            else:
                prefix = ""
            if my_is_from:
                self.add_filter("%ssearch_type" % prefix, sobject.get_search_type() )
                self.add_filter("%ssearch_id" % prefix, sobject.get_id() )
            else:
                self.add_filter(self.get_id_col(), sobject.get_value("search_id"))

        elif relationship in ['search_code']:
            prefix = attrs.get("prefix")
            if prefix:
                prefix = "%s_" % prefix
            else:
                prefix = ""

            if my_is_from:
                self.add_filter("%ssearch_type" % prefix, sobject.get_search_type() )
                self.add_filter("%ssearch_code" % prefix, sobject.get_code() )
            else:
                self.add_filter("code", sobject.get_value("search_code"))


        elif relationship in ['instance']:

            instance_type = attrs.get("instance_type")
            assert(instance_type)

            self.add_join(instance_type, search_type)
            self.add_join(related_type, instance_type)

            search_type_obj = SearchType.get(search_type)
            related_type_obj = SearchType.get(related_type)

            table = search_type_obj.get_table()
            related_table = related_type_obj.get_table()
            self.add_column("*", table=table)
            self.add_column("code", table=related_table, as_column="_related_code")

            if my_is_from:
                value = sobject.get_value(to_col)
                if not value:
                    self.null_filter = True
                    return
                self.add_filter(from_col, value, table=related_table )
            else:
                value = sobject.get_value(from_col)
                if not value:
                    self.null_filter = True
                    return
                self.add_filter(to_col, value, table=table )

 
        else:
            raise SearchException("Relationship [%s] not supported yet" % relationship)




    def add_relationship_filters(self, sobjects, op='in', path=None, type=None):
        '''adds a filter to the current search that are related to the passed
        in sobjects.  The schema takes care of figuring out how to relate
        the two search_types

        This method is relatively slower than "add_relationship_search_filter"
        because it required you to already have the full sobjects.
        '''
        if not sobjects:
            self.null_filter = True
            return

        sobject = sobjects[0]

        search_type = self.get_base_search_type()
        related_type = sobjects[0].get_base_search_type()
        
        project_code = self.project_code
        # should go by this search_type's project_code


        from pyasm.biz import Schema
        if project_code == 'sthpw':
            related_project_code = sobjects[0].get_project_code()
            schema = Schema.get(project_code=related_project_code)
        else:
            schema = Schema.get(project_code=project_code)

        attrs = schema.get_relationship_attrs(search_type, related_type, path=path, type=type)

        relationship = attrs.get('relationship')


        # handle case where both search types are the same
        # NOTE: currently instances don't work well when the src and dst search
        # type are the same as it produces an incorrect SQL reference the
        # table twice.  Until this is resolved, use this more inefficeint method
        if search_type == related_type and (not attrs or relationship == 'instance'):
            has_code = SearchType.column_exists(search_type, "code")
            if has_code:
                self.add_filters("code", [x.get_value("code") for x in sobjects], op=op)
            else:
                self.add_filters(sobject.get_id_col(), [x.get_id() for x in sobjects], op=op)
            return




        if not attrs:
            raise SearchException("Search type [%s] is not related to search_type [%s]" % ( search_type, related_type) )

        if attrs.get("disabled") == True:
            self.null_filter = True
            return


        my_is_from = attrs['from'] == search_type

        from_col = attrs.get('from_col')
        to_col = attrs.get('to_col')

        if relationship in ['id', 'code']:
            if my_is_from:
                col_values  = [x.get_value(to_col) for x in sobjects]
                self.add_filters(from_col, col_values, op=op )
            else:
                col_values  = [x.get_value(from_col) for x in sobjects]
                self.add_filters(to_col, col_values, op=op )
        elif relationship in ['search_type','search_code','search_id']:

            prefix = attrs.get("prefix")
            if prefix:
                prefix = "%s_" % prefix
            else:
                prefix = ""

            if my_is_from:
                if not to_col:
                    attrs = schema.resolve_relationship_attrs(attrs, self.get_search_type(), sobjects[0].get_search_type())
                    to_col = attrs.get("to_col")
                    from_col = attrs.get("from_col")

                # quickly go through the sobjects to determine if the
                # search types are the same
                multi_stypes = False
                last_st = None
                for idx, sobject in enumerate(sobjects):
                    if idx == 0:
                        last_st = sobject.get_search_type()
                        continue
                    if sobject.get_search_type() != last_st:
                        multi_stypes = True
                        break

                if not multi_stypes:
                    col_values  = [x.get_value(to_col) for x in sobjects]

                    self.add_filter("%ssearch_type" % prefix, sobjects[0].get_search_type() )
                    if isinstance(col_values[0], six.integer_types):
                        self.add_filters(from_col, col_values, op=op )
                    else:
                        self.add_filters("%ssearch_code" % prefix, col_values, op=op)
                else:
                    if op != 'in':
                        raise SearchException("For searches with multi_stypes, op = 'in' must be used.");

                    # FIXME: why doesn't the ops work here?
                    filters = []
                    for sobject in sobjects:
                        search_type = sobject.get_search_type()
                        search_code = sobject.get_value(to_col)

                        #search.add_filter('search_type', search_type)
                        #search.add_filter(from_col, search_code)
                        #search.add_op("and")
                        filters.append("(search_type = '%s' and %s = '%s')" % (search_type, from_col, search_code))
                    self.add_where("( %s )" % " or ".join(filters))



            else:
                # assume default search_type/search_id schema like task, snapshot
                # filter out the sobjects that are not the same search type
                # as the search
                full_search_type = self.get_search_type()
                filtered_sobjects = []
                for sobject in sobjects:
                    if sobject.get_value("%ssearch_type" % prefix) != full_search_type:
                        continue
                    filtered_sobjects.append(sobject)
                sobjects = filtered_sobjects

                code_column = "%ssearch_code" % prefix
                has_code = SearchType.column_exists(related_type, code_column)

                if has_code:
                    column = "%ssearch_code" % prefix
                    column2 = "code"
                else:
                    column = "%ssearch_id" % prefix
                    column2 = "id"

                sobject_values = SObject.get_values(sobjects, column, unique=True)
                sobject_values = [x for x in sobject_values if x]
                self.add_filters(column2, sobject_values, op=op)

        elif relationship in ['instance']:
            instance_type = attrs.get("instance_type")
            assert(instance_type)

            self.add_join(instance_type, search_type)
            self.add_join(related_type, instance_type)


            search_type_obj = SearchType.get(search_type)
            related_type_obj = SearchType.get(related_type)

            table = search_type_obj.get_table()
            related_table = related_type_obj.get_table()
            self.add_column("*", table=table)

            self.add_column("code", table=related_table, as_column="_related_code")

            #raise SearchException("Relationship [%s] not supported yet" % relationship)

        else:
            raise SearchException("Relationship [%s] not supported yet" % relationship)




    def add_relationship_search_filter(self, search, op='in', delay_null=False, use_multidb=None, path=None):
        '''optimized relationship filter so that you don't need the results
        of the sub search.  This is much faster because the search is done
        completely in the database without having to go through the whole
        sobject conversion

        @param
        delay_null - If True, the set_null_filter action will not be executed when the search passed in has 0 result, this method returns False instead 

        For example
        
        (slow method):
            search = Search("MMS/job")
            sobjects = search.get_sobjects()
            search2 = Search("MMS/request")
            search2.add_relationship_filter(sobjects)

        (fast method)
            search = Search("MMS/job")
            search2 = Search("MMS/request")
            search2.add_relationship_search_filter(search)
        '''

        if not search:
            self.null_filter = True
            return False

        assert op in ['in', 'not in']

        search_type = self.get_base_search_type()
        full_search_type = self.get_search_type()
        related_type = search.get_base_search_type()
        full_related_type = search.get_search_type()

        search_type_obj = self.get_search_type_obj()
        table = search_type_obj.get_table()
        
        search.order_by = False

        if not path and search_type == related_type:
            #print("WARNING: related type and search type are the same for [%s]" % search_type)
            search.add_column("id")
            self.add_search_filter("id", search, op, table=table )
            return True

        from pyasm.biz import Schema
        if self.project_code == 'sthpw':
            related_project_code = search.project_code
            schema = Schema.get(project_code=related_project_code)
        else:
            schema = Schema.get(project_code=self.project_code)
        attrs = schema.get_relationship_attrs(search_type, related_type, path=path)
        if not attrs:
            raise SearchException("Search type [%s] is not related to search_type [%s]" % ( search_type, related_type) )


        relationship = attrs.get('relationship')

        my_is_from = attrs['from'] == search_type
        if relationship in ['id', 'code']:
            from_col = attrs['from_col']
            to_col = attrs['to_col']

            if my_is_from:
                search.add_column(to_col)
                self.add_search_filter(from_col, search, op, table=table )
            else:
                search.add_column(from_col)
                self.add_search_filter(to_col, search, op, table=table )
        elif relationship in ['search_type', 'search_code', 'search_id']:
            if relationship == 'search_type':
                relationship = schema.resolve_search_type_relationship(attrs, search_type, related_type)

            # see if a multi database join can be made
            can_join = DatabaseImpl.can_search_types_join(full_search_type, full_related_type)
            
            if can_join and use_multidb != None:
                can_join = use_multidb
            if Config.get_value('database','join') == 'false':
                can_join = False 
            if can_join:
                self.add_op('begin')
                if my_is_from:
                    self.add_filter("search_type", search.get_search_type() )

                    if relationship == "search_code":
                        search.add_column("code", distinct=True)
                        self.add_search_filter("search_code", search, op=op)
                    else:
                        search.add_column("id", distinct=True)
                        self.add_search_filter("search_id", search, op=op)

                else:
                    search.add_filter("search_type", self.get_search_type())

                    if relationship == 'search_code':
                        search.add_column("search_code", distinct=True)
                        self.add_search_filter("code", search, op=op)
                    else:
                        search.add_column("search_id", distinct=True)
                        self.add_search_filter("id", search, op=op)


                self.add_op('and')
                return True


            # only apply delay_null in search_type condition 
            if my_is_from:
                # only support to_col == 'id'
                # fast way of getting search_ids
                if relationship == 'search_code':
                    s_values = search.get_sobject_codes()
                else:
                    s_values = search.get_sobject_ids()

                if delay_null and not s_values:
                    return False
                
                self.add_op('begin')
                self.add_filter("search_type", search.get_search_type() )

                if relationship == 'search_code':
                    self.add_filters("search_code", s_values )
                else:
                    self.add_filters("search_id", s_values )

                self.add_op('and')

            else:
                if relationship == 'search_code':
                    search.add_column("search_code", distinct=True)
                else:
                    search.add_column("search_id", distinct=True)

                search.add_filter("search_type", full_search_type)

                # skip retired
                sql = DbContainer.get(self.db_resource)
                columns = search.get_columns()
                search.skip_retired(columns)

                statement = search.get_statement()
                # avoid building sobjects
                sthpw_sql = DbContainer.get("sthpw")
                results = sthpw_sql.do_query(statement)

                if delay_null and not results:
                    return False


                if not results:
                    if relationship == 'search_code':
                        self.add_filter("code", "NULL", quoted=False)
                    else:
                        self.add_filter("id", "NULL", quoted=False)
                else:
                    # filter out invalid search_id = NULL
                    values = [x[0] for x in results if x[0]]
                    if delay_null and not values:
                        return False
                    if relationship == 'search_code':
                        self.add_filters("code", values, op=op)
                    else:
                        self.add_filters("id", values, op=op)

        elif relationship in ['instance']:

            # add_relationship_filter(self, search, op='in', delay_null=False, use_multidb=None)

            from_col = attrs['from_col']
            to_col = attrs['to_col']

            instance_type = attrs.get("instance_type")
            assert instance_type

            self.add_join(instance_type, search_type)
            self.add_join(related_type, instance_type)

            search_type_obj = SearchType.get(search_type)
            related_type_obj = SearchType.get(related_type)

            table = search_type_obj.get_table()
            related_table = related_type_obj.get_table()
            self.add_column("*", table=table)
            self.add_column("code", table=related_table, as_column="_related_code")

            s_values = search.get_sobject_codes()
            self.add_filters(to_col, s_values, table=related_table)

        else:
            raise SearchException("Relationship [%s] not supported" % relationship)

        return True


    def add_user_filter(self, user=None, column=None, table=""):
        '''convenience function to add a filter for the given sobject'''
        if user == None:
            user = Environment.get_user_name()
        if not column:
            column = "login"

        if not table:
            table = self.select.get_table()

        self.add_filter(column, user, table=table)



    def add_project_filter(self, project_code=None, show_unset=True):
        from pyasm.biz import Project
        filter = Project.get_project_filter(project_code, show_unset=show_unset)
        self.add_where(filter)


    def add_date_range_filter(self, name, start_date, end_date, table=''):
        '''convenience function to add a filter between two dates.  This
        method will strip out the time and ensure that the range is
            start_date >= date <= end_date + 1 day
        '''

        if start_date and isinstance(start_date, basestring):
            from dateutil import parser
            start_date = parser.parse(start_date)
        if end_date and isinstance(end_date, basestring):
            from dateutil import parser
            end_date = parser.parse(end_date)

        if not start_date and not end_date:
            self.set_null_filter()

        if start_date and end_date:
            self.add_op('begin')


        if start_date:
            start_date = datetime.datetime(year=start_date.year,month=start_date.month,day=start_date.day)
            self.add_filter(name, start_date, op=">=", table=table)

        if end_date:
            end_date = datetime.datetime(year=end_date.year,month=end_date.month,day=end_date.day)
            end_date = end_date + datetime.timedelta(days=1)

            self.add_filter(name, end_date, op="<", table=table)

        if start_date and end_date:
            self.add_op('and')



    def add_dates_overlap_filter(self, start_col, end_col, start_date, end_date, table='', op='in'):
        '''convenience function to add a filter of two date columns that
        overlap two dates.

        The conditions are:
          start_col < start_date and end_col > start_date
          start_col < end_date and end_col > end_date
        '''

        if isinstance(start_date, basestring):
            from dateutil import parser
            start_date = parser.parse(start_date)
        if isinstance(end_date, basestring):
            from dateutil import parser
            end_date = parser.parse(end_date)

        if not start_date and not end_date:
            self.set_null_filter()

        start_date = datetime.datetime(year=start_date.year,month=start_date.month,day=start_date.day)
        end_date = datetime.datetime(year=end_date.year,month=end_date.month,day=end_date.day)
        # NOTE: not sure if we want to add this extra day here?
        end_date = end_date + datetime.timedelta(days=1)
        table = self.select.get_table()

        select = Select()
        select.set_database(self.db_resource)
        self.select.set_id_col(self.get_id_col())
        select.add_table(table)
        select.add_column("id")

        select.add_op('begin')

        select.add_op('begin')
        select.add_filter(start_col, start_date, op="<=", table=table)
        select.add_filter(end_col, start_date, op=">=", table=table)
        select.add_op('and')

        select.add_op('begin')
        select.add_filter(end_col, end_date, op=">=", table=table)
        select.add_filter(start_col, end_date, op="<=", table=table)
        select.add_op('and')

        # NOTE this "or" should not be required now 
        # NOTE: At the moment, the nested "begin" operators on more
        # than two operations is not supported, so need to add
        # an explicit "or" operator here
        #select.add_op('or')

        select.add_op('begin')
        select.add_filter(start_col, start_date, op=">=", table=table)
        select.add_filter(end_col, end_date, op="<=", table=table)
        select.add_op('and')

        select.add_op('or')

        statement = select.get_statement()

        self.add_where('''"%s"."id" %s (%s)'''% (table, op, statement) )




    def add_id_filter(self, value):
        self.add_filter( self.get_id_col(), value , quoted=False)

        # when adding an explicit id filter, you probably want it even
        # if it is retired
        self.set_show_retired_flag(True)


    def add_code_filter(self, value):
        self.add_filter( "code", value )

        # when adding an explicit id filter, you probably want it even
        # if it is retired
        self.set_show_retired_flag(True)



    def add_group_by(self, column):
        self.select.add_group_by(column)

    def add_having(self, filter):
        self.select.add_having(filter)



    def add_group_aggregate_filter(self, group_cols, column='id', aggregate='max'):
        '''This does a co-related subselect which finds the result of an
        aggregate function over a list of grouped columns
       
        Searching for the max version for each context of a snapshot.
        This is called by:

        search.add_aggregate_group_filter(['search_type','search_id','context'], "version")

        This producess the following sql:

        select * from snapshot where version = (select max(version) from snapshot as f where f.search_type = snapshot.search_type and f.search_id = snapshot.search_id and f.context = snapshot.context) order by search_type, search_id;

        Reference:
        http://www.xaprb.com/blog/2006/12/07/how-to-select-the-firstleastmax-row-per-group-in-sql/
        
        '''
        self.select.add_group_aggregate_filter(group_cols, column, aggregate)


    def add_distinct_filter(self, group_cols):
        self.select.add_group_aggregate_filter(group_cols)


    def add_keyword_filter(self, column, keywords, table=None, column_type=None, op=None, case_sensitive=False):

        if not table:
            table = self.search_type_obj.get_table()

        if not column_type:
            column_types = SearchType.get_column_types(self.full_search_type)
            column_type =  column_types.get(column)
       
        if isinstance(keywords, basestring):
            raise SearchException('Expects a list for add_keyword_filter')

        
        # defaults to and
        if not op:
            op = 'and'
        self.select.add_op('begin')
        for keyword in keywords:
            if not keyword:
                continue

            if not case_sensitive:
                keyword = keyword.lower()
            # avoid syntax error
            keyword = keyword.replace("'", "''")
            
            if column_type in ['integer','serial']:
                # cast integer as string
                expr = """CAST("%s"."%s" AS varchar(10)) like '%s%%'""" % (table, column, keyword)
            else:
                # don't add lower() here to allow index to function
                expr = '''"%s"."%s" like '%%%s%%' ''' % (table, column, keyword)
            self.select.add_where(expr)
        self.select.add_op(op)


    def add_startswith_keyword_filter(self, column, keywords, case_sensitive=False):

        if column.find(".") != -1:
            parts = column.split(".")
            column = parts[-1]
            search_types = parts[:-1]
            # A simpler implementation without trying to find the related results only

            # there is no need to do join here as it creates many duplicates and obstructs the intention 
            # to get the last 10 best matched result in Look Ahead search. we could uncomment this in the future
            # if we have a cross database way of eliminating duplicates.
            '''   
            prev_stype = self.get_base_search_type()
            search_types = reversed(search_types)
            
            for next_stype in search_types:
                self.add_join(next_stype, prev_stype)
                prev_stype = next_stype

            # postgresql only way
            self.set_distinct_col('"%s".id'%table)
            '''
            table = self.search_type_obj.get_table()
            column_types = SearchType.get_column_types(self.full_search_type)
        else: 
            table = self.search_type_obj.get_table()
            column_types = SearchType.get_column_types(self.full_search_type)



        for keyword in keywords:
            if not keyword:
                continue


            # avoid syntax error
            keyword = keyword.replace("'", "''")

            col_type =  column_types.get(column)
           
            if col_type in ['integer','serial']:
                # cast as a string first for integer supported by postgres, SQLServer, MySQL
                expr1 = """CAST("%s"."%s" AS varchar(10)) like '%% %s%%'""" % (table, column, keyword)
                expr2 = """CAST("%s"."%s" AS varchar(10)) like '%s%%'""" % (table, column, keyword)
            else:
                if case_sensitive:
                    
                    expr1 = '''"%s"."%s" like '%% %s%%' ''' % (table, column, keyword)
                    expr2 = '''"%s"."%s" like '%s%%' ''' % (table, column, keyword)
                else:
                    keyword = keyword.lower()
                    expr1 = '''lower("%s"."%s") like lower('%% %s%%')''' % (table, column, keyword)
                    # NOTE: lower() on the column disables the use of index, resulting in much slower performance
                    expr2 = '''lower("%s"."%s") like lower('%s%%')''' % (table, column, keyword)

            self.select.add_op("begin")

            self.select.add_where(expr1)
            self.select.add_where(expr2)
            self.select.add_op("or")




    def add_text_search_filter(self, column, keywords, table=None, op='&'):

        self.select.add_text_search_filter(column, keywords, table=table, op=op)



    def add_text_search_filters(self, columns, keywords, table=None):
        '''function that searches keywords across multiple columns'''

        single_col = len(columns) == 1
        partial_op = 'and'

        if not keywords:
            return

        # keywords is kept as a string to maintain OR full-text search
        if isinstance(keywords,basestring):
            keywords = keywords.replace(",", " ")
            keywords = re.sub(' +', ' ', keywords)
            keywords = keywords.strip()

            # keywords_list is used for add_keyword_filter()
            keywords_list = keywords.split(" ")
        else:
            keywords_list = keywords

        if not keywords_list:
            return

        single_keyword = len(keywords_list) == 1

        if isinstance(columns,basestring):
            columns = columns.split(",")


        if single_col:
            if single_keyword:
                multi_col_op = 'or' # this doesn't really matter
                op = '|'            # this doesn't really matter
            else: # multi_keyword, single column
                multi_col_op = 'or' # this doesn't really matter
                op = '&'

        else:
            if single_keyword:
                multi_col_op = 'or'
                op = '|'            # this doesn't really matter
            else:
                multi_col_op = 'or'
                op = '&'


        search_type = self.get_search_type()
        search_type_obj = SearchType.get(search_type)

        if not table:
            table = search_type_obj.get_table()

        self.add_op("begin")

        for column in columns:
            self.add_text_search_filter(column, keywords, table=table, op=op)

        self.add_op(multi_col_op)




    def add_join(self, to_search_type, from_search_type=None, path=None, join=None):
        to_search_type_obj = SearchType.get(to_search_type)
        to_search_type = to_search_type_obj.get_base_key()

        if not from_search_type:
            from_search_type = self.get_base_search_type()
        else:
            from_search_type_obj = SearchType.get(from_search_type)
            from_search_type = from_search_type_obj.get_base_key()

        if to_search_type == from_search_type:
            return


        namespace, from_table = from_search_type.split("/")
        namespace, to_table = to_search_type.split("/")


        from pyasm.biz import Schema
        schema = Schema.get(project_code=self.project_code)
        attrs = schema.get_relationship_attrs(from_search_type, to_search_type, path=path)
        if not attrs:
            return



        relationship = attrs.get("relationship")
        if relationship == 'search_type':
            relationship = schema.resolve_search_type_relationship(attrs, from_search_type, to_search_type)


        if relationship in ["search_code", "search_id"]:

            from_db_resource = SearchType.get_db_resource_by_search_type(from_search_type)
            from_database = from_db_resource.get_database()
            to_db_resource = SearchType.get_db_resource_by_search_type(to_search_type)
            to_database = to_db_resource.get_database()

            if from_search_type == attrs.get("from"):
                if relationship == "search_code":
                    from_col = "search_code"
                    to_col = "code"
                else:
                    from_col = "search_id"
                    to_col = "id"
                self.add_filter("search_type", self.get_search_type(),table=from_table)
            else:
                if relationship == "search_code":
                    from_col = "code"
                    to_col = "search_code"
                else:
                    from_col = "id"
                    to_col = "search_id"
                self.add_filter("search_type", self.get_search_type(),table=to_table)

        else:
            from_database = None
            to_database = None
            if from_search_type == attrs.get("from"):
                from_col = attrs.get("from_col")
                to_col = attrs.get("to_col")
            else:
                from_col = attrs.get("to_col")
                to_col = attrs.get("from_col")


        if not join:
            join = "LEFT OUTER"

        if from_table:
            self.select.add_join(from_table, to_table, from_col, to_col, join=join, database=from_database, database2=to_database)
        else:
            self.select.add_join(to_table, join=join)



    def add_order_by(self, order_str, direction='', join="LEFT OUTER"):

        # check if it is valid
        if ',' in order_str:
            order_bys = order_str.split(",")
            for order_by in order_bys:
                # do not call return in the loop so that all items are looped through
               
                self.add_order_by(order_by, direction)
            return

        order_str = order_str.strip()
        # extract the column: in case of: "code desc"
        strs = order_str.split(' ', 1)
        column = strs[0]

        if len(strs) == 2:
            direction = strs[1]
        # prevent duplicate order bys ... first one wins
        if column in self.order_bys:
            return

        parts = column.split(".")
        parts = [x for x in parts if x]
        
        if "connect" in parts:
            return

        if len(parts) >= 2:
            # Add joins to order by another search_type

            prev_search_type = self.get_base_search_type()
            for search_type in parts[0:-1]:

                if search_type.find("/") == -1:
                    prev_search_type_obj = SearchType.get(prev_search_type)
                    namespace = prev_search_type_obj.get_value("namespace")
                    search_type = "%s/%s" % (namespace, search_type)

                if search_type.find(":") != -1:
                    parts = search_type.split(":")
                    path = parts[0]
                    search_type = parts[1]
                else:
                    path = None

                # skip if the main search_type is joined to itself
                if search_type == prev_search_type:
                    continue


                can_join = DatabaseImpl.can_search_types_join( \
                        search_type, prev_search_type)
                if can_join:
                    self.add_join(search_type, prev_search_type, join=join)
                else:
                    return False


                prev_search_type = search_type


            self.order_bys.append(column)

            search_type_obj = SearchType.get(search_type)
            table = search_type_obj.get_table()
            column = parts[-1]
            self.select.add_order_by(column, direction=direction, table=table)

            return True
        else:

            table = self.search_type_obj.get_table()

            impl = self.get_database_impl()
            if impl.is_column_sortable(self.get_db_resource(), table, column):
                self.select.add_order_by(order_str, direction)
                self.order_bys.append(column)
                return True
            else:
                return False


    def add_enum_order_by(self, column, values, table=None):
        self.select.add_enum_order_by(column, values, table)

    def get_order_bys(self):
        return self.select.order_bys

    def add_limit(self, limit):
        '''deprecated: use set_limit()'''
        self.select.set_limit(limit)

    def set_limit(self, limit):
        self.select.set_limit(limit)

    def set_offset(self, offset):
        self.select.set_offset(offset)


    # DEPRECATED: use set_show_retired
    def set_show_retired_flag(self, flag):
        '''retired assets must be explicitly asked for'''
        self.show_retired_flag = flag

    def set_show_retired(self, flag):
        '''retired assets must be explicitly asked for'''
        self.show_retired_flag = flag



    def do_search(self, redo=False, statement=None):

        if self.null_filter:
            return []

        # if we are doing a remote search, then get the sobjects from the
        # remote search
        if isinstance(self.select, RemoteSearch):
            return self.select.get_sobjects()

        if not redo and self.is_search_done:
            return self.sobjects

        search_type = self.get_base_search_type()
        security = Environment.get_security()


        # filter
        extra_filter = self.search_type_obj.get_value("extra_filter", no_exception=True)
        if extra_filter:
            self.add_where(extra_filter)

     
        # DEPRECATED: not sure if this was ever used??
        #
        # allow the sobject to alter search
        # A little convoluted, but it works
        class_path = self.search_type_obj.get_class()
        (module_name, class_name) = \
                Common.breakup_class_path(class_path)
        try:
            try:
                exec("%s.alter_search(self)" % class_name )
            except NameError:
                exec("from %s import %s" % (module_name,class_name), gl, lc )
                exec("%s.alter_search(self)" % class_name )
        except ImportError:
            raise SearchException("Class_path [%s] does not exist" % class_path)

        # allow security to alter the search if it hasn't been done in SearchLimitWdg
        if not self.security_filter:
            security.alter_search(self)


        # build an sql object
        database = self.get_database() 
        # SQL Server: Skip the temp column put in by handle_pagination()
        
        db_resource = self.db_resource
        sql = DbContainer.get(db_resource)

        # get the columns
        table = self.get_table()
        columns = sql.get_columns(table)
        #columns = self.remove_temp_column(columns, sql) 
        select_columns = self.select.get_columns()
        if select_columns:
            if select_columns[0] == '*':
                del(select_columns[0])
                columns.extend(select_columns)
            else:
                columns = select_columns


        '''
        self.config = SObjectConfig.get_by_search_type(self.search_type_obj, database)
        if self.config != None:
            order_bys = self.config.get_order_by()
            order_bys = order_bys.split(',')
            for order_by in order_bys:
                if order_by:
                    self.add_order_by(order_by)
        '''
        # Hard coded replacement.  This is done for performance reasons
        if self.order_by:

            if search_type in ['sthpw/snapshot', 'sthpw/note','sthpw/sobject_log', 'sthpw/transaction_log', 'sthpw/status_log']:
                self.add_order_by("timestamp", direction="desc")
            elif search_type == 'sthpw/task':
                self.add_order_by("search_type")
                if self.column_exists("search_code"):
                    self.add_order_by("search_code")
            elif search_type == 'sthpw/login':
                self.add_order_by("login")
            elif search_type == 'sthpw/login_group':
                self.add_order_by("login_group")
            elif search_type == 'config/process':
                self.add_order_by("pipeline_code,sort_order")
            elif search_type == 'sthpw/message_log':
                self.add_order_by("timestamp", direction="desc")
            elif "code" in columns:
                self.add_order_by("code")



        # skip retired sobject
        self.skip_retired(columns)

        # get columns that are datetime to be converted to strings in
        # SObject constructor
        column_info = self.get_column_info()

        datetime_cols = []
        boolean_cols = []
        skipped_cols = []
        for key,value in column_info.items():
            data_type = value.get('data_type')
            if data_type in ['timestamp', 'time', 'date', 'datetime2']:
                datetime_cols.append(key)
            elif data_type in ['boolean']:
                boolean_cols.append(key)
            elif data_type in ['sqlserver_timestamp']:
                skipped_cols.append(key)

        vendor = db_resource.get_vendor()
        if vendor == "MongoDb":
            #statement = self.select.get_statement()
            #print('statement: ', statement)
            results = sql.do_query(self.select)
            # TODO:
            # Not really used because results is already a dictionary
            # and the column data is dynamic
            columns = ['_id']
            result_is_dict = True



        elif vendor in ["Salesforce"] or search_type.startswith("salesforce/"):

            impl = db_resource.get_database_impl()
            self.sobjects = impl.execute_query(sql, self.select)

            # remember that the search has been done
            self.is_search_done = True

            return self.sobjects


        else:
            # get the select statement and do the query
            if not statement:
                statement = self.select.get_statement()

            from pyasm.security import Site
            results = sql.do_query(statement)

            # this gets the actual order of columns in this SQL
            columns = sql.get_columns_from_description()

            result_is_dict = False


        Container.increment('Search:sql_query') 

        # create a list of objects
        self.sobjects = []

        # precalculate some information
        from pyasm.biz import Project
        #full_search_type = Project.get_full_search_type(search_type, project_code=self.project_code)
        full_search_type = self.get_full_search_type()
        fast_data = {
            'full_search_type': full_search_type,
            'search_type_obj': self.search_type_obj,
            'database': Project.extract_database(full_search_type),
            'db_resource': db_resource,
            'datetime_cols': datetime_cols,
            'boolean_cols': boolean_cols,
            'skipped_cols': skipped_cols,
        }

        # Count number of sobjects
        num_sobjects = Container.get("NUM_SOBJECTS")
        if not num_sobjects:
            num_sobjects = 0
        num_sobjects = num_sobjects + len(results)
        if len(results) > 10000:
            print("WARNING query: (%s) sobjects found: %s" % (len(results), statement.encode('utf-8','ignore')))
        Container.put("NUM_SOBJECTS", num_sobjects)


        # assemble the data dictionaries to be distributed to the sobjects
        data_list = []
        for result in results:
            if result_is_dict:
                data = result
            else:
                data = dict(zip(columns, result))
            if skipped_cols:
                for skipped_col in skipped_cols:
                    # forcing this data empty because
                    # otherwise the sobject does not have
                    # a column it believes it should have
                    #del data[skipped_col]
                    data[skipped_col] = ""
            data_list.append(data)

        fast_data['data'] = data_list

        # do this inline for performance
        for i, result in enumerate(results):
            fast_data['count'] = i

            sobject = SearchType.fast_create_from_class_path(class_name,
                self.search_type_obj, columns, result, module_name=module_name,
                fast_data=fast_data)
            # add this sobject to the list of sobjects for the search
            self.sobjects.append(sobject)


        # remember that the search has been done
        self.is_search_done = True

        return self.sobjects




    def eval(cls, expression, sobjects=None, mode=None, single=False, list=False, vars={}, dictionary=False, env_sobjects={}, show_retired=False, state={}, extra_filters={}, search=None):
        from pyasm.biz import ExpressionParser
        parser = ExpressionParser()
        return parser.eval(expression, sobjects=sobjects, single=single, list=list, dictionary=dictionary, vars=vars, env_sobjects=env_sobjects, show_retired=show_retired, state=state, extra_filters=extra_filters, search=search)
    eval = classmethod(eval)



    def get_eval_cache(cls, expression, sobjects=None, mode=None, single=False, list=False, vars={}, dictionary=False, env_sobjects={}, show_retired=False, state={}, extra_filters={}, search=None):
        from pyasm.biz import ExpressionParser
        parser = ExpressionParser()
        parser.eval(expression, sobjects=sobjects, single=single, list=list, dictionary=dictionary, vars=vars, env_sobjects=env_sobjects, show_retired=show_retired, state=state, extra_filters=extra_filters, search=search)
        return parser.get_cache_sobjects()
    get_eval_cache = classmethod(get_eval_cache)


    def skip_retired(self, columns):
        retired_col = self.search_type_obj.get_retire_col()
        table = self.search_type_obj.get_table()

        # remove retired filter
        filter_name = "(\"%s\".\"%s\" != 'retired' or \"%s\".\"%s\" is NULL)" %(table, retired_col, table, retired_col)
        if not self.show_retired_flag and (retired_col in columns):
            self.add_where(filter_name) 
        else:
            self.remove_where(filter_name)


    # DEPRECATED: this is now in database_impl
    """
    def remove_temp_column(self, columns, sql):
        # SQL Server temp columns are put in by ROW_NUMBER()
        # in database_impl.handle_pagination()
        impl = sql.get_database_impl()
        temp_column_name = impl.get_temp_column_name()
        if temp_column_name and temp_column_name in columns:
            columns.remove(temp_column_name)

        return columns
    """

    def get_sobject_ids(self):
        '''fast way of getting sobject ids without creating them during search'''
        if 'id' not in self.select.columns:
            self.add_column('id')
        
        sql = DbContainer.get(self.db_resource)
        columns = self.get_columns()
        self.skip_retired(columns)

        statement = self.get_statement()
        results = sql.do_query(statement)
        ids = [x[0] for x in results]
        return ids


    def get_sobject_codes(self):
        '''fast way of getting sobject codeswithout creating them during search'''
        if 'code' not in self.select.columns:
            self.add_column('code')
        
        sql = DbContainer.get(self.db_resource)
        columns = self.get_columns()
        self.skip_retired(columns)

        statement = self.get_statement()
        results = sql.do_query(statement)
        codes = [x[0] for x in results]
        return codes




    def get_sobjects(self, redo=False, statement=None):
        '''convenience function for interface consistency'''
        return self.do_search(redo, statement)


    def get_sobject(self, redo=False):
        '''convenience function to get a single object'''
        self.set_limit(1)
        sobjects = self.do_search(redo)
        if sobjects:
            return sobjects[0]
        else:
            return None



    def get_count(self, no_exception=False):
        '''Get the number of sobjects that this search will retrieve'''

        if self.null_filter:
            return 0

        database = self.database

        db_resource = self.db_resource
        sql = DbContainer.get(db_resource)
        table = self.search_type_obj.get_table()

        #columns = Search.get_cached_columns(database, self.search_type_obj)
        columns = sql.get_columns(table)

        self.skip_retired(columns)
        try:
            security = Environment.get_security()
            if not self.security_filter:
                security.alter_search(self)

            vendor = db_resource.get_vendor()
            if vendor == "MongoDb":
                count = self.select.execute_count()

            elif vendor == "Salesforce":
                count = 100
            else:
                statement = self.select.get_count()
                count = sql.get_value(statement)

        except SqlException:
            if no_exception:
                return -1
            else:
                raise

        if not count:
            return 0
        return int(count)

   
    
    # static helper functions for Search

    def get_by_value(search_type, column, value):
        '''convenience method to get a single sobject from a column/value
        pair'''
        search = Search(search_type)
        search.add_filter(column, value)
        sobject = search.get_sobject()
        return sobject
    get_by_value = staticmethod(get_by_value)

    
    def get_by_id(search_type, search_id, show_retired=True):
        # allow search_id = 0
        if not search_type or search_id in [None, '']:
            return None
        search = Search(search_type)
        search.set_show_retired(show_retired)
        if isinstance(search_id, list):
            # assuming idential search_type
            search.add_filters(search.get_id_col(), search_id)
            return search.get_sobjects()
        else:
            # use caching
            search.add_id_filter(search_id)
            # NOTE: search_type replaced
            from pyasm.biz import Project
            search.full_search_type = Project.get_full_search_type(search_type)
            key = SearchKey.build_search_key(search_type, search_id, column='id', project_code=search.project_code)
            sobj = SObject.get_by_search(search, key)
            return sobj
    get_by_id = staticmethod(get_by_id)


    def get_by_code(search_type, code, show_retired=True):
        if not search_type or not code:
            return None

        search = Search(search_type)
        search.set_show_retired(show_retired)
        if isinstance(code, list):
            # assuming idential search_type
            search.add_filters('code', code)
            return search.get_sobjects()
        else:
            # use caching
            search.add_filter("code", code)

            key = SearchKey.build_search_key(search_type, code, column='code', project_code=search.project_code)
            sobj = SObject.get_by_search(search, key)
            return sobj
    get_by_code = staticmethod(get_by_code)


    def get_by_search_key(search_key):
        return SearchKey.get_by_search_key(search_key)
    get_by_search_key = staticmethod(get_by_search_key)

   
    def get_by_search_keys(search_keys, keep_order=False):
        return SearchKey.get_by_search_keys(search_keys, keep_order=keep_order)
    get_by_search_keys = staticmethod(get_by_search_keys)

    def get_compound_filter(text_value, columns):
        '''a more sophisticated search filter'''
        if text_value == "":
            return None

        # replace all * to % for wildcard
        #text_value = text_value.replace("*", "%")
        def _get_sql_str(text_values, op='EQI', condition='or'):
            '''get a partial sql string'''
            filters = []
            if not text_values:
                return ''
            condition = ' %s ' % condition
            for tmp_value in text_values:
                if op in ['EQ','EQI']:
                    expr = [Search.get_regex_filter(x, tmp_value, op=op) for x in columns]
                else:
                    expr = ['("%s" or "%s" is NULL)' %(Search.get_regex_filter(x, tmp_value, op=op), x) for x in columns]
                
                filter = " %s " %condition.join(expr)
                
                filters.append(filter)

            final = " and ".join( [ "(%s)" % x for x in filters] )
            return final

        #TODO: make OR and AND work after NOT appears, now it assumes AND 
        pos_words, neg_words = '',''

        text_value = text_value.replace(' OR ', '|')
        text_value = text_value.replace(' AND ', ' ')

        # account for lazy typing 
        if text_value.endswith(' NOT'):
            text_value = '%s ' % text_value
        # look for NOT
        if ' NOT ' in text_value:
            pos_words, neg_words = text_value.split(' NOT ', 1)
        elif text_value.startswith('NOT '):
            pos_words = ''
            neg_words = text_value.replace('NOT ', '')
        else:
            pos_words = text_value
        text_values = []
        if pos_words:
            text_values = pos_words.split(" ")
            text_values = [x.lower() for x in text_values if x]

        neg_values = neg_words.split(" ")
        neg_values = [x.lower() for x in neg_values if x]
       
        pos_final = _get_sql_str(text_values)
        final = ''
        if pos_final:
            final = pos_final
        if neg_values:
            neg_final = _get_sql_str(neg_values, op='NEQI', condition='and')
            if final:
                final = '%s and %s' %(final, neg_final)
            else:
                final = neg_final
        return final
    get_compound_filter = staticmethod(get_compound_filter)




    def get_related_by_sobjects(cls, sobjects, related_type, filters=[], path=None, show_retired=False):

        if not sobjects:
            return {}

        tmp_data = {}

        # assume all the sobjects are of the same type
        sobject = sobjects[0]
        if not sobject:
             return {}

        search_type = sobject.get_base_search_type()
        project_code = sobject.get_project_code()


        search = Search(related_type)
        if show_retired:
            search.set_show_retired(True)

        if filters:
            search.add_op_filters(filters)
        search.add_relationship_filters(sobjects, path=path)
        related_sobjects = search.get_sobjects()

        # to maintain returned data consistency, it should let it 
        # return search_key: related_sobjects even if related_sobjects is []
        # if not related_sobjects:
        #    return tmp_data

        # get the base related type to avoid getting a None relationship
        related_type = SearchKey.extract_base_search_type(related_type)
        
        from pyasm.biz import Schema
        schema = Schema.get(project_code=project_code)
        attrs = schema.get_relationship_attrs(related_type, search_type, path=path )

        # if not attrs and the search_types are the same, return nothing
        if related_type == search_type and not attrs:
            print("WARNING: source type is the same as related type [%s]" % search_type)
            return {}

        relationship = attrs.get("relationship")
        is_from = related_type == attrs.get("from")

        prefix = attrs.get("prefix")
        if prefix:
            prefix = "%s_" % prefix
        else:
            prefix = ""

        # go through the related sobjects and map them
        for related_sobject in related_sobjects:
            if relationship == 'search_type':
                relationship = schema.resolve_search_type_relationship(attrs, search_type, related_type)

            # find the key that relates back to the orignal sobject
            if relationship in ['code','id']:
                if is_from:
                    key = related_sobject.get_value(attrs.get("from_col"))
                else:
                    key = related_sobject.get_value(attrs.get("to_col"))

            elif relationship == "instance":
                if is_from:
                    key = related_sobject.get_value("_related_code")
                else:
                    key = related_sobject.get_value("_related_code")


            elif relationship in ['search_code']:
                if is_from:
                    search_type = related_sobject.get_value("%ssearch_type" % prefix)
                    search_code = related_sobject.get_value("%ssearch_code" % prefix)
                    key = "%s&code=%s" % (search_type, search_code)
                else:
                    search_type = related_sobject.get_search_type()
                    search_code = related_sobject.get_value("code")
                    key = "%s&code=%s" % (search_type, search_code)
 
            elif relationship in ['search_id']:
                if is_from:
                    search_type = related_sobject.get_value("%ssearch_type" % prefix)
                    search_id = related_sobject.get_value("%ssearch_id" % prefix)
                    key = "%s&id=%s" % (search_type, search_id)
                else:
                    search_type = related_sobject.get_search_type()
                    search_id = related_sobject.get_value("id")
                    key = "%s&id=%s" % (search_type, search_id)
 
            else:
                raise SearchException("Relationship [%s] not supported" % relationship)



            # map to the corresponding key
            items = tmp_data.get(key)
            if items == None:
                items = []
                tmp_data[key] = items
            items.append(related_sobject)


        # go through all of the original sobjects and map
        data = {}
        for sobject in sobjects:
            if relationship in ['code','id','instance']:
                if is_from:
                    key = sobject.get_value(attrs.get("to_col"))
                else:
                    key = sobject.get_value(attrs.get("from_col"))
            elif relationship in ['search_type','search_code','search_id']:
                if relationship == "search_type":
                    relationship = schema.resolve_search_type_relationship(attrs, search_type, related_type)

                if is_from:
                    if relationship == 'search_code':
                        key = "%s&code=%s" % (sobject.get_search_type(), sobject.get_value("code"))
                    else:
                        key = "%s&id=%s" % (sobject.get_search_type(), sobject.get_id())

                else:
                    if relationship == 'search_code':
                        key = "%s&code=%s" % (sobject.get_value("%ssearch_type" % prefix), sobject.get_value("%ssearch_code" % prefix))
                    else:
                        key = "%s&id=%s" % (sobject.get_value("%ssearch_type" % prefix), sobject.get_value("%ssearch_id" % prefix))

            else:
                raise TacticException("Relationship [%s] not supported" % relationship)

            search_key = sobject.get_search_key()

            items = tmp_data.get(key)
            if items == None:
                data[search_key] = []
            else:
                # remap so that search_key is used as the key
                data[search_key] = items

        return data

    get_related_by_sobjects = classmethod(get_related_by_sobjects)




    def get_search_by_db_resource(cls, db_resource, table):
        '''Get a search object from purely a database resource, without the
        need to register a project'''
        # make up a fake project name
        database = db_resource.get_database()
        project_code = "db_resource/%s" % database
        search_type = "table/%s?project=%s" % (table, project_code)
        search = Search(search_type)
        return search
    get_search_by_db_resource = classmethod(get_search_by_db_resource)



__all__.append("RemoteSearch")
class RemoteSearch(Select):
    '''Class to proxy out search requests to a remote Tactic server.  This
    class is derived from Select because it is meant to be used as a
    cross between Select and Search.  It is never meant to be instantiated
    directly, but instead by Search itself.  This ensures that all
    Search operations will work regardless if the functionality is supported
    or not'''
    def __init__(self, search_type):

        super(RemoteSearch,self).__init__()

        from pyasm.biz import Project
        self.project_code = Project.extract_project_code(search_type)
        #self.database = Project.extract_database(search_type)
        #self.host = Project.extract_host(search_type)
        #self.base_search_type = Project.extract_base_search_type(search_type)
        #self.db_resource = DbResource(database=self.database, host=self.host)

        self.filters = []

        project = Project.get_by_code(self.project_code)
        self.resource = project.get_resource()
        self.server = self.resource.get_server()
        self.remote_project = self.resource.get_project()
        if self.remote_project:
            self.search_type = search_type.replace("project=%s" % project.get_code(), "project=%s" % self.remote_project)




    def add_filter(self, name, value, op='=', quoted=True):
        if not op:
            op = '='

        self.filters.append( [name, op, value] )

    def get_sobjects(self):

        results = []
        trys = 3
        import time
        start = time.time()

        for i in range(1, trys):
            try:
                results = self.server.query(self.search_type, filters=self.filters,
                    limit=self.limit)

            except Exception as e:
                if time.time() - start > 10:
                    print("WARNING: try [%s] took longer than 10s: " % i, str(e))
                    raise

                if i == trys:
                    raise
                else:
                    print("WARNING: try [%s]: " % i, str(e))
                    continue
            else:
                break

        sobjects = []
        for result in results:
            columns = result.keys()
            values = result.values()

            # all objects come back as SObject?
            if self.search_type.startswith("sthpw/search_object"):
                sobject = SearchType(self.search_type, columns, values)
            else:
                sobject = SObject(self.search_type, columns, values, remote=True)

            sobjects.append(sobject)
        return sobjects

    def get_sobject(self):
        self.limit = 1
        self.set_limit(self.limit)
        self.sobjects = self.get_sobjects()
        if not self.sobjects:
            return None
        else:
            return self.sobjects[0]





class SObject(object):
    '''Base class of the object/relation mapper.  All results from the Search class come as derived class of SObject'''
    
    SEARCH_TYPE = "pyasm.search.SObject"

    COUNT = 0


    def __init__(self, search_type, columns=None, result=None, remote=False, fast_data=None):

        # cache the security object
        #self.security = Environment.get_security()
        self._security = None

        from pyasm.biz import Project

        if fast_data:
            self.search_type_obj = fast_data['search_type_obj']
            self.full_search_type = fast_data["full_search_type"]
            self.database = fast_data["database"]
            self.db_resource = fast_data["db_resource"]
        else:
            if isinstance(search_type, SearchType):
                self.search_type_obj = search_type
                self.full_search_type = Project.get_full_search_type(search_type)
            elif remote == True:
                self.search_type_obj = SearchType.create("sthpw/search_object")
                self.search_type_obj.set_value("search_type", search_type)
                self.full_search_type = search_type

            elif search_type == "sthpw/search_object":
                # special case for when this SObject is SearchType
                self.search_type_obj = self
                self.full_search_type = "sthpw/search_object"

            elif isinstance(search_type, basestring):
                self.search_type_obj = SearchType.get(search_type)
                self.full_search_type = Project.get_full_search_type(search_type)
            else:
                self.search_type_obj = search_type
                self.full_search_type = Project.get_full_search_type(search_type)

            self.database = Project.extract_database(self.full_search_type)
            self.db_resource = Project.get_db_resource_by_search_type(self.full_search_type)


        self._update_data = None
        self._quoted_flag = None
        self.has_updates = False
        self._prev_data = None
        self._prev_update_data = None
        self.update_description = None
        self._skip_invalid_column = False
        #self.database_impl = None

        # id override
        self.new_id = -1

        if not columns:
            self.data = {}
            self.data[self.get_id_col()] = -1
        else:
            if fast_data:
                self.data = fast_data['data'][fast_data['count']]

                # MongoDb
                #if '_id' in self.data and 'code' not in self.data:
                #    self.data["code"] = self.data["_id"]

                # convert datetimes to strings
                datetime_cols = fast_data.get("datetime_cols")
                if datetime_cols:
                    database_type = self.db_resource.get_database_type()
                    # Sqlite stores the values in GMT when there is no timezone
                    # rather than the local timezone
                    if database_type == 'Sqlite':
                        is_gmt = True
                    else:
                        is_gmt = False

                    for col in datetime_cols:
                        # fast_data may not be in the columns
                        # if add_column() has been called
                        value = self.data.get(col)
                        if value:
                            # convert to UTC (NOTE: are we sure that this
                            # is always coming from the database?)
                            if not SObject.is_day_column(col):
                                value = SPTDate.convert(value, is_gmt=is_gmt)
                            self.data[col] = str(value)
                    

                boolean_cols = fast_data.get("boolean_cols")
                if boolean_cols:
                    for col in boolean_cols:
                        # fast_data may not be in the columns if add_column() has been called
                        value = self.data.get(col)
                        if value in ["false", "", 0, None]:
                            self.data[col] = False
                        else:
                            self.data[col] = True
                    

 

            else:
                self.data = {}
                data = self.data
                #self.data = dict(zip(columns, result))
                for column, value in zip(columns, result):
                    # convert all datetime objects to strings.  This simplifies
                    # export to various other source (such as XML)
                    if value and isinstance(value, datetimeclass):
                        date_string = str(value)
                        data[column] = date_string
                    else:
                        data[column] = value



        # handle attrs - made this lazy.  Will only look up if needed.  It
        # appears that the ParallelStatusWdg makes use of attributes.  Not sure
        # where else, but they unnecesary overhead for the vast majority of
        # cases
        self.attrs_handled = False

        # force insert attr
        self.force_insert = False

        # to handle trigger errors call by sobjects
        self._errors = None

        # metadata cache
        self.metadata = {}


    def _get_my_update_data(self):
        if self._update_data == None:
            self._update_data = {}
        return self._update_data
    def _set_my_update_data(self, update_data):
        self._update_data = update_data
    update_data = property(_get_my_update_data, _set_my_update_data)


    def _get_my_prev_data(self):
        if self._prev_data == None:
            self._prev_data = {}
        return self._prev_data
    def _set_my_prev_data(self, prev_data):
        self._prev_data = prev_data
    prev_data = property(_get_my_prev_data, _set_my_prev_data)



    def _get_my_prev_update_data(self):
        if self._prev_update_data == None:
            self._prev_update_data = {}
        return self._prev_update_data
    def _set_my_prev_update_data(self, prev_update_data):
        self._prev_update_data = prev_update_data
    prev_update_data = property(_get_my_prev_update_data, _set_my_prev_update_data)

    def _get_my_quoted_flag(self):
        if self._quoted_flag == None:
            self._quoted_flag = {}
        return self._quoted_flag
    def _set_my_quoted_flag(self, quoted_flag):
        self._quoted_flag = quoted_flag
    quoted_flag = property(_get_my_quoted_flag, _set_my_quoted_flag)


    def _get_my_errors(self):
        if self._errors == None:
            self._errors = []
        return self._errors
    def _set_my_errors(self, errors):
        self._errors = errors
    errors = property(_get_my_errors, _set_my_errors)

    def _get_my_security(self):
        if self._security == None:
            self._security = {}
        return self._security
    def _set_my_security(self, security):
        self._security = security
    security = property(_get_my_security, _set_my_security)


    def set_force_insert(self, force=True):
        self.force_insert = force



    def add_static_triggers(cls, search_type):
        '''for any kinds of insert run TaskCreatorTrigger to auto-create tasks where applicable'''
        from pyasm.command import Trigger
        event = "insert|%s" % search_type
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("mode", "same process,same transaction")
        trigger.set_value("class_name", "tactic.command.TaskCreatorTrigger")
        Trigger.append_static_trigger(trigger)
    add_static_triggers = classmethod(add_static_triggers)


    def column_exists(self, column):
        return SearchType.column_exists(self.full_search_type, column)


    def get_code_key(self):
        '''used in the transaction code'''
        from pyasm.biz import ProjectSetting
        search_type = self.get_base_search_type()
        prefix = ProjectSetting.get_value_by_key('code_prefix', search_type)
        if not prefix:
            prefix = self.get_table()
            prefix = prefix.upper()

        elif prefix.startswith("{") and prefix.endswith("}"):
            prefix = prefix.strip("{")
            prefix = prefix.strip("}")
            prefix = Search.eval(prefix, self, single=True)


        return prefix



    def get_database_impl(self):
        return self.db_resource.get_database_impl()


    def get_db_resource(self):
        return self.db_resource

    def get_database_type(self):
        return self.db_resource.get_database_type()




    def get_sql(self):
        return self.db_resource.get_sql()



    def get_project_code(self):
        search_type = self.full_search_type
        p = re.compile(".*\?project=(\w+)&?.*")
        m = p.search(search_type)
        if m:
            project_code = m.groups()[0]
        else:
            # here only for backwards compatibility
            #project_code = self.search_type_obj.get_project()
            from pyasm.biz import Project
            project_code = Project.get_global_project_code()

        if not project_code:
            project_code = "admin"

        return project_code


    def get_columns(self):
        columns = SearchType.get_columns(self.get_search_type())
        return columns



    def get_data(self, merged=True):
        if merged:
            data = self.data.copy()
            data.update(self.update_data)
            return data

        return self.data

    def set_data(self, data):
        data = data.copy()
        self.data = data


    def set_update_data(self, data):
        data = data.copy()
        self.update_data = data





    def get_project(self):
        from pyasm.biz import Project
        project_code = self.get_project_code()
        return Project.get_by_code(project_code)
            
    def get_schema(self):
        '''Get the schema for this sobject'''
        from pyasm.biz import Schema
        schema = Schema.get_by_sobject(self)
        return schema
 

    def get_id_col(self):
        '''returns the column which stores the id of the sobject'''
        search_type = self.full_search_type
        key = "SObject::%s::id_col" % search_type
        id_col = Container.get(key)
        if not id_col:
            database_impl = self.db_resource.get_database_impl()
            id_col =  database_impl.get_id_col(self.db_resource, search_type)
            Container.put(key, id_col)

        return id_col




    def get_id(self):
        '''returns the id of the sobject'''
        id_col = self.get_id_col()
        return self.get_value(id_col, no_exception=True)


    def get_code_col(self):
        '''returns the column which stores the id of the sobject'''
        database_impl = self.db_resource.get_database_impl()
        search_type = self.full_search_type
        return database_impl.get_code_col(self.db_resource, search_type)



    def get_search_type(self):
        '''returns the type of the sobject'''
        return self.full_search_type

    def get_base_search_type(self):
        '''returns the type of the sobject'''
        if isinstance(self, SearchType):
            return "sthpw/search_object"
        else:
            return self.search_type_obj.get_base_key()

    def get_base_parent_search_type(cls):
        return ""
    get_base_parent_search_type = classmethod(get_base_parent_search_type)



    def get_search_type_obj(self):
        '''returns the full search type object'''
        return self.search_type_obj

    def get_search_key(self, use_id=False):
        '''returns a string key that uniquely identifies this sobject'''
        #return "%s|%s" % (self.get_search_type() ,self.get_id() )
        return SearchKey.get_by_sobject(self, use_id=use_id)

    def get_database(self):
        '''get the database that stores the sobject'''
        #return self.search_type_obj.get_database()
        return self.database

    def get_table(self):
        '''get the table which stores the sobject'''
        return self.search_type_obj.get_table()


    def get_code(self):
        if self.has_value("code"):
            return self.get_value("code")
        else:
            return str(self.get_id())


    def get_display_value(self, long=False):
        from pyasm.biz import Schema
        schema = Schema.get()
        base_search_type = self.get_base_search_type()
        attrs = schema.get_attrs_by_search_type(base_search_type)

        display = attrs.get("display")
        if display:
            # evaluate the expression
            from pyasm.biz import ExpressionParser
            parser = ExpressionParser()
            result = parser.eval(display, self, single=True)
            return result
        else:
            return self.get_name(long=long)
        




    def get_name(self, long=False):
        '''get a readable name for this sobject'''
        name = ''
        if self.has_value("name"):
            name = self.get_value("name")
        if long:
            code = self.get_code()
            if name:
                name = '%s (%s)' %(name, code)
            else:
                code = self.get_code()
                id = self.get_id()
                if code != id:
                    name = '%s (%s)' %(code, id)
                else:
                    name = code
        else:
            if not name:
                name = self.get_code()
        return name


    def get_primary_key_value(self):
        return self.get_value(self.get_primary_key())

    def get_description(self):
        if self.has_value('description'):
            return self.get_value('description')
        else:
            return self.get_code()

    def get_attr(self, name):
        self._handle_attrs()
        if name in self.attrs:
            return self.attrs[name]
        elif self.has_value(name):
            # by default all columns are attrs
            return SObjectAttr( name, self )
        else:
            return None

    def get_attr_value(self, name):
        self._handle_attrs()
        attr = self.get_attr(name)
        return attr.get_value()

    def get_attr_names(self):
        self._handle_attrs()
        keys = self.attrs.keys()
        keys.sort()
        return keys


    # DEPRECATED
    def _handle_attrs(self):
        if self.attrs_handled:
            return

        self.attrs = {}
        self.attrs_handled = True


        # create an attr for every column
        for key,value in self.data.items():
            attr = SObjectAttr(key,self)
            self.attrs[key] = attr


        # get the config (However, SearchType can't need itself, so it
        # can't have a config file)
        if isinstance(self,SearchType):
            return

        database = self.get_database()
        self.config = SObjectConfig.get_by_search_type(self.search_type_obj, database)
        if self.config == None:
            return


        attr_names = self.config.get_attr_names()
        for attr_name in attr_names:
            # create the attr
            attr = self.config.create_attr(attr_name, self)

            # store a reference to the sobject in each attribute
            attr.set_sobject(self)

            self.attrs[attr_name] = attr



    def _get_dynamic_value(self, name, no_exceptions=False):

        search_type = self.get_search_type()
        if search_type.startswith("sthpw/"):
            return None

        key = "SObject:dynamic_attr_handler:%s:%s" % (search_type, name)

        handler = Container.get(key)
        if handler == None:
            config_dict = Container.get("SObject:dynamic_attr:config")
            if config_dict == None:
                config_dict = {}
                Container.put("SObject:dynamic_attr:config", config_dict)

            config = config_dict.get(search_type)
            if config == None:
                # this will require caching!!!
                #search = Search("config/widget_config")
                #search.add_filter("search_type", search_type)
                #search.add_filter("view", "attr_definition")
                #config = search.get_sobject()
                #if not config:
                #    return
                #config_xml = config.get_xml_value("config")
                config_xml = '''
                <config>
                  <attr_definition>
                    <element name='ec2_id'>
                      <handler class='ExpressionAttr'>
                        <expression>{@GET(.code)} 123Redlight</expression>
                      </handler>
                    </element>
                    <element name='foo'>
                      <handler class='ExpressionAttr'>
                        <expression>@GET(.id)</expression>
                      </handler>
                    </element>
                  </attr_definition>
                </config>
                '''

                from pyasm.widget import WidgetConfig
                config = WidgetConfig.get(view='attr_definition', xml=config_xml)
                config_dict[search_type] = config

            handler = config.get_handler(name, "handler")
            options = config.get_options(name, "handler")
            Container.put(key, handler)
            Container.put("%s:options" % key, options)


        if handler:
            options = Container.get("%s:options" % key)
            expression = options.get("expression")
            if expression:
                value = Search.eval(expression, self)
            else:
                value = ""
            return value

        else:
            return None


    def get(self, name, **kwargs):
        return self.get_value(name, **kwargs)


    def get_value(self, name, no_exception=False, auto_convert=True):
        '''get the value of the named attribute stored as metadata in the
        sobject.  The no_exception argument determines whethere or not
        an exception is raised if the sobject does not have this attr'''

        # DISABLING
        #value = self._get_dynamic_value(name, no_exception)
        #if value != None:
        #    return value
        if not name:
            return None

        is_data = False
        if name.find("->>") != -1:
            parts = name.split("->>")
            is_data = True
            name = parts[0]
            attr = parts[1]
        elif name.find("->") != -1:
            parts = name.split("->")
            is_data = True
            name = parts[0]
            attr = parts[1]



        from pyasm.biz import Translation
        lang = Translation.get_language()
        if lang:
            tmp_name = "%s_%s" % (name, lang)
            if not self.full_search_type.startswith("sthpw/") and SearchType.column_exists(self.full_search_type, tmp_name):
                name = tmp_name



        # first look at the update data
        # This will fail most often, so we don't use the try/except clause
        if self.has_updates and name in self.update_data:
            if is_data:
                attr_data = self.update_data.get(name) or {}
                if len(parts) > 2:
                    return attr_data.get(parts[1]).get(parts[2])
                else:
                    return attr_data.get(attr)
            else:
                return self.update_data[name]

        # then look at the old data
        try:
            value = self.data[name]

            if value and is_data:
                if len(parts) > 2:
                    value = value.get(parts[1]).get(parts[2])
                else:
                    value = value.get(attr)




            # NOTE: We should support datetime natively, however a lot
            # of basic operations don't work with datetime so we would always
            # have to check
            if value and isinstance(value, datetimeclass):
                value = str(value)
                return value

            if value and isinstance(value, dict):
                value = value.copy()

            if auto_convert and value == None:
                col_type = SearchType.get_column_type(self.full_search_type, name)
                if col_type in ['integer','float','numeric','decimal','double precision']:
                    return 0
                else: 
                    return ""
            else:
                return value
        except KeyError as e:
            pass


        if name != self.get_id_col() and self.get_id() == -1:
            return ""

        if no_exception:
            return ""

        raise SObjectValueException("Column [%s] does not exist in search_object type [%s]" % (name, self.get_search_type()) )



    def has_value(self, name):
        '''determines if the sobject contains a value with the given name'''

        if name.find("->>") != -1:
            parts = name.split("->>")
            name = parts[0]
        elif name.find("->") != -1:
            parts = name.split("->")
            name = parts[0]


        # first look at the update data
        if name in self.update_data:
            return True
        # then look at the old data
        elif name in self.data:
            return True
        else:
            return False


    def get_seq_value(self, name, delimiter=","):
        '''returns a list that is splitted from the value with a delimiter'''
        value = self.get_value(name)

        if value == "":
            return []
        else:
            return value.split(delimiter)

    def get_dict_value(self, name, delimiter=","):
        '''returns a dictionary of values splitted by the delimiter'''
        values = self.get_seq_value(name,delimiter)

        seq = {}
        for value in values:
            seq[value] = ''

        return seq


    def get_datetime_value(self, name):
        value = self.get_value(name)
        if isinstance(value, datetime.datetime):
            return value

        if value:
            value = parser.parse(value)
        else:
            value = None
        return value


    def get_datetime_display(self, name, format):
        value = self.get_value(name)
        if value:
            value = parser.parse(value)
            value = value.strftime(format)
        else:
            value = ""
        return value




    def get_json_value(self, name, default=None, no_exception=False):
        '''get the value that is stored as a json data structure'''
        value = self.get_value(name, no_exception=no_exception)
        if isinstance(value, dict):
            value = value.copy()
            return value

        if not isinstance(value, basestring):
            return value

        if value.startswith("zlib:"):
            value = Common.decompress_transaction(value)

        if value.strip():
            try:
                data = jsonloads(value)
            except:
                data = value
        else:
            data = default
        return data


    def set_json_value(self, name, value):
        if value is None:
            self.set_value(name, value)
            return
    
        column_type = SearchType.get_column_type(self.full_search_type, name)
        if column_type in ['json']:
            self.set_value(name, value)
            return

        data = jsondumps(value)

        length_before = len(data)
        cutoff = 10*1024
        if length_before > cutoff:
            data = Common.compress_transaction(data)
        
        self.set_value(name, data)

    

    def get_xml_root(self, name):
        '''provide the ability to specify xml roots that are different
        from the name of the column'''
        return name



    def get_xml_value(self, name, root=None, strip_cdata=True, remove_blank_text=True):
        '''convenience function to get xml data'''

        xml_dict = Container.get("SObject:xml_cache")
        if xml_dict == None:
            xml_dict = {}
            Container.put("SObject:xml_cache", xml_dict)
        search_key = self.get_search_key()
        key = "%s|%s" % (search_key, name)
        xml = xml_dict.get(key)
        if xml != None:
            return xml


        # Change this from root = "snapshot" by default to it being the
        # name of the column
        if not root:
            root = self.get_xml_root(name)
        
        # if this xml value starts with "zlib:" then decompress
        value = self.get_value(name)
        if value is None:
            value = ''

        if value.startswith("zlib:"):
            value = Common.decompress_transaction(value)

        xml = Xml(strip_cdata=strip_cdata)

        if value == "":
            value = "<%s/>" % root

        try:
            xml.read_string(value, remove_blank_text=remove_blank_text)
        except XmlException as e:
            value = "<%s/>" % root
            xml.read_string(value)

            msg = "Xml read error for [%s]: %s" % \
                (self.get_search_key(), e.__str__())

            Environment.add_warning("Xml read error", msg )

        # COMMENTED OUT FOR now until client_api_test pass
        #xml_dict[key] = xml
        return xml

    
    def skip_invalid_column(self):
        self._skip_invalid_column = True


    def process_value(self, name, value, column_type):
        info = {}
        info['quoted'] = False

        if column_type == "timestamp":
            if isinstance(value, basestring):
                try:
                    value = parser.parse(value)
                except ValueError:
                    pass

            if isinstance(value, datetime.datetime):
                if value.tzinfo:
                    value = SPTDate.convert_to_timezone(value, 'UTC')
                info['quoted'] = True

            info['value'] = value
        else:
            info = self.get_database_impl().process_value(name, value, column_type)

        return info


    def set_value(self, name, value, quoted=True, temp=False, no_exception=False):
        '''set the value of this sobject. It is
        not commited to the database'''

        if name.find("->") != -1:
            parts = name.split("->")
            return self.set_data_value(parts[0], parts[1], value)

        from pyasm.biz import Translation
        lang = Translation.get_language()
        if lang:
            tmp_name = "%s_%s" % (name, lang)
            if not self.full_search_type.startswith("sthpw/") and SearchType.column_exists(self.full_search_type, tmp_name):
                name = tmp_name
        
        # skip if column does not exist
        if self._skip_invalid_column and not SearchType.column_exists(self.full_search_type, name):
            return

        if temp:
            self._set_value(name, value, quoted=quoted)
            return

        # set_value removes the xml cache
        xml_dict = Container.get("SObject:xml_cache")
        if xml_dict == None:
            xml_dict = {}
            Container.put("SObject:xml_cache", xml_dict)
        search_key = self.get_search_key()
        key = "%s|%s" % (search_key, name)
        if key in xml_dict:
            del xml_dict[key]


        # make sure name is defined
        if not name:
            raise SObjectException("Name is None for value [%s]" % value)


        # explicitly test for None (empty string is ok)
        if value == None:
            if no_exception == False:
                raise SObjectException("Value for [%s] is None" % name)
            else:
                return

        # convert an xml object to its string value
        if isinstance(value, Xml):
            value.clear_xpath_cache()
            value = value.to_string()
        #elif type(value) in [types.ListType, types.TupleType]:
        elif isinstance(value, (list, tuple)):
            if len(value) == 0:
                # This check added to handle cases where a list is empty, as 'value[0]' is not defined
                # in that case. For now we just return and skip the setting of this value.
                #
                # NOTE: won't raise exception here for now ... just skip update of field. TODO: raise exception?
                #
                return
            value = value[0]

        # NOTE: this should be pretty quick, but could use some optimization
        column_type = SearchType.get_column_type(self.full_search_type, name)

        info = self.process_value(name, value, column_type)

        if info:
            value = info.get("value")
            quoted = info.get("quoted")

        # handle security
        from pyasm.biz import Project
        if isinstance(self, Project):
            project_code = '*'
        else:
            project_code = Project.get_project_code()
        key = { 'search_type' : self.search_type_obj.get_base_key(),
                'column' : name,
                'project': project_code}

        security = Environment.get_security()

        # unspecified default makes the access level edit
        if not security.check_access("sobject_column", key , "edit"):
            raise SecurityException("Column [%s] not editable for search type [%s]" % (name,self.get_search_type()) )

        all_column_info = SearchType.get_column_info(self.full_search_type)
        column_info = all_column_info.get(name) or {}
        if value == None or value == '':
            if not column_info:
                # NOTE: This is legal
                #print("WARNING: column [%s] does not exist in [%s]" % (name, self.get_base_search_type() ))
                pass
            elif column_info.get('data_type') in ['timestamp']:
                value = None
            elif column_info.get('data_type') in ['integer','bigint','float','numeric','decimal','double precision']:
                 # skip inserting '' in number type column
                 #return
                if column_info.get('nullable'):
                    value = None
                else:
                    return
            elif column_info.get('nullable'):
                value = None
        elif column_info.get('data_type') in ['timestamp','datetime','datetime2']:
            from dateutil import parser
            try:
                value = parser.parse(value)
                value = str(value)
            except Exception as e:
                # Keep the value as is
                value = value
        elif column_info.get('data_type') in ['varchar','text']:
            if isinstance(value, str):
                # this may be needed for those \x60 formatted string from a text file
                #value = value.decode('string_escape'))
                try:
                    value = value.decode('utf-8', 'ignore')
                except UnicodeDecodeError as e:
                    value = value.decode('iso-8859-1', 'ignore')
                except:
                    if IS_Pv3 and isinstance(value, bytes):
                        value = value.decode()

            # if the value is None and column info is not nullable then set to
            # empty string
            if not value and column_info and column_info.get('nullable') == False:
                value = ""

        self._set_value(name, value, quoted=quoted)



    def _set_value(self, name, value, quoted=True):
        '''called by set_value()'''

        if name in self.update_data or name not in self.data or value != self.data[name]:

            self.update_data[name] = value
            self.quoted_flag[name] = quoted

        self.has_updates = True



    def set_data_value(self, column, name, value, quoted=True):
        data = self.get_json_value(column, default={})
        data = data.copy()

        data[name] = value

        self.set_value(column, data)



    def set_expr_value(self, name, value, quoted=1):
        value = Search.eval(value)
        return self.set_value(name, value, quoted)



    def set_now(self, column="timestamp"):
        sql = DbContainer.get(self.db_resource)
        self.set_value(column, sql.get_default_timestamp_now(), quoted=False)


    def get_column_type(self, name):
        col_type = SearchType.get_column_type(self.full_search_type, name)
        return col_type



    #
    # Support for expressions
    #
    # DEPRECATED: use eval
    def eval_expression(self, expression):
        from pyasm.biz import ExpressionParser
        parser = ExpressionParser()
        result = parser.eval(expression, self)
        return result

    def eval(self, expression):
        from pyasm.biz import ExpressionParser
        parser = ExpressionParser()
        result = parser.eval(expression, self)
        return result





    #
    # Metadata: this allows setting of arbitrary metadata without having to
    #   create a whole new column
    #
    # NOTE: metadata is no longer stored as XML, it is stored as JSON
    def get_metadata_xml(self):
        metadata_mode = "json"
        if not self.metadata:
            if metadata_mode == 'json':
                self.metadata = self.get_json_value("metadata")
                if not self.metadata:
                    self.metadata = {}
            else:
                self.metadata = self.get_xml_value("metadata", root="metadata")

        return self.metadata



    def get_metadata(self):
        self.metadata = self.get_json_value("metadata")
        if not self.metadata:
            self.metadata = {}
        return self.metadata



    def get_metadata_value(self, name):
        ''' this method is not used much. get_metadata_dict is the main one'''
        metadata_mode = "json"
        if metadata_mode == 'json':
            value = self.metadata.get(name)
            if value == None:
                value = ''
            return value
        else:
            metadata = self.get_metadata_xml()
            return metadata.get_value("metadata/%s" % name)


    def get_metadata_dict(self):
        '''returns a dictionary of all of the metadata'''
        metadata_mode = "json"
        if metadata_mode == 'json':
            return self.get_metadata_xml()

        else:
            metadata = self.get_metadata_xml()
            self.get_metadata_xml()
            nodes = metadata.get_nodes("metadata/*")
            data = {}
            for node in nodes:
                name = Xml.get_node_name(node)
                data[name] = metadata.get_node_value(node)
            return data



    def set_metadata_value(self, name, value):
        # ensure that the value is a string
        metadata_mode = "json"
        if metadata_mode == "json":
            metadata = self.get_metadata_xml()
            # to overwrite old xml data with new json data
            if isinstance(metadata, basestring):
                metadata = {}
            metadata[name] = value
            self.set_json_value("metadata", metadata)
        else:

            value = str(value)

            metadata = self.get_metadata_xml()
            node = metadata.get_node("metadata/%s" % name)
            if node is not None:
                current_value = Xml.get_attribute(node, name)
                if value != current_value:
                    new_node = metadata.create_text_element(name, value)
                    root_node = metadata.get_root_node()
                    #root_node.replaceChild(new_node, node)
                    Xml.replace_child(root_node, node, new_node)
                else:
                    return
            else:
                new_node = metadata.create_text_element(name, value)
                root_node = metadata.get_root_node()
                metadata.append_child(root_node, new_node)

            self.set_value("metadata", metadata)



    def add_metadata(self, data, replace=False):
        '''takes a whole dictionary of values and sets them'''
        metadata_mode = "json"

        if metadata_mode == 'json':
            if replace:
                self.metadata = data
                self.set_json_value("metadata", data)
            else:
                for name, value in data.items():
                    self.set_metadata_value(name, value)

        else:
            if replace:
                self.set_value("metadata", "<metadata/>")
                self.metadata = None

            for name, value in data.items():
                self.set_metadata_value(name, value)




    # General setting of attributes values

    def set_id(self, value):
        '''handles the changing of the id.  This has to be a special function
        because, since this is the unique identifier, the "where id='##'"
        will update the incorrect in the database.'''
        self.new_id = int(value)

    def set_auto_code(self):
        '''set a unique code automatically for certain internal sTypes'''
        unique_id = uuid.uuid1()
        unique_code = '%s_%s'%(self.get_code_key(), unique_id)
        self.set_value('code', unique_code)

    def set_user(self, user=None):
        if user == None:
            user = Environment.get_user_name()
        self.set_value("login", user)

    def set_project(self, project_code=None):
        if not project_code:
            project_code = Project.get_project_code()
        self.set_value("project_code", project_code)



    def set_sobject_value(self, sobject, type=None):
        # makes a relation to this input sobject
        from pyasm.biz import Schema

        schema = Schema.get()
        attrs = schema.get_relationship_attrs(
            self.get_base_search_type(),
            sobject.get_base_search_type(),
        )

        attrs = schema.resolve_relationship_attrs(
            attrs,
            self.get_search_type(),
            sobject.get_search_type()
        )

        # TODO: While this logic below works, it should explicitly use from_col
        # and to_col
        relationship = attrs.get("relationship")
        if relationship in ['search_type', 'search_code', 'search_id']:

            self.set_value("search_type", sobject.get_search_type() )
            # fill in search_id only if it is an integer: this may not be the
            # case, such as in MongoDb, where the id is an object
            if SearchType.column_exists(self.full_search_type, "search_id"):
                sobj_id = sobject.get_id()
            
                if isinstance(sobj_id, six.integer_types):
                    self.set_value("search_id", sobj_id )
                else:
                    self.set_value("search_code", sobj_id )

            if SearchType.column_exists(self.full_search_type, "search_code") and SearchType.column_exists(sobject.get_search_type(), "code"):

                if sobject.get_database_type() == "MongoDb":
                    self.set_value("search_code", sobject.get_id() )
                else:
                    self.set_value("search_code", sobject.get_value("code") )

        elif relationship in ['code']:

            search_type = self.get_base_search_type()
            is_from = attrs.get("to") == search_type
            to_col = attrs.get("to_col")
            from_col = attrs.get("from_col")

            if is_from:
                self.set_value( to_col, sobject.get_value(from_col) )
            else:
                self.set_value( from_col, sobject.get_value(to_col) )
 
        elif relationship in ['general']:
            print('WARNING: relationship [%s] not supported' % relationship)

        else:
            raise SearchException("Relationship [%s] is not supported" % relationship)


    def set_parent(self, sobject, relationship=None):
        schema = self.get_schema()

        search_type = self.get_base_search_type()

        if isinstance(sobject, basestring):
            tmp_sobject = SearchKey.get_by_search_key(sobject)
            if not tmp_sobject:
                raise SearchException("Parent [%s] not found" %sobject) 
            else:
                sobject = tmp_sobject
            
        search_type2 = sobject.get_base_search_type()

        if not relationship:
            full_search_type = self.full_search_type
            full_search_type2 = sobject.get_search_type()
            relationship = schema.get_relationship(full_search_type, full_search_type2)
            #relationship = schema.get_relationship(search_type, search_type2)


        if relationship in ["search_type", "search_code", "search_id"]:
            self.set_sobject_value(sobject, type="hierarchy")
        elif relationship in ["foreign_key", "code", "id"]:
            #foreign_key = sobject.get_foreign_key()
            #code = sobject.get_code()
            #self.set_value(foreign_key, code)
            attrs = schema.get_relationship_attrs(search_type, search_type2, path=None)
            is_from = attrs.get("to") == search_type
            to_col = attrs.get("to_col")
            from_col = attrs.get("from_col")

            if is_from:
                self.set_value( to_col, sobject.get_value(from_col) )
            else:
                self.set_value( from_col, sobject.get_value(to_col) )
        elif relationship == "parent_code":
            code = sobject.get_code()
            self.set_value("parent_code", code)
        elif relationship == "search_key":
            search_key = SearchKey.build_by_sobject(sobject)
            self.set_value("search_key", search_key)


    def add_relationship(self, sobject, relationship=None):
        '''add this sobject as a relationship in the predefined manner'''
        return self.set_parent(sobject, relationship=relationship) 


    def add_related_connection(self, src_sobject, dst_sobject, src_path=None):
        '''adding the related sobject code to this e.g. (many-to-many) relationbship sobject''' 
        self.add_related_sobject(src_sobject, src_path=src_path)
        self.add_related_sobject(dst_sobject)

    def add_related_sobject(self, sobject, src_path=None):
        '''add a related sobject.  This uses the style relationships'''
        search_type = self.get_base_search_type()

        if isinstance(sobject, basestring):
            sobject = SearchKey.get_by_search_key(sobject)

        search_type2 = sobject.get_base_search_type()

        schema = self.get_schema()
        #relationship = schema.get_relationship(search_type, search_type2)
        attrs = schema.get_relationship_attrs(search_type, search_type2, path=src_path)

        relationship = attrs.get("relationship")
        if relationship == "search_type":
            relationship = schema.resolve_search_type_relationship(attrs, search_type, search_type2)

        is_from = attrs.get("to") == search_type
        to_col = attrs.get("to_col")
        from_col = attrs.get("from_col")
        

        if relationship == "search_code": 
            self.set_value("search_type", sobject.get_search_type() )
            self.set_value("search_code", sobject.get_code() )
            # maintain some backwards compatibility
            self.set_value("search_id", sobject.get_id() )
        elif relationship == "search_id":
            self.set_value("search_type", sobject.get_search_type() )
            self.set_value("search_id", sobject.get_id() )

        elif is_from:
            self.set_value( to_col, sobject.get_value(from_col) )
        else:
            self.set_value( from_col, sobject.get_value(to_col) )




    def connect(self, sobjects=[], context="reference"):
        if not isinstance(sobjects, list):
            sobjects = [sobjects]
            
        from pyasm.biz import SObjectConnection
        for sobject in sobjects:
            if isinstance(sobject, basestring):
                sobject = Search.get_by_search_key(sobject)
            SObjectConnection.create(self, sobject, context=context)


    def get_connections(self, context="reference"):
        from pyasm.biz import SObjectConnection
        connections, sobjects = SObjectConnection.get_connected_sobjects(self, context=context)
        return sobjects





    def is_retired(self):
        '''check if it is retired '''
        retired_col = self.search_type_obj.get_retire_col()
        if not self.has_value(retired_col):
            return False
        return self.get_value(retired_col) == 'retired' 

    def is_insert(self):
        search_id = self.get_id()
        if search_id == -1:
            return True
        elif self.get_id() in ['-1','']:
            return True
        return False


    def validate(self):
        '''validate entries into this sobject'''
        return True


    def on_insert(self):
        '''executed when an item is inserted'''
        pass


    def on_update(self):
        '''executed when an item is updated'''
        pass


    def on_delete(self):
        '''executed when an item is deleted'''
        pass



    def handle_commit_security(self):

        from pyasm.security import Sudo

        # certain tables can only be written by admin
        security = Environment.get_security()
        if security.is_admin() or Sudo.is_sudo():
            return True

        search_type = self.get_base_search_type()

        login = Environment.get_user_name()


        admin_types = [
                'config/custom_script'
        ]
        if search_type in admin_types:
            return False


        return True


    def store_version(self):
        # versioning
        versioning = False
        if versioning and self.get_base_search_type() in ["spme/wop","spme/shot"]:
            # find the last version
            last_search = Search("spme/version")
            last_search.add_column("version")
            last_search.add_filter("search_type", self.get_search_type())
            last_search.add_filter("search_code", self.get_code())
            last_search.add_order_by("version desc")
            last = last_search.get_sobject()
            if not last:
                version = 1
            else:
                version = last.get("version")
            version += 1

            new_version = SearchType.create("spme/version")
            new_version.set_value("version", version)
            new_version.set_value("search_type", self.get_search_type())
            new_version.set_value("search_code", self.get_code())
            new_version.set_user()

            # get and copy the data
            data = self.get_data()
            data = data.copy()

            # scrub the data
            new_data = {}
            for name, value in data.items():
                if value is None:
                    continue
                new_data[name] = value

            new_version.set_value("data", new_data)
            new_version.commit()



    def get_statement(self):
        return self.commit(return_sql=True)


    def commit(self, triggers=True, log_transaction=True, cache=True, return_sql=False):
        '''commit all of the changes to the database'''

        is_insert = False 
        id = self.get_id()
        if self.force_insert or id == -1:
            is_insert = True
        if id in ['-1', '']:
            self.set_id(-1)
            is_insert = True


        if not self.handle_commit_security():
            raise SecurityException("Security: Action not permitted")




        impl = self.get_database_impl()
        # before we make the final statement, we allow the sobject to set
        # a minimal set of defaults so that the sql statement will always
        # work
        if is_insert:
            self.set_defaults()


        if not is_insert:
            self.store_version()


        # remap triggers kwarg
        if triggers == True:
            triggers = "all"
        elif triggers == False:
            triggers = "integral"
        assert(triggers in ["all", "integral", "ingest", "none"])


        # to allow for the convenience of a SearchType to be used as an
        # SObject, the database and table must be hard coded in order to
        # avoid a circular loop
        is_search_type = isinstance(self,SearchType)

        # create the update statement
        update = None
        if is_insert:
            update = Insert()
        else:
            update = Update()

        # to allow for the convenience of a SearchType to be used as an
        # SObject, the database and table must be hard coded in order to
        # avoid a circular loop
        if is_search_type:
            database = SearchType.DATABASE
            table = SearchType.TABLE
        else:
            database = self.get_database()
            table = self.get_table()

        db_resource = self.get_db_resource()
        update.set_database(db_resource)
        # set the table to update
        update.set_table(table)

        if not is_insert:
            update.add_filter(self.get_id_col(), self.get_id() )
            #where = '"%s" = %s' % (self.get_id_col(), self.get_id())
            #update.add_where(where)



        # it is now safe to add the override id to the update data and update
        # object, since the "where" is already added to the update object
        id_override = False
        if self.new_id != -1:
            self.set_value("id", self.new_id)
            # set the id and clear the new_id
            id = self.new_id
            self.new_id = -1
            id_override = True



        # generate a code value for this sobject when triggers are set to "ingest".
        # This is a special condition
        if is_insert and triggers == "ingest":
            if not self.update_data or not self.update_data.get("code"):
                if SearchType.column_exists(self.full_search_type, "code"):
                    temp_search_code = Common.generate_random_key()
                    self.set_value("code", temp_search_code)

        # if no update data is specified
        if is_insert and not self.update_data:
            # if there is no update data, an error will result, so give
            # it a try with code as a random key ...
            # this will work for most search types
            if SearchType.column_exists(self.full_search_type, "code"):
                self.set_value("code", "NULL", quoted=False)

        # validate should raise an exception if data is not valid
        self.validate()

        sql = DbContainer.get(db_resource)

        column_types = SearchType.get_column_types(self.full_search_type)
        column_info = SearchType.get_column_info(self.full_search_type)

        # fill in the updated values
        is_postgres = impl.get_database_type() == 'PostgreSQL'
        is_sqlite = impl.get_database_type() == 'Sqlite'
        
        #is_mysql = impl.get_database_type() == 'MySQL'

        for key, value in self.update_data.items():
            quoted = self.quoted_flag.get(key)
            escape_quoted = False
            changed = False

            if isinstance(value, dict):
                value = jsondumps(value)


            # escape the backward slashes
            if is_postgres and isinstance(value, basestring):
                if value.find('\\') != -1:
                    value = value.replace('\\', '\\\\')
                    changed = True
                    escape_quoted = True
            if value and isinstance(value, datetimeclass):
                changed = True

            # if this is a timestamp, then add the a time zone.
            # For SQLite, this should always be set to GMT
            # For Postgres, if there is no time zone, then the value
            # needs to be set to localtime
            if column_types.get(key) in ['timestamp', 'datetime','datetime2']:
                if value and not SObject.is_day_column(key):
                    info = column_info.get(key) or {}
                    if not is_sqlite and not info.get("time_zone"):
                        # if it has no timezone, it assumes it is GMT
                        value = SPTDate.convert_to_local(value)
                    else:
                        value = SPTDate.add_gmt_timezone(value)
                    
                # stringified it if it's a datetime obj
                if value and not isinstance(value, basestring):
                    value = value.strftime('%Y-%m-%d %H:%M:%S %z')
           
                changed = True

            if changed:
                self.update_data[key] = value
            #impl.process_value(database, table, key, value)

            # For SQLServer, do not set the value for the ID column
            # when trying to do an sql UPDATE
            if not is_insert and key == 'id' and sql.get_database_type() == 'SQLServer':
                continue
            update.set_value(key, value, quoted=quoted, escape_quoted=escape_quoted )



        vendor = db_resource.get_vendor()
        if vendor in ["MongoDb"]:
            update.execute(sql)
            #statement = update.get_statement()
            #print("statement: ", statement)
            statement = "MongoDB!!!"


        elif vendor == 'Salesforce':
            impl = db_resource.get_database_impl()
            impl.execute_update(self, sql, update)

        else:
            # perform the update
            statement = update.get_statement()
            if not statement:
                return

            if return_sql:
                return statement

            # SQL Server: before a redo, set IDENTITY_INSERT to ON
            # to allow an explicit ID value to be inserted into the ID column of the table.
            # note: At any time, only one table in a session can have
            #       the IDENTITY_INSERT property set to ON. 
            if id_override == True:
                id_statement = impl.get_id_override_statement(table, True)
                if id_statement:
                    sql.do_update(id_statement)

            #print("statement: ", statement)
            sql.do_update(statement)


            """
            f = open("/tmp/sql_commit", 'a')
            f.write(statement)
            f.write('\n')
            f.close()
            """

            # SQL Server: after a redo, set IDENTITY_INSERT to OFF
            # to dis-allow an explicit ID value to be inserted into the ID column of the table.
            if id_override == True:
                id_statement = impl.get_id_override_statement(table, False)
                if id_statement:
                    sql.do_update(id_statement)


        Container.increment('Search:sql_commit')

        # Fill the data back in (autocreate of ids)
        # The only way to do this reliably is to query the database
        if is_insert:
            # assume that the id is constantly incrementing
            if not impl.has_sequences():
                id = sql.last_row_id
            else:
                sequence = impl.get_sequence_name(SearchType.get(self.full_search_type), database=database)
                id = sql.get_value( impl.get_currval_select(sequence))
                id = int(id)


        if triggers == "ingest":
            self.set_id(id)
            return


        # Get the updated values and fill it into data.  This handles
        # auto updated values in the database
        sobject = None
        if not is_search_type:

            from pyasm.security import Sudo
            sudo = Sudo()
            try:
                search = Search(self.full_search_type)
            finally:
                sudo.exit()
            search.set_show_retired_flag(True)
            # trick the search to believe that security filter has been applied
            search.set_security_filter()
            search.add_id_filter(id)
            sobject = search.get_sobject()
            if sobject == None:
                raise SObjectException("Insert/Update of [%s] failed. The entry with id [%s] cannot be found.\n%s" % (self.get_search_type(), id, statement))

            # need to update the update data with new values if
            # they are autogenerated
            for key, value in self.update_data.items():
                if not self.quoted_flag.get(key):
                    self.update_data[key] = sobject.get_value(key)

        else:
            sobject = self
            #sobject.data = self.update_data.copy()
            for key, value in self.update_data.items():
                self.data[key] = self.update_data[key]


        # if the code has changed, then update dependencies automatically
        prev_code = None
        if not is_insert and self.update_data.get("code") and self.data.get("code") and self.update_data.get("code") != self.data.get("code"):
            prev_code = self.data.get("code")


        # auto generate the new code
        search_code = None
        if sobject and column_info.get("code") != None:
            if not sobject.get_value("code", no_exception=True):
                search_code = self.generate_code(id)
            else:
                search_code = sobject.get_value("code")


        # now that we have all the changed data, store which changes
        # were made
        from pyasm.security import Site
        # Note: if this site is not explicitly the first one, then logging the change
        # timestamp is not supported (at the moment)
        search_type = self.get_search_type()
        if search_type not in [
                "sthpw/change_timestamp",
                "sthpw/transaction_log",
                "sthpw/sync_job",
                "sthpw/sync_log",
                'sthpw/message',
                'sthpw/message_log',
                'sthpw/queue',

        ] \
                and sobject and sobject.has_value("code") \
                and Site.get_site() == Site.get_first_site():


            # get the current transaction and get the change log
            # from this transaction
            transaction = Transaction.get()
            #if not is_insert and search_code and transaction:
            if search_code and transaction:
                key = "%s|%s" % (search_type, search_code)
                log = transaction.change_timestamps.get(key)
                if log == None:
                    # create a virtual log
                    log = SearchType.create("sthpw/change_timestamp")
                    log.set_auto_code()
                    log.set_value("search_type", search_type)
                    log.set_value("search_code", search_code)
                    transaction.change_timestamps[key] = log
                    changed_on = {}
                    changed_by = {}
                else:
                    changed_on = log.get_json_value("changed_on", {})
                    changed_by = log.get_json_value("changed_by", {})

                if not is_insert:
                    login = Environment.get_user_name()
                    for name, value in self.update_data.items():
                        changed_on[name] = "CHANGED"
                        changed_by[name] = login
                    log.set_json_value("changed_on", changed_on)
                    log.set_json_value("changed_by", changed_by)


        # store the undo information.  The transaction_log needs to
        # store both the old code and the new code
        if log_transaction:
            SObjectUndo.log_undo(self, search_code, id, is_insert, prev_code=prev_code)

        # store data for triggers    
        trigger_update_data = self.update_data.copy()

        trigger_prev_data = {}
        for key in trigger_update_data.keys():
            trigger_prev_data[key] = self.data.get(key)


        # remember the old data
        self.prev_data = self.data
        self.prev_update_data = self.update_data

        # replace the updated data
        if not is_search_type:
            self.data = sobject.data

        # reset the update data
        self.update_data = {}
        self.has_updates = False

        # set the description of the commit
        self.update_description = self.build_update_description(is_insert)


        # use the autogenerated code if none was explicitly specified
        if sobject and column_info.get("code") and not sobject.get_value("code", no_exception=True):
            sobject.set_value("code", search_code )
            sobject.commit(triggers="none", log_transaction=False)
            self.data['code'] = search_code



        
        # triggers are not executed when in undo or redo mode
        is_undo = Container.get("is_undo")
        sql = DbContainer.get(db_resource)
        sql.set_savepoint()

        # NOTE: this is run even if triggers is false because of the need to
        # run integral triggers
        #if triggers and is_undo != True:
        if triggers != "none" and is_undo != True:

            # call a trigger
            # Certain search types are ignored because these are required in
            # an insert and will cause an infinite loop
            base_search_type = self.get_base_search_type()
            if base_search_type not in [
                    'sthpw/transaction_log',
                    'sthpw/ticket',
                    'sthpw/transaction_state',
                    'sthpw/access_log',
                    'sthpw/status_log',
                    'sthpw/search_object',
                    'sthpw/wdg_settings',
                    'sthpw/sync_log',
                    'sthpw/sync_job',
                    'sthpw/message',
            # enabled triggers from message_log so that inserts to this table can send out notifications
            #        'sthpw/message_log',
                    'sthpw/change_timestamp',
                    'sthpw/sobject_list',
                    'sthpw/sobject_log'
            ]:

                process = self.get_value("process", no_exception=True)


                from pyasm.command import Trigger
                output = {}
                output["is_insert"] = is_insert
                if is_insert:
                    output["mode"] = "insert"
                else:
                    output["mode"] = "update"
                output["id"] = self.get_id()
                output["search_code"] = self.get_value("code", no_exception=True)
                output["search_type"] = self.get_search_type()
                output["search_key"] = SearchKey.build_by_sobject(self)
                output["update_data"] = trigger_update_data
                output["prev_data"] = trigger_prev_data
                output["sobject"] = self.get_sobject_dict()


                # call all of the triggers
                if is_insert:
                    mode = "insert"
                else:
                    mode = "update"
                # special condition for some base types
                if base_search_type in ["sthpw/note", "sthpw/task", "sthpw/work_hour", "sthpw/snapshot"]:
                    parent_type = self.get_value("search_type")
                    parts = parent_type.split("?")
                    parent_type = parts[0]
                else:
                    parent_type = self.get_base_search_type()
                self._call_triggers(trigger_update_data, mode, output, process, parent_type, triggers)

            
                # add message only if triggers is true
                if triggers:
                    self._add_message(sobject, output, mode)


            # cache this sobject, by code and id
            if cache:
                search_type = self.get_search_type()
                key = SearchKey.build_search_key(search_type, id, column='id', project_code=self.get_project_code())
                self.cache_sobject(key, self)
                code = self.get_code()
                if code:
                    key = SearchKey.build_search_key(search_type, code, column='code', project_code=self.get_project_code())
                    self.cache_sobject(key, self)



        if prev_code and triggers == "all":
            self._update_code_dependencies(prev_code)



        if is_insert:
            self.on_insert()
        else:
           self.on_update()







    def generate_code(self, id):
        search_type = self.get_base_search_type()


        # Generate more readable key
        parts = []

        # scope by server
        server = Config.get_value("install", "server")
        if server:
            parts.append(server)

        log_key = self.get_code_key()
        parts.append( log_key )



        from pyasm.biz import ProjectSetting
        if ProjectSetting.get_value_by_key('code_format', search_type) == 'random':
            # generate the code
            log_key = self.get_code_key()
            random_code = Common.generate_random_key(digits=10)
            parts.append( random_code )

        else:

            try:
                search_type = self.get_base_search_type()
                if search_type in [
                        'sthpw/file', 'sthpw/snapshot', 'sthpw/transaction_log',
                        'sthpw/ticket', 'sthpw/task','sthpw/sync_job','sthpw/sync_log'
                ]:
                    padding = 8
                else:
                    padding = 5


                int(id)
                number_expr = "%%0.%dd" % padding
                parts.append( number_expr % id )
            except:
                parts.append(str(id))



        delimiter = ""

        search_code = delimiter.join(parts)

        return search_code




    def _add_message(self, sobject, data, mode):

        # message types are "insert,update,change"
        search_type_obj = sobject.get_search_type_obj()
        events = search_type_obj.get_value("message_event", no_exception=True)
        if not events:
            return
        message_events = events.split("|")
        send_message = False
        for message_event in message_events:
            if message_event in [mode,'change']:
                send_message = True
                break
        if not send_message:
            return


        search_type = sobject.get_base_search_type()
        if search_type in ['sthpw/note','sthpw/task','sthpw/snapshot']:
            search_type = sobject.get_value("search_type")
            search_code = sobject.get_value("search_code")
            message_code = "%s&code=%s" % (search_type, search_code)
        elif search_type.startswith("sthpw/"):
            return
        elif search_type.startswith("config/"):
            return
        else:
            message_code = sobject.get_search_key()

        project_code = Project.get_project_code()


        message = Search.get_by_code("sthpw/message", message_code)

        """
        # if there are no subscriptions, don't bother storing
        #search = Search("sthpw/subscription")
        #search.add_filter("code", message_code)
        #search.add_filter("category", "sobject")
        #if search.get_count() == 0:
        #    return
        """

        search = Search("sthpw/message")
        search.add_filter("code", message_code)
        message = search.get_sobject()
        if not message:
            message = SearchType.create("sthpw/message")
            message.set_value("code", message_code)
            message.set_value("category", "sobject")

        # not suitable to make a dictionary unicode string
        #data = unicode(data)
        json_data = jsondumps(data, ensure_ascii=True)

        # this is not needed even for string literals with \
        #json_data = json_data.replace("\\", "\\\\")
        message.set_value("message", json_data )
        message.set_value("timestamp", "NOW")
        message.set_value("project_code", project_code)
        message.set_value("status", "complete")
        message.set_user()
        message.commit(triggers=False)



        # repeat with the log
        message = SearchType.create("sthpw/message_log")
        message.set_value("message_code", message_code)
        message.set_value("category", "sobject")
        message.set_value("message", json_data )
        message.set_value("project_code", project_code)
        message.set_value("timestamp", "NOW")
        message.set_user()
        message.set_value("status", "complete")
        message.commit(triggers=False)



        return message
        




        


    def _call_triggers(self, trigger_update_data, mode, output, process, parent_type, triggers):

        is_undo = Container.get("is_undo")
        if triggers == "integral" or is_undo == True:
            integral_only = True
        else:
            integral_only = False


        from pyasm.command import Trigger

        search_type = self.get_base_search_type()

        # build up a list of events and call the trigger
        events = [
            mode,
            '%s|%s' % (mode, search_type),
            'change',
            'change|%s' % search_type
        ]

        from pyasm.biz import Project
        project_code = Project.get_project_code()

        for column in trigger_update_data.keys():
            # skip timestamp column
            if column == 'timestamp':
                continue
            events.append( '%s|%s|%s' % (mode, search_type, column) )
            events.append( 'change|%s|%s' % (search_type, column) )

        keys = []
        for event in events:

            # first key
            key = {'event': event}
            Trigger.call_by_key(key, self, output, integral_only=integral_only, project_code=project_code)

            if parent_type:
                key = {'event': event}
                key['search_type'] = parent_type
                Trigger.call_by_key(key, self, output, integral_only=integral_only, project_code=project_code)



            if process:
                key = {'event': event}
                key['process'] = process
                Trigger.call_by_key(key, self, output, integral_only=integral_only, project_code=project_code)


            if process and parent_type:
                key = {'event': event}
                key['process'] = process
                key['search_type'] = parent_type
                Trigger.call_by_key(key, self, output, integral_only=integral_only, project_code=project_code)


            # process can be either the process name or the process code
            if process and self.get_base_search_type() in [
                    'sthpw/task',
                    'sthpw/note',
                    'sthpw/snapshot',
                    'sthpw/work_hour'
            ]:
                # need to to get the parent
                parent = self.get_parent()
                pipeline_code = None
                if parent:
                    pipeline_code = parent.get_value("pipeline_code", no_exception=True)

                if pipeline_code:
                    search = Search("config/process")
                    search.add_filter("process", process)
                    search.add_filter("pipeline_code", pipeline_code)
                    process_sobj = search.get_sobject()
                    if process_sobj:
                        process_code = process_sobj.get_code()

                        key = {'event': event}
                        key['process'] = process_code
                        Trigger.call_by_key(key, self, output, integral_only=integral_only, project_code=project_code)

                        if parent_type:
                            key = {'event': event}
                            key['process'] = process_code
                            key['search_type'] = parent_type
                            Trigger.call_by_key(key, self, output, integral_only=integral_only, project_code=project_code)








    def update(self):
        '''update the current sobject's data if the db has been changed since its creation'''
        #search = Search(self.search_type_obj)
        search = Search(self.full_search_type)
        search.set_show_retired_flag(True)
        # trick the search to believe that security filter has been applied
        search.set_security_filter()
        search.add_id_filter(self.get_id())
        sobject = search.get_sobject()
        if sobject == None:
            raise SObjectException("Failed to recache data")
        self.data = sobject.data



    def _update_code_dependencies(self, old_code):

        search_type = self.get_base_search_type()

        # set the data to the old code to get the dependencies
        new_code = self.data['code']
        self.data['code'] = old_code

        related_types = ['sthpw/snapshot', 'sthpw/note', 'sthpw/task']
        if search_type in related_types:
            return

        for related_type in related_types:
            related_sobjects = self.get_related_sobjects(related_type)
            if related_sobjects:
                print("Updating dependent search_type [%s]" % related_type)
            for related_sobject in related_sobjects:
                related_sobject.set_value("search_code", new_code)
                related_sobject.commit()


        from pyasm.biz import Schema
        schema = Schema.get()
        related_types = schema.get_related_search_types(search_type)
        for related_type in related_types:
            if related_type == "*":
                continue

            print("Preparing to update [%s]" % related_type)
            attrs = schema.get_relationship_attrs(search_type, related_type)
            relationship = attrs.get('relationship')

            if relationship == 'code':
                # attrs is a dictionary of the relationship details between the two
                # schema tables. We need to check if the related_type is the parent or the
                # child. Depending on which, we then check if the connected column is 
                # != "code". If it is, we can safely continue with the database operation, 
                # if not, there are dependencies that need changing before moving safely
                if related_type == attrs.get("from"):
                    if attrs.get("to_col") != "code":
                        continue
                else:
                    if attrs.get("from_col") != "code":
                        continue
                    


            related_sobjects = self.get_related_sobjects(related_type)
            for related_sobject in related_sobjects:
                print("... related: ", related_sobject.get_code())

            if related_sobjects:
                raise TacticException("There are related items in [%s].  Please change these first" % related_type)

        self.data['code'] = new_code



    def build_update_description(self, is_insert=True):
        '''This is asked for by the edit widget and possibly other commands'''
        if is_insert:
            action = "Inserted"
        else:
            action = "Updated"
        title = self.get_search_type_obj().get_value("title", no_exception=True)
        code = self.get_code()
        name = self.get_name()
        if code == name:
            description = "%s %s: %s" % (action, title, code)
        else:
            description = "%s %s: %s %s" % (action, title, code, name)

        return description



    def get_update_description(self):
        # if all of this is successful, add a description to the update.
        return self.update_description


    def get_prev_value(self, name):
        return self.prev_data.get(name)

    def get_prev_update_data(self):
        return self.prev_update_data
   
    def get_defaults(self):
        '''returns a dictionary of default name value pairs to be filled in
        whenver there is a commit'''
        defaults = {}
        from pyasm.biz import ProjectSetting

        autofill_pipeline_code = ProjectSetting.get_value_by_key('autofill_pipeline_code')
        if autofill_pipeline_code != 'false':
            base_search_type = self.get_base_search_type() 
            if base_search_type == 'sthpw/task':
                return defaults
            full_search_type = self.get_search_type()
            has_pipeline = SearchType.column_exists(full_search_type, "pipeline_code")
            if has_pipeline:
                from pyasm.biz import Pipeline
                pipelines = Pipeline.get_by_search_type(base_search_type)
                if len(pipelines) >= 1:
                    defaults['pipeline_code'] = pipelines[0].get_code()



        base_search_type = self.get_base_search_type() 
        if base_search_type != "sthpw/file":
            if self.column_exists("relative_dir"):
                parts = base_search_type.split("/")
                project_code = Project.get_project_code()
                defaults['relative_dir'] = '%s/%s' % (project_code, parts[1])


        return defaults



    def set_defaults(self):
        try:
            defaults = self.get_defaults()
            for key,value in defaults.items():
                if not self.has_value(key) or self.get_value(key) == None:
                    self.set_value(key, value)
        except Exception as e:
            print("Error: ", e.__str__())
            #raise



        # all timestamps must be set at least to now()
        if SearchType.column_exists(self.full_search_type, "timestamp") and not self.get_value("timestamp", no_exception=True):
            db_resource = self.get_db_resource()
            sql = DbContainer.get(db_resource)
            self.set_value("timestamp", sql.get_timestamp_now(), quoted=False)

        return



    # retiring and deleting

    def retire(self):
        '''retires the asset.  This is prefered to deleting because
        deletion is a loss of work and is permanently removed from ever
        existing'''
        retire_col = self.search_type_obj.get_retire_col()
        self.set_value(retire_col,"retired")
        self.commit()

        from .sobject_log import RetireLog
        RetireLog.create(self.get_search_type(), search_code=self.get_code() )

        # remember the data
        data = self.data.copy()

        # call a retire event
        from pyasm.command import Trigger
        output = {}
        output["is_retire"] = True
        output["mode"] = "retire"
        output["search_key"] = SearchKey.build_by_sobject(self)
        output["id"] = self.get_id()
        output["search_type"] = self.get_search_type()
        output["data"] = data
        output["sobject"] = self.get_sobject_dict()

        from pyasm.biz import Project
        project_code = Project.get_project_code()
        Trigger.call(self, "retire", output, project_code=project_code)
        Trigger.call(self, "retire|%s" % self.get_base_search_type(), output, project_code=project_code)
        Trigger.call(self, "change", output, project_code=project_code)
        Trigger.call(self, "change|%s" % self.get_base_search_type(), output, project_code=project_code)

        # add message
        self._add_message(self, output, 'retire')

    def reactivate(self):
        '''reactivate a retired asset'''
        retire_col = self.search_type_obj.get_retire_col()
        self.set_value(retire_col, "NULL", quoted=0)
        self.commit()



    def delete(self, log=True, triggers=True):
        '''delete the sobject (only the database)
        WARNING: use with extreme caution.  If you are uncertain,
        just use retire()
        '''
        security = Environment.get_security()
        base_search_type = self.get_base_search_type()

        id = self.get_id()
        if id == -1:
            return


        current_project_code = self.get_project_code()
        
        # special conditions of task, note and work_hour
        if base_search_type in ['sthpw/task', 'sthpw/note','sthpw/snapshot','sthpw/file','sthpw/work_hour']:
            sobject_project_code = self.get_value('project_code')
            key = { "code": base_search_type }
            key2 = { "code": base_search_type, "project": sobject_project_code }
            key3 = { "code": "*" }
            key4 = { "code": "*", "project": sobject_project_code }
            keys = [key, key2, key3, key4]
            default = "allow"

            if not security.check_access("search_type", keys, "delete", default=default):
                raise SObjectException('[%s] is not allowed to delete item in [%s]. You may need to adjust the access rules for the group.' % (Environment.get_user_name(), base_search_type))
        elif not base_search_type.startswith("sthpw/") and not base_search_type.startswith("config/"):
            # default to deny delete of any non sthpw or config sobjects
            key = { "code": base_search_type }
            key2 = { "code": base_search_type, "project": current_project_code }
            key3 = { "code": "*" }
            key4 = { "code": "*", "project": current_project_code }
            keys = [key, key2, key3, key4]
            default = "deny"
            if not security.check_access("search_type", keys, "delete", default=default):
                print("WARNING: User [%s] security failed for search type [%s]" % (Environment.get_user_name(), base_search_type))
                raise SObjectException('[%s] is not allowed to delete item in [%s]. You may need to adjust the access rules for the group.' % (Environment.get_user_name(), base_search_type))

        # remember the data
        data = self.data.copy()

        database_impl = self.get_database_impl()
        database_type = database_impl.get_database_type()

        db_resource = self.get_db_resource()
        sql = DbContainer.get(db_resource)


        # make sure we have the right table for search types
        is_search_type = isinstance(self,SearchType)
        if is_search_type:
            database = SearchType.DATABASE
            table = SearchType.TABLE
        else:
            database = self.get_database()
            table = self.search_type_obj.get_table()

        if database_type == 'MongoDb':

            database_impl.execute_delete(sql, table, id)


        else:
            where = '"%s" = %s' % (self.get_id_col(),id)

            if database_type == 'Oracle':
                # do fully qualified table names (i.e. include schema prefix) for Oracle SQL ... needed
                # for use with set-ups that use a service user to access the Oracle DB
                statement = 'DELETE FROM %s."%s" WHERE %s' % (database, table, where )
            elif database_type == 'SQLServer':
                statement = 'DELETE FROM [%s] WHERE %s' % (table, where)
            else:
                statement = 'DELETE FROM "%s" WHERE %s' % (table, where )

            sql.do_update(statement)

        # record the delete unless specifically not requested (for undo)
        if log:
            SObjectUndo.log_undo_for_delete(self)

        if triggers:
            # call a delete event
            from pyasm.command import Trigger
            from pyasm.biz import Project
            project_code = Project.get_project_code()
            output = {}
            output["is_delete"] = True
            output["mode"] = "delete"
            output["search_key"] = SearchKey.build_by_sobject(self)
            output["id"] = id
            output["search_type"] = self.get_search_type()
            output["data"] = data
            output["sobject"] = self.get_sobject_dict()
            Trigger.call(self, "delete", output)
            Trigger.call(self, "delete|%s" % base_search_type, output, project_code=project_code)
            Trigger.call(self, "change", output)
            Trigger.call(self, "change|%s" % base_search_type, output, project_code=project_code)

        # delete the sobject_list entry
        if base_search_type not in ['sthpw/sobject_list']:
            search = Search("sthpw/sobject_list")
            search.add_filter("search_type", base_search_type)
            search.add_filter("search_code", self.get_code() )
            sobject = search.get_sobject()
            if sobject:
                sobject.delete(log=log)

        self.on_delete()

       



    def clone(self, recursive=True, related_types=[], parent=None, extra_data={}):
        '''copy an sobject'''
        search_type = self.get_base_search_type()
        clone = SearchType.create(search_type)
        #clone.update_data = self.data.copy()

        for name, value in self.data.items():
            if value == None or name == 'code':
                continue

            if isinstance(value, list) or isinstance(value, dict):
                clone.set_json_value(name, value)
            else:
                clone.set_value(name, value)

        del(clone.update_data['id'])
        clone.set_id(-1)

        if parent:
            clone.set_parent(parent)

        for name, value in extra_data.items():
            clone.set_value(name, value)

        clone.commit(triggers=False)

        # copy recursively
        if related_types:
            for related_type in related_types:
                # if related type is the search type, then skip
                if related_type == search_type:
                    continue

                related_sobjects = self.get_related_sobjects(related_type)

                for related_sobject in related_sobjects:
                    related_sobject.clone(parent=clone)

        return clone





    # Directory structure functions
    def get_repo_handler(self, snapshot):
        '''Projects can define which repo handler is used.
        This gives the ability to use different styles and or 3rd party
        repositories such as Perforce or Subversion'''
        from pyasm.biz import Project
        repo_handler = Project.get_project_repo_handler()
        repo_handler.set_snapshot(snapshot)
        repo_handler.set_sobject(self)
        return repo_handler

    def get_repo(self, snapshot):
        '''get the repo for this specific snapshot'''
        repo_handler = self.get_repo_handler(snapshot)
        return repo_handler.get_repo()


    def get_web_dir(self,snapshot=None,file_type=None, file_object=None):
        '''The http sobject directory from the client point of view.
        The details are handled by the project class'''
        from pyasm.biz import Project
        dir = Project.get_project_web_dir(self,snapshot,file_type,file_object=file_object)
        return dir

    def get_lib_dir(self,snapshot=None,file_type=None, create=False, file_object=None, dir_naming=None):
        '''The nfs sobject directory from the server point of view.
        The details are handled by the project class'''
        from pyasm.biz import Project
        dir = Project.get_project_lib_dir(self,snapshot,file_type, create=create, file_object=file_object, dir_naming=dir_naming)
        return dir

    def get_env_dir(self,snapshot=None,file_type=None):
        '''This retrieves the unexpanded directory:
        $TACTIC_ASSET_DIR/bar/shot/...
        '''
        from pyasm.biz import Project
        dir = Project.get_project_env_dir(self,snapshot,file_type)
        return dir



    def get_remote_web_dir(self, snapshot=None, file_type=None):
        '''get_web_dir with the full http link.
        All web directories are, by default, relative links.  This function
        will force a full link, including the http://<server> part'''
        from pyasm.biz import Project
        dir = Project.get_project_remote_web_dir(self,snapshot,file_type)
        return dir


    def get_client_lib_dir(self, snapshot=None, file_type=None, create=False, file_object=None, dir_naming=None):
        '''The asset directory from the client point of view.  This is only
        valid if this directory is visible to the client'''
        # for now assume the same directory as the server
        from pyasm.biz import Project
        dir = Project.get_project_client_lib_dir(self,snapshot,file_type,\
                create=create, file_object=file_object, dir_naming=dir_naming)
        return dir


    def get_local_dir(self, snapshot=None):
        '''finds the local directory on the client to download files to'''
        base_dir = Config.get_value("checkin","win32_local_base_dir")
        return "%s/download" % (base_dir)



    def get_local_repo_dir(self, snapshot=None, file_type=None, file_object=None):
        '''the local sync of the Tactic repository'''
        from pyasm.biz import Project
        dir = Project.get_project_local_repo_dir(self,snapshot,file_type, file_object=file_object)
        return dir


    def get_sandbox_dir(self, snapshot=None, file_type=None):
        '''the local sandbox(work area) designated by Tactic'''
        from pyasm.biz import Project
        dir = Project.get_project_sandbox_dir(self,snapshot,file_type)
        return dir

    def get_relative_dir(self, snapshot=None, file_type=None, create=False, file_object=None, dir_naming=None):
        '''the relative direcory without any base'''
        from pyasm.biz import Project
        dir = Project.get_project_relative_dir(self,snapshot,file_type, create=create, file_object=file_object, dir_naming=dir_naming)
        return dir



    def get_column_info(self, column=None):
        column_info = SearchType.get_column_info(self.get_search_type())
        if not column:
            return column_info
        else:
            return column_info.get(column) or {}



    def alter_search(search):
        '''allow the sobject to alter the search'''
        pass
    alter_search = staticmethod(alter_search)



    def get_values(sobjects, attr_name, unique=False, no_exception=False ):
        ''' static method to get the value of multiple sobjects'''
        if not sobjects:
            return []
        list = [sobject.get_value(attr_name, no_exception=no_exception) for sobject in sobjects]
        # this is not the most comprehensive method of obtaining uniqueness
        # ordering is lost
        if unique:
            list = sorted(set(list))
        return list
    get_values = staticmethod(get_values)

    def get_int_values(sobjects, attr_name, unique=True ):
        ''' static method to get the value of multiple sobjects'''
        if not sobjects:
            return []
        list = [int(sobject.get_attr_value(attr_name)) for sobject in sobjects]
        # this is not the most comprehensive method of obtaining uniqueness
        # ordering is lost
        if unique:
            list = sorted(set(list))
        return list
    
    get_int_values = staticmethod(get_int_values)
     
    def get_dict(sobjects, key_cols=['id']):
        '''given a list of sobject, a dictionary is returned using key_cols
        as separated by '|' as the key'''
        dict = {}
        if not sobjects:
            return dict

        if not key_cols:
            for sobject in sobjects:
                key = sobject.get_search_key()
                dict[key] = sobject
        else:    
            for sobject in sobjects:
                #key = '|'.join([ str(sobject.get_value(col)) for col in key_cols]) 
                values = []
                for col in key_cols:
                    value = sobject.get_value(col)
                    if not isinstance(value, basestring):
                        value = str(value)
                    values.append(value)
                key = "|".join(values)

                dict[key] = sobject
        return dict

    get_dict = staticmethod(get_dict)

    

    def get_primary_key(self):
        '''TODO: incorporate this into a column in SearchType
           This is the column name of the primary key of this sobject.
           This column should be referenced by the column returned 
           by get_foreign_key()'''
        return "id"  


    # Searchs for relates sobjects.  This is designed to be a more generalized
    # solution than the parent/child relationships below.  This makes heavy
    # use of schema to find relationships between search types
    def get_related_sobject(self, related_type, filters=[], show_retired=False):
        search_type = self.get_base_search_type()
        search = Search(related_type)
        if show_retired:
            search.set_show_retired(True)
        if filters:
            search.add_op_filters(filters)

        search.add_relationship_filter(self)
        return search.get_sobject()

    def get_related_sobjects(self, related_type, filters=[], path=None, show_retired=False):

        # if we have an instance relationship, then we have to do a pre
        # search to the instance table
        search_type = self.get_base_search_type()

        from pyasm.biz import Schema
        schema = Schema.get(project_code=self.get_project_code())
        attrs = schema.get_relationship_attrs(search_type, related_type)
        relationship = attrs.get('relationship')
        if relationship == 'many_to_many':
            return []
            '''
            # this relationship is rather complicated
            attrs = {
                'relationship': 'many_to_many',
                'from': 'project/asset',
                'link_type': 'project/asset_in_asset',
                'to': 'project/asset',
                'to_path': 'sub'
            }

            # standard. Because all the connections are defined, we don't
            # have to go into detail.  We can use the connections that
            # already exists.
            attrs = {
                'relationship': 'many_to_many',
                'from': 'project/asset',
                'to': 'project/shot',
                'link_type': 'project/asset_in_shot',
            }
            '''

            link_type = attrs.get('link_type')
            from_path = attrs.get('from_path')  # not used yet
            to_path = attrs.get('to_path')

            search = Search(link_type)
            search.add_relationship_filter(self)
            link_sobjects = search.get_sobjects()

            sobjects_dict = Search.get_related_by_sobjects(link_sobjects, related_type, filters=filters, show_retired=show_retired, path=to_path)

            sobjects = []
            for name, items in sobjects_dict.items():
                sobjects.extend(items)

            return sobjects
        else:
            search_type = self.get_base_search_type()

            search = Search(related_type)
            if show_retired:
                search.set_show_retired(True)

            if filters:
                search.add_op_filters(filters)
            search.add_relationship_filter(self, path=path)
            sobjects = search.get_sobjects()


            return sobjects



    # Instance relationships
    def add_instance(self, sobject):
        search_type1 = self.get_base_search_type()
        search_type2 = sobject.get_base_search_type()

        from pyasm.biz import Schema
        attrs = Schema.get().get_relationship_attrs(search_type1, search_type2)
        relationship = attrs.get("relationship")
        if relationship != "instance":
            raise SearchException("Not an instance relationship")

        # get the instance
        instance_type = attrs.get("instance_type")

        instance = SearchType.create(instance_type)
        instance.add_related_sobject(self)
        instance.add_related_sobject(sobject)
        instance.commit()

        return instance




    def get_instances(self, search_type2):

        search_type1 = self.get_base_search_type()

        from pyasm.biz import Schema
        attrs = Schema.get().get_relationship_attrs(search_type1, search_type2)
        relationship = attrs.get("relationship")
        if relationship != "instance":
            raise SearchException("Not an instance relationship")

        # get the instance
        instance_type = attrs.get("instance_type")

        expression = "@SOBJECT(%s)" % (instance_type)
        instances = Search.eval(expression, self)

        return instances



    def remove_instance(self, sobject):
        search_type1 = self.get_base_search_type()
        search_type2 = sobject.get_base_search_type()

        from pyasm.biz import Schema
        attrs = Schema.get().get_relationship_attrs(search_type1, search_type2)
        relationship = attrs.get("relationship")
        if relationship != "instance":
            raise SearchException("Not an instance relationship")

        instance_type = attrs.get("instance_type")

        expression = "@SOBJECT(%s)" % (instance_type)
        from_instances = Search.eval(expression, self)

        to_instances = Search.eval(expression, sobject)

        for from_instance in from_instances:
            from_search_key = from_instance.get_search_key()
            for to_instance in to_instances:
                to_search_key = to_instance.get_search_key()
                if from_search_key == to_search_key:
                    to_instance.delete()

        # NOTE: need to clear the expression cache.  This may be a little
        # too heavy, but it is assumed that this operation does not
        # happen too often
        from pyasm.biz import ExpressionParser
        ExpressionParser.clear_cache()





    # Parent/Child Relationships
    def get_foreign_key(self):
        '''This is the foreign key that other sobjects will use to refer
        to this sobject type.'''
        return SearchType.get_foreign_key(self.search_type_obj.get_base_key())



    def get_all_children_search(self, child_type):
        '''gets the search object for searching children, without doing the
        search.  This provides the opportunity to add further filters to the
        search object'''
        search = Search(child_type)
        self.children_alter_search(search, child_type)
        return search


    def children_alter_search(self, search, child_type):
        # look at the schema for the type of relationship
        schema = self.get_schema()
        if schema:
            relationship = schema.get_relationship( self.get_base_search_type(), child_type )
            # the filters are based on the type of relationship
           

            if relationship == "search_type":
                search.add_filter("search_type", self.get_search_type() )
                search.add_filter("search_id", self.get_id() )

            elif relationship == "search_code":
                search.add_filter("search_type", self.get_search_type() )
                search.add_filter("search_code", self.get_code() )

            elif relationship == "search_key":
                search.add_filter("search_key", self.get_search_key() )
            elif relationship == "parent_code":
                code = self.get_code()
                search.add_filter( "parent_code", code )
            elif relationship == "id":
                relationship_attrs = schema.get_relationship_attrs( child_type, self.get_base_search_type() )
                code = self.get_id()
                col = relationship_attrs.get('from_col')
                if not col:
                    col = self.get_foreign_key()
                search.add_filter(col, code)
            elif relationship == "code":
                
                relationship_attrs = schema.get_relationship_attrs(child_type, self.get_base_search_type() )
            

                is_from = relationship_attrs['from'] in [ child_type, '*']
                code = self.get_code()
                if is_from:
                    col = relationship_attrs.get('from_col')
                else:
                    col = relationship_attrs.get('to_col')
                if not col:
                    col = self.get_foreign_key()
                search.add_filter(col, code)
            elif relationship == "general":
                # if connected through connection table,just return
                # nothing for now
                # NOTE: this is not really support yet
                search.set_null_filter()
            
            else:
                # FIXME: hard coding
                # use foreign code
                key = self.get_foreign_key()
                if key == 'asset_library_code':
                    key = 'asset_library'
                code = self.get_code()
                search.add_filter(key,code)
        else:
            key = self.get_foreign_key()
            code = self.get_code()
            search.add_filter(key,code)

        return search


    def get_all_children(self, child_type):
        '''The parent/child relationship for sobjects is defined the schema'''
        search = self.get_all_children_search(child_type)
        return search.get_sobjects()


    def get_child(self, child_type):
        '''convenience function to return a single child'''
        sobjects = self.get_all_children(child_type)
        if not sobjects:
            return None
        else:
            return sobjects[0]


    

    def get_parent_search_key(self):
        '''Without trying to get the parent sobject, just build the search key. 
        it conforms to the SearchKey.get_by_sobject() format, can be used by Task, Snapshot, Note'''
        search_type = self.get_value("search_type")
        search_code = self.get_value("search_code", no_exception=True)
        if search_code:
            search_key = SearchKey.build_search_key(search_type, search_code, column='code', project_code=None)
        else:
            search_id = self.get_value("search_id")
            search_key = SearchKey.build_search_key(search_type, search_id, column='id', project_code=None)

        return search_key


    def get_parent(self, parent_type=None, columns=[], show_retired=False):
        # columns arg is DEPRECATED

        if not parent_type:
            schema = self.get_schema()
            parent_type = schema.get_parent_type(self.get_base_search_type() )


        if parent_type == '*':

            attrs = schema.get_relationship_attrs("*", self.get_base_search_type(), path=None)


            prefix = attrs.get("prefix")
            if prefix:
                prefix = "%s_" % prefix
            else:
                prefix = ""

            search_type = self.get_value("%ssearch_type" % prefix, no_exception=True)
            # it could be an insert mode sobject
            if not search_type:
                return None


            attrs = schema.resolve_relationship_attrs(attrs, self.get_search_type(), search_type) 
            relationship = attrs.get('relationship')
            #if relationship == "search_type":
            #    relationship = schema.resolve_search_type_relationship(attrs, self.get_base_search_type(), search_type)

            if relationship == "search_code":
                search_type = self.get_value("%ssearch_type" % prefix)
                search_code = self.get_value("%ssearch_code" % prefix)
                return Search.get_by_code(search_type,search_code)

            elif relationship == "search_id":
                search_type = self.get_value("%ssearch_type" % prefix)
                search_id = self.get_value("%ssearch_id" % prefix)
                return Search.get_by_id(search_type,search_id)
            else:
                return None

        if parent_type:
            return self.get_related_sobject(parent_type, show_retired=show_retired)
            


    def get_reference(self, search_type):
        return self.get_parent(search_type)
  
    

    def get_icon_context(cls, context=None):
        '''gives various widgets (namely the ThumbWdg) and indication of
        which context of this asset provide an appropriate icon'''
        if context:
            return context
        else:
            #return "publish"
            # new default is icon
            return "icon"
    get_icon_context = classmethod(get_icon_context)
   

    def has_auto_current(self):
        '''determines whether new snapshots for this sobject are automatically
        set as the current.  This is true for most sobjects, however, some
        have the current explicitly set'''
        return True


    # class methods for SObject

    def create_new(cls):
       return SearchType.create(cls.SEARCH_TYPE)
    create_new = classmethod(create_new)


    def get_by_statement(cls, statement):
        ''' get SObjects by a custom SQL statement '''

        # protect against non statements
        if not statement:
            return []

        # to skip retired sobject, specify it in the statement 
        search_type = cls.SEARCH_TYPE
        search_type_obj = SearchType.get(search_type)

        # without full search type, we can only rely on search_type_obj to get db
        database = search_type_obj.get_database()
        db_resource = SearchType.get_db_resource_by_search_type(search_type)
        sql = DbContainer.get(db_resource)
        
        table = search_type_obj.get_table()
    
        results = sql.do_query(statement)

        #columns = Search.get_cached_columns(database, search_type_obj)
        columns = sql.get_columns(table)

        # create a list of objects
        sobjects = []

        # do this inline for performance
        search_type_obj = SearchType.get(search_type)
        class_path = search_type_obj.get_class()
        (module_name, class_name) = Common.breakup_class_path(class_path)

        for result in results:
            sobject = SearchType.fast_create_from_class_path(class_name, \
                search_type,columns,result, module_name=module_name)
            
            # add this sobject to the list of sobjects for the search
            sobjects.append(sobject)

        return sobjects
    get_by_statement = classmethod(get_by_statement)
   
    def get_by_search(cls, search, key, is_multi=False):
        ''' auto-caching given a search and a unique key'''
        assert cls.SEARCH_TYPE != None
        # switch to relevant search type for caching
        cls_search_type = None
        if cls.__name__ == 'SObject':
             cls_search_type = search.get_base_search_type()

        cached = cls.get_cached_obj(key, search_type=cls_search_type)
        # cached can be a sobject or a list of sobjects
        if cached:
            if cached == '__NONE__':
                if is_multi:
                    return []
                else:
                    return None
            else:
                return cached
        result = None
        if is_multi:
            result = search.get_sobjects()
        else:
            result = search.get_sobject()
        
        cls.cache_sobject(key, result, search_type=cls_search_type)
        return result

    get_by_search = classmethod(get_by_search)

    def get_by_id(cls, id, show_retired=True):
        '''class method to get all the asset with a give id.  Automatically
        caches the asset so that it this function can be called repeatedly
        without penalty'''

        search = Search( cls.SEARCH_TYPE )
        search.set_show_retired(show_retired)
        search.add_id_filter(id)
      
        search_type = search.get_search_type()
        key = SearchKey.build_search_key(search_type, id, column='id', project_code=search.project_code)
        if show_retired == False:
            key = '%s:False'%key
      
        sobj = cls.get_by_search(search, key)
       
        return sobj
    get_by_id = classmethod(get_by_id)


    def get_by_code(cls, code, show_retired=True):
        '''class method to get all the asset with a give code.  Automatically
        caches the asset so that it this function can be called repeatedly
        without penalty'''

        search = Search( cls.SEARCH_TYPE )
        search.set_show_retired(show_retired)
        search.add_filter('code', code)
        search_type = search.get_search_type()


        #key = "%s|%s" % (search_type,code)
        key = SearchKey.build_search_key(search_type, code, column='code', project_code=search.project_code)
        if show_retired == False:
            key = '%s:False'%key
        sobj = cls.get_by_search(search, key)
       
        return sobj
    get_by_code = classmethod(get_by_code)


    #
    # Collection Methods
    #
    def get_collection_type(self):
        base_search_type = self.get_base_search_type()
        parts = base_search_type.split("/")
        return "%s/%s_in_%s" % (parts[0], parts[1], parts[1])

    def add_to_collection(self, collection):
        if not collection.get_value("_is_collection", no_exception=True):
            raise Exception("SObject [%s] is not a collection" % collection.get_code() )

        collection_type = self.get_collection_type()

        search_code = self.get_code()
        parent_code = collection.get_code()

        search = Search(collection_type)
        search.add_filter("search_code", search_code)
        search.add_filter("parent_code", parent_code)
        item = search.get_sobject()
        if item:
            return

        item = SearchType.create(collection_type)
        item.set_value("search_code", search_code)
        item.set_value("parent_code", parent_code)
        item.commit()






    #
    # Caching methods
    #
    def _get_cached_key(key):
        return "%s::cached_obj" %key
    _get_cached_key = staticmethod(_get_cached_key)


    def get_cache_dict(cls, sobject=None, search_type=None):
        '''get the cache dict to insert new sobj into'''
        #if sobject and type(sobject) != types.ListType:
        if sobject and not isinstance(sobject, list):
            key = SObject._get_cached_key(sobject.get_base_search_type())
        elif search_type:
            key = SObject._get_cached_key(search_type)
        else:
            key = SObject._get_cached_key(cls.SEARCH_TYPE)
        dict = Container.get(key)
        # this is needed since cache_sobject() can happen before get_cached_obj()
        if dict == None:
            dict = {}
            Container.put(key, dict)
        return dict

    get_cache_dict = classmethod(get_cache_dict)


    def cache_sobject(cls, key, sobject, search_type=None):
        ''' cache any sobject for any SObject class'''
       
        dict = cls.get_cache_dict(sobject=sobject, search_type=search_type)
        cached_sobj = sobject
        if sobject == None or sobject == []:
            cached_sobj = '__NONE__'
        dict[key] = cached_sobj
     
    cache_sobject = classmethod(cache_sobject)


    def get_cached_obj(cls, key, search_type=None):
        ''' Get cached sobject resulted from get_by_code and get_by_id '''
        dict = cls.get_cache_dict(search_type=search_type)
     
        sobj = dict.get(key)
        return sobj

    get_cached_obj = classmethod(get_cached_obj)

    def clear_cache(cls, search_key=None, key=None):
        ''' clear the cache of an sobject '''
        cached_key = SObject._get_cached_key(cls.SEARCH_TYPE)
        if search_key:
            # just clears the sobject with this code 
            dict = Container.get(cached_key)
            project_code = Project.get_project_code()
            # adopt the rule used in get_by_code()
            if dict:
                dict[search_key] = None
        elif key:
            # just clears the sobject with this key
            dict = Container.get(cached_key)
            if dict:
                dict[key] = None
        else:
            # clears everything for this class
            dict = {}
            Container.put(cached_key, {})

    clear_cache = classmethod(clear_cache)








    def get_required_columns():
        '''get the required columns for csv import'''
        return []
    get_required_columns = staticmethod(get_required_columns)


    def has_versionless(snapshot, file_object):
        '''function to determine whether an sobject uses versionless checkins'''
        return False
    has_versionless = staticmethod(has_versionless)




    def get_sobject_dict(self, columns=None, use_id=False, language='python'):
        '''gets all the values for this sobject in a dictionary form, this mimics the one in API-XMLRPC'''

        if self.get_base_search_type() == "sthpw/virtual":
            columns = set(self.data.keys())
            columns.update( self.update_data.keys() )
            columns = list(columns)
        elif not columns:
            columns = SearchType.get_columns(self.get_search_type())

        result = {}
        for column in columns:
            if column == 'metadata':
                value = self.get_metadata_dict()
            else:
                value = self.get_value(column, no_exception=True)
                if language == 'c#':
                    if value == '':
                        value = None
                if isinstance(value, datetime.datetime):
                    value = str(value)
                elif isinstance(value, decimal.Decimal):
                    # use str to avoid loss of precision
                    value = str(value)


            result[column] = value
        result['__search_key__'] = SearchKey.build_by_sobject(self, use_id=use_id)
        return result


    def is_day_column(col):
        '''a rough way of differentiating a timestamp column used solely 
           for date. Time portion is set to 00:00:00 usually'''
        return col.endswith('day')
    is_day_column = staticmethod(is_day_column)


class SearchType(SObject):
    SEARCH_TYPE = "sthpw/search_object"
    DATABASE = "sthpw"
    TABLE = "search_object"

    def __init__(self, search_type, columns=None, result=None, fast_data=None):
        ''' do not use this constructor, use the get method '''
        # bake the current template
        if search_type == None:
            raise SObjectException("search_type is none")

        if isinstance(search_type,SObject):
            search_type = search_type.SEARCH_TYPE


        super(SearchType,self).__init__(search_type,columns,result, fast_data=fast_data)

        # cache this value as it gets called a lot
        self.base_key = self.get_value("search_type")
        if not self.base_key:
            # ??? not sure why this is empty on "sthpw/search_object" on 
            # dynamically created sobjects??
            self.base_key = "sthpw/search_object"

        self.database = None


    #
    # These are put here for backwards compatibility
    #
    # Commenting this out ... this overrides the base class which has
    # a different implementation.  Do not want this.
    """
    def set_project(cls, project):
        from pyasm.biz import Project
        Project.set_global_project_code(project)
    set_project = classmethod(set_project)

    def get_project(cls):
        ffasdsd
        from pyasm.biz import Project
        return Project.get_global_project_code()
    get_project = classmethod(get_project)
    """



    def get_defaults(self):
        search_type = self.get_value("search_type")
        return {
            'code': search_type
        }




    def get_search_type(self):
        return SearchType.SEARCH_TYPE


    def get_table(self):
        table = self.get_value("table_name")
        table = table.replace("{public}.", "")
        table = table.replace("public.", "")
        return table

   
    #
    # Sequence methods: these are static functions as SearchType has no
    # knowledge of the exact database used in a particular project.
    #
    def sequence_setval(cls, search_type, num=None):
        val = cls.sequence_util(search_type, 'setval', num=num)
        return val
    sequence_setval = classmethod(sequence_setval)

    def sequence_nextval(cls, search_type):
        '''call the current sequence nextval i.e. increment the next id '''
        val = cls.sequence_util(search_type, 'nextval')
        return val
    sequence_nextval = classmethod(sequence_nextval)

    def sequence_currval(cls, search_type):
        '''get the current sequence currval i.e. the next id '''
        val = cls.sequence_util(search_type, 'currval')
        return val
    sequence_currval = classmethod(sequence_currval)


    def sequence_util(cls, search_type, mode, num=''):
        '''get the current sequence currval i.e. the next id '''
        assert( isinstance(search_type, basestring) )

        from pyasm.biz import Project
        db_resource = Project.get_db_resource_by_search_type(search_type)

        search_type_obj = SearchType.get(search_type)
        table = search_type_obj.get_table()
        database = search_type_obj.get_database()

        sql = DbContainer.get(db_resource)
        impl = sql.get_database_impl()
        if not impl.has_sequences():
            return 0


        #sequence = impl.get_sequence_name(table, database=database)
        sequence = impl.get_sequence_name(search_type_obj, database=database)
        if mode == 'currval':
            id = sql.get_value( impl.get_currval_select(sequence))
        elif mode == 'nextval':
            id = sql.get_value( impl.get_nextval_select(sequence))
        elif mode == 'setval':
            if not num:
                raise SqlException('setval needs a number larger than 0')
            if impl.get_database_type() == "SQLServer":
                sql.do_update( impl.get_setval_select(sequence, num))
                id = sql.get_value( impl.get_currval_select(sequence))
            else:
                id = sql.get_value( impl.get_setval_select(sequence, num))

        id = int(id)
        return id
    sequence_util = classmethod(sequence_util)



    def get_database(self, use_cache=True):
        # use_cache is deprecated

        #if use_cache and not self.database:
        #    check = True
        #elif not use_cache:
        #    check = True
        #else:
        #    check = False

        check = True
        if check:
            database = self.get_value("database")
            if database == "{project}":
                from pyasm.biz import Project
                self.database = Project.get().get_database_name()
            elif database.startswith("{") and database.endswith("}"):
                # TEST
                var = database[1:-1]
                settings = {
                    'database': "portal"
                }
                self.database = settings.get("database")
            else:
                self.database = database

        return self.database


    #
    # database methods
    #
    def get_db_resource_by_search_type(cls, search_type):
        from pyasm.biz import Project
        project = Project.get_by_search_type(search_type)
        db_resource = project.get_project_db_resource()
        return db_resource
    get_db_resource_by_search_type = classmethod(get_db_resource_by_search_type)


    def get_database_impl_by_search_type(cls, search_type):
        db_resource = cls.get_db_resource_by_search_type(search_type)
        return db_resource.get_database_impl()
    get_database_impl_by_search_type = classmethod(get_database_impl_by_search_type)


    def get_sql_by_search_type(cls, search_type):
        from pyasm.biz import Project
        #project = Project.get_by_search_type(search_type)
        #db_resource = project.get_project_db_resource()
        db_resource = Project.get_db_resource_by_search_type(search_type)

        sql = DbContainer.get(db_resource)
        return sql
    get_sql_by_search_type = classmethod(get_sql_by_search_type)


    def get_columns(cls, search_type, show_hidden=True):
        # get the columns 

        sql = cls.get_sql_by_search_type(search_type)

        # get the table
        search_type_obj = SearchType.get(search_type)
        table = search_type_obj.get_table()
    
        columns = sql.get_columns(table)

        #    if "id" in columns:
        #        columns.remove("id")
        #    if "s_status" in columns:
        #        columns.remove("s_status")

        for column in columns:
            if column.startswith("_tmp"):
                columns.remove(column)

        return columns
    get_columns = classmethod(get_columns)



    def get_column_types(cls, search_type):
        # process the column types to match indexes of the above elements
        if search_type == 'sthpw/virtual':
            return {}

        # get the columns
        key = "SearchType:type:%s" % search_type
        #key = "SearchType:types:%s:%s" % (db_resource, table)

        column_types = Container.get(key)
        if column_types == None:
            column_types = {}

            from pyasm.biz import Project
            project = Project.get_by_search_type(search_type)
            db_resource = project.get_project_db_resource()
            search_type_obj = SearchType.get(search_type)
            table = search_type_obj.get_table()

            sql = DbContainer.get(db_resource)
            column_types = sql.get_column_types(table)
            Container.put(key, column_types)

        return column_types
    get_column_types = classmethod(get_column_types)


    def get_column_type(cls, search_type, column):
        column_types = cls.get_column_types(search_type)
        return column_types.get(column)
    get_column_type = classmethod(get_column_type)



    def get_column_info(cls, search_type):
        # process the column types to match indexes of the above elements
        column_info = Container.get("SearchType:column_info:%s" % search_type)
        if column_info == None:

            if search_type == 'sthpw/virtual' or search_type.startswith("table/"):
                column_info = {}
            else: 
                from pyasm.biz import Project
                project = Project.get_by_search_type(search_type)
                db_resource = project.get_project_db_resource()
                sql = DbContainer.get(db_resource)

                search_type_obj = SearchType.get(search_type)
                table = search_type_obj.get_table()

                column_info = sql.get_column_info(table)

            Container.put("SearchType:column_info:%s" % search_type, column_info)
        return column_info

    get_column_info = classmethod(get_column_info)

    def clear_column_cache(cls, search_type):
        '''clear the column cache in 2 steps'''
        # this needs to be None to clear
        Container.put("SearchType:column_info:%s" % search_type, None)

        from pyasm.biz import Project
        project = Project.get_by_search_type(search_type)
        db_resource = project.get_project_db_resource()
        sql = DbContainer.get(db_resource)
        key = "DatabaseImpl:column_info"
        cache_dict = Container.get(key)
        if cache_dict:
            search_type_obj = SearchType.get(search_type)
            table = search_type_obj.get_table()
            key2 = "%s:%s" % (db_resource, table)
            #cache_dict[key2] = None
            del(cache_dict[key2])


    clear_column_cache = classmethod(clear_column_cache)

            
        

    def column_exists(cls, search_type, column):
        if isinstance(search_type, SObject):
            search_type = search_type.get_search_type()

        column_info = cls.get_column_info(search_type)
        if column.find("->"):
            parts = column.split("->")
            column = parts[0]
        has_column = column_info.get(column) != None
        return has_column
    column_exists = classmethod(column_exists)




    def get_tactic_type(cls, search_type, column):
        '''These are the tactic types (as opposed to the database types)'''

        """
        # TODO: attempt to put types in widget config ....???
        tactic_types = Container.get("tactic_types")
        if tactic_types == None:
            tactic_types = {}
            Container.put("tactic_types", tactic_types)

            search = Search("config/widget_config")
            search.add_filter("category", "Type")
            configs = search.get_sobjects()

            for config in configs:
                config_xml = config.get_xml_value("config")
                search_type = config.get_value("search_type")
                tactic_types[search_type] = config_xml


        config_xml = tactic_types.get(search_type)
        if config_xml:
            xpath = "config/type/element[@name='%s']/@type" % column
            type = config_xml.get_value(xpath)
            if type:
                return type
        """

        info = cls.get_column_info(search_type)
        column_info = info.get(column)
        if not column_info:
            return "string"

        # right now, the type is the table type
        type = column_info.get("data_type")
        size = column_info.get("size") or 256

        if type == "varchar" and size > 256:
            type = "text"
        elif type.startswith("time"):
            type = "time"
        elif type.startswith("datetime"):
            type = "datetime"
        elif type in ['double precision','numeric','decimal']:
            type = "float"
        elif type in ['character','char']:
            type = "character"


        return type

    get_tactic_type = classmethod(get_tactic_type)



    def get_tactic_types(cls, search_type):
        '''These are the tactic types (as opposed to the database types)'''

        # look in the database
        column_types = cls.get_column_types(search_type)
        types = {}

        for column, column_type in column_types.items():
            types[column] = cls.get_tactic_type(search_type, column)

        return types
    get_tactic_types = classmethod(get_tactic_types)







    def get_class(self):
        class_name = self.get_value("class_name")
        # FIXME: why is class_name an integer at some point??
        assert isinstance(class_name, basestring)

        if class_name == "":
            return "pyasm.search.SObject"
        else:
            assert class_name.strip() == class_name
            return class_name

    def get_description(self):
        return self.get_value("description")

    def get_label(self):
        label = '%s (%s)' %(self.get_base_key(), self.get_title())
        return label

    def get_title(self):
        title = self.get_value("title")
        if title == "":
            # take off the schema
            title = self.get_base_key()
            parts = title.split("/")
            if len(parts) < 2:
                title = self.get_table()
            else:
                title = parts[1]
            title = Common.get_display_title(title)

        return title


    def get_search_type_id_col(self):
        id_col = self.data.get("id_column")
        if not id_col:
            return "id"
        else:
            return id_col


    def get_search_type_code_col(self):
        id_col = self.data.get("code_column")
        if not code_col:
            return "code"
        else:
            return code_col




    def get_retire_col(self):
        return "s_status"



    def get_base_key(self):
        return self.base_key



    def get_project_code(self):
        # first look at how the search type points to the database
        database = self.get_value("database")
        if database == "{project}":
            # if it is variable, then get the project
            project_code = Project.get_project_code()

        else:
            project_code = database

        return project_code





    def get_foreign_key(cls, search_type):
        '''This returns attr that all other sobjects will use to reference
        to this sobject.  By default, it is <table>_code.
        Note: this should probably be <table>_id to be more generic,
        however, most of Tactic will use <table>_code'''
        search_type_obj = SearchType.get(search_type)

        if SearchType.column_exists(search_type, "code"):
            return "%s_code" % search_type_obj.get_table()
        else:
            return "%s_id" % search_type_obj.get_table()

    get_foreign_key = classmethod(get_foreign_key)
        

 
    def get_icon_context(self, context=None):
        class_name = self.get_class()
        if not class_name:
            class_name = 'pyasm.search.SObject'
        try:
            exec( Common.get_import_from_class_path(class_name) )
            return eval("%s.get_icon_context(%s)" % (class_name, context))
        except:
            return "icon"


    def get_virtual(cls, key):
        # look at the virtual stypes first
        virtual_key = "SearchType:virtual_stypes"
        virtual_stypes = Container.get(virtual_key)
        if virtual_stypes == None:
            virtual_stypes = {}
            Container.put(virtual_key, virtual_stypes)
        search_type = virtual_stypes.get(key)
        return search_type
    get_virtual = classmethod(get_virtual)
  
    def set_virtual(cls, key, search_type):
        # set the virtual stype
        virtual_key = "SearchType:virtual_stypes"
        virtual_stypes = Container.get(virtual_key)
        if virtual_stypes == None:
            virtual_stypes = {}
            Container.put(virtual_key, virtual_stypes)
        virtual_stypes[key] = search_type
    set_virtual = classmethod(set_virtual)
  


    # static function
    # Note: use_mapping is DEPRECATED
    def get(cls, key, use_mapping=True, no_exception=False):
        # See if there are any projects in the string.
        search_type = None

        # look at the virtual stypes first
        search_type = cls.get_virtual(key)
        if search_type != None:
            return search_type


        if key.find("?") != -1:
            base, project_str = key.split("?")

            resource = None
            # if there is a project
            if project_str.find('project') != -1:
                from pyasm.biz import Project
                project_code = Project.extract_project_code(key)
                project = Project.get_by_code(project_code)
                if project:
                    resource = project.get_value("resource", no_exception=True)
                
            if resource:
                search_key = "sthpw/search_object?project=%s" % project_code
                search = RemoteSearch(search_key)
                search.add_filter("search_type", base)
                search_type = search.get_sobject()
            else:
                try:
                    search_type = cls._get_data(base)
                except SearchException:
                    if not no_exception:
                        raise

        else:
            base = key
            try:
                search_type = cls._get_data(base)
            except SearchException as e:
                if not no_exception:
                    raise

        cls.add_triggers(base)

        return search_type
    get = classmethod(get)



    def add_triggers(cls, base):
        # Add some triggers.  These will only be added when a search type
        # is accessed for the first time.
        # 
        triggers = Container.get("SearchType::triggers")
        if triggers == None:
            triggers = {}
            Container.put("SearchType::triggers", triggers)


        if triggers.get(base):
            return

        base_triggers = {}
        triggers[base] = base_triggers
        if base == 'sthpw/task':
            if base_triggers.get(base) == None:
                #exec("from pyasm.biz import Task")
                from pyasm.biz import Task
                Task.add_static_triggers()
                base_triggers[base] = True

        if not base.startswith("sthpw/") and base_triggers.get("task_insert") == None:
            SObject.add_static_triggers(base)
            base_triggers["task_insert"] = True


        if not base.startswith("sthpw/") and not base.startswith("config/"):
            # global search trigger.  Add all automatically
            if not base_triggers.get('global_search'): 
                from pyasm.command import Trigger
                event = "change|%s" % base
                trigger = SearchType.create("sthpw/trigger")
                trigger.set_value("event", event)
                trigger.set_value("mode", "same process,same transaction")
                trigger.set_value("class_name", "tactic.command.GlobalSearchTrigger")
                Trigger.append_static_trigger(trigger)
                base_triggers["global_search"] = True

            if not base_triggers.get('folder_trigger'): 
                event = "insert|%s" % base
                trigger = SearchType.create("sthpw/trigger")
                trigger.set_value("event", event)
                trigger.set_value("mode", "same process,same transaction")
                trigger.set_value("class_name", "tactic.command.FolderTrigger")

                Trigger.append_static_trigger(trigger)
                base_triggers["folder_trigger"] = True






        elif base == 'sthpw/login_group':
            if not base_triggers.get('login_group_sync'): 
                from pyasm.command import Trigger
                event = "change|%s" % base
                trigger = SearchType.create("sthpw/trigger")
                trigger.set_value("event", event)
                trigger.set_value("mode", "same process,same transaction")
                trigger.set_value("class_name", "tactic.command.LoginGroupTrigger")
                Trigger.append_static_trigger(trigger)
                base_triggers["login_group_sync"] = True

        elif base == 'sthpw/snapshot':
            if not base_triggers.get('snapshot_lastest_triger'):
                from pyasm.biz import Snapshot
                Snapshot.add_integral_trigger()
            base_triggers["snapshot_latest_trigger"] = True


    add_triggers = classmethod(add_triggers)




    def set_global_template(cls, var, impl):
        if var == "project":
            return Project.set_global_project_code(impl)
            #return cls.set_project(impl)

        print("DEPRECATED: set_global_template: ", var, impl)
    set_global_template = classmethod(set_global_template)

    def get_global_template(cls, var):
        if var == "project":
            return Project.get_global_project_code()
            #return cls.get_project()

        print("DEPRECATED: get_global_template: ")
        return SObjectFactory.get_template(var)
    get_global_template = classmethod(get_global_template)




    # utility function
    def break_up_key(key):
        '''takes a search type string and breaks it up into its two parts.
        This is purely a string function and does not require the sobject.
        There reason for this function is to prevent infinite loops within
        the sobject.  This occurs because SearchType is an SObject itself'''
        if key.find("?") != -1:
            search_type, template = key.split("?")
        else:
            search_type = key
            template = ""
        return search_type, key

    break_up_key = staticmethod(break_up_key)

    def get_schema_config(search_type):
        '''get a schema config for a search type'''
        xml = Xml(string='<config/>')
        root = xml.get_root_node()
        view = 'schema_definition'
        view_node = xml.create_element(view)
        xml.append_child(root, view_node)
        widget_config = None

        info = SearchType.get_column_info(search_type)
        columns = SearchType.get_columns(search_type)

        for column in columns:
            el = xml.create_element('element')
            Xml.set_attribute(el, 'name', column)
            dict = info.get(column)
            data_type = dict.get('data_type')
            nullable = dict.get('nullable')

            Xml.set_attribute(el, 'data_type', data_type)
            Xml.set_attribute(el, 'nullable', nullable)
            xml.append_child(view_node, el)
        from pyasm.widget import WidgetConfig
        widget_config = WidgetConfig.get(view=view, xml=xml.to_string())
        return widget_config

    get_schema_config = staticmethod(get_schema_config)



    def create(cls, search_type, columns=None, result=None):
        '''creation function for all sobject'''
        # super complicated dynamically importing a module
        # and instantiating the appropriate class
        class_path = None
        if search_type == "sthpw/search_object":
            class_path = "pyasm.search.SearchType"
        else:
            search_type_obj = SearchType.get(search_type)
            class_path = search_type_obj.get_class()

        # Put in a new inline creator that avoids the whole Marshaller.
        #sobject = Common.create_from_class_path(class_path, \
        #    [search_type,columns,result])
        sobject = cls.fast_create_from_class_path(class_path, \
            search_type,columns,result)
        return sobject
    create = classmethod(create)


    def fast_create_from_class_path(cls, class_name, search_type, columns, result, module_name=None, fast_data=None):

        if not module_name:
            (module_name, class_name) = Common.breakup_class_path(class_name)

        #try:
        module = sys.modules.get(module_name)
        if not module:
            __import__(module_name)
            module = sys.modules.get(module_name)

        try:
            object = getattr(module, class_name)(search_type, columns, result, fast_data=fast_data)
        except Exception as e:
            #if class_name == "SearchType":
            if True:
                import traceback
                print("Error: ", e)
                # print the stacktrace
                tb = sys.exc_info()[2]
                stacktrace = traceback.format_tb(tb)
                stacktrace_str = "".join(stacktrace)
                print("-"*50)
                print(stacktrace_str)
                print(str(e))
                print("-"*50)

            print("WARNING: class [%s] does not accept fast_data" % class_name)
            object = getattr(module, class_name)(search_type, columns, result)

        return object
    fast_create_from_class_path = classmethod(fast_create_from_class_path)




    def _get_data(cls, search_type):

        # if it already exists, then get the cached data
        cache_name = "SearchType:search_object_data"
        search_object_data = Container.get(cache_name)
        if search_object_data == None:
            search_object_data = {}
            Container.put(cache_name, search_object_data)

        if isinstance(search_type, SObject):
            search_type = search_type.SEARCH_TYPE

        sobject = search_object_data.get(search_type)
        if sobject:
            return sobject


        # get it from the global cache
        from pyasm.biz import CacheContainer
        cache = CacheContainer.get("sthpw/search_object")
        if cache:
            sobject = cache.get_value_by_key("search_type", search_type)
            if sobject:
                return sobject

        # create a virtual search type
        if search_type == 'sthpw/virtual':
            columns = ['id', 'table_name', 'title', 'search_type','class_name', 'namespace','database']
            result = ['0', 'unknown', 'Virtual', 'sthpw/virtual','pyasm.search.SObject','sthpw','sthpw']
            sobject = cls.create("sthpw/search_object",columns,result)
            return sobject

        if search_type.startswith('table/'):
            parts = search_type.split("/")
            namespace = parts[0]
            table = parts[1]
            #project = '__NONE__'
            project = "{project}"
            columns = ['id', 'table_name', 'title', 'search_type','class_name', 'namespace','database']
            result = ['0', table, Common.get_display_title(table), search_type,'pyasm.search.SObject',namespace,project]
            sobject = cls.create("sthpw/search_object",columns,result)
            return sobject



        # build the search type sobject manually.  has to be done because
        # otherwise you would just get an infinite loop
        database = Environment.get_sobject_database()
        db_resource = DbResource.get_default(database)
        table = "search_object"
        sql = DbContainer.get(db_resource)
        # get the data for the search_type
        select = Select()
        select.set_database(sql)
        select.add_table(table)
        select.add_filter("search_type", search_type)

        #query = select.get_statement()
        #results = sql.do_query(query)
        results = select.execute(sql)
        from pyasm.security import Site
        if not results:
            # if no results are found, then this search type is not explicitly
            # registered.  It could, however, be from a template
            #from pyasm.security import Site
            #print("Site: ", Site.get_site())
            #print("sql: ", select.get_statement())

            # for now just throw an exception
            raise SearchException("Search type [%s] not registered" % search_type )

        result = results[0]
        columns = sql.get_columns(table)

        # create the sobject
        sobject = cls.create("sthpw/search_object",columns,result)
        search_object_data[search_type] = sobject

        return sobject

    _get_data = classmethod(_get_data)

    def build_search_type(search_type, project_code=None):
        # do not append project for sthpw/* search_type
        if search_type.startswith('sthpw/'):
            return search_type

        if search_type.find("?") != -1:
            if project_code:
                # Note: should maybe chnage project
                return search_type
            else:
                return search_type

        if not project_code:
            from pyasm.biz import Project
            project_code = Project.get_project_code()

        return "%s?project=%s" % (search_type, project_code)

    build_search_type = staticmethod(build_search_type)




    def breakup_search_type(search_type):

        if search_type.find("?") == -1:
            parts = search_type.split("/")
            if len(parts) == 1:
                parts = ['','']

            return {
                'search_type': search_type,
                'namespace': parts[0],
                'table': parts[1],
                'project': "",
                'code': ""
            }

        parts = search_type.split("?")

        search_type = parts[0]
        search_type_parts = search_type.split("/")
        if len(search_type_parts) == 1:
            namespace = ''
            table = ''
        else:
            namespace = search_type_parts[0]
            table = search_type_parts[1]

        name_value_pairs = parts[1]
        name_value_parts = name_value_pairs.split("&")


        data = {
            'search_type': search_type,
            'namespace': namespace,
            'table': table,
        }
        for name_value_part in name_value_parts:
            name, value = name_value_part.split("=")
            data[name] = value

        return data


    breakup_search_type = staticmethod(breakup_search_type)

    def get_related_types(cls, search_type, direction="children"):
        '''find all the downstream related types for delete purpose in delete_sobject() or DeleteToolWdg'''
        from pyasm.biz import Schema, Project
        project_code = Project.extract_project_code(search_type)
        
        schema = Schema.get(project_code=project_code)
        related_types = schema.get_related_search_types(search_type, direction=direction)
        parent_type = schema.get_parent_type(search_type)


        # some special considerations
        # FIXME: this needs to be more automatic.  Should only be
        # deletable children (however, that will be defined)
        if search_type in ['sthpw/task','sthpw/note', 'sthpw/snapshot']:
            if "sthpw/project" in related_types:
                related_types.remove("sthpw/project")

            if "sthpw/login" in related_types:
                related_types.remove("sthpw/login")

            if "config/process" in related_types:
                related_types.remove("config/process")



        if direction == "children" and parent_type in related_types:
            related_types.remove(parent_type)

        related_types.append('sthpw/note')
        related_types.append('sthpw/task')
        related_types.append('sthpw/snapshot')
        if 'sthpw/work_hour' not in related_types:
            related_types.append('sthpw/work_hour')
    
        return related_types

    get_related_types = classmethod(get_related_types)


class SObjectFactory(Base):
    '''DEPRECATED: use SearchType'''
    def create(search_type, columns=None, result=None):
        '''creation function for all sobject'''
        # super complicated dynamically importing a module
        # and instantiating the appropriate class
        class_path = None
        if search_type == "sthpw/search_object":
            class_path = "pyasm.search.SearchType"
        else:
            search_type_obj = SearchType.get(search_type)
            class_path = search_type_obj.get_class()

        sobject = Common.create_from_class_path(class_path, \
            [search_type,columns,result])
        return sobject
    create = staticmethod(create)



from pyasm.common import TacticException

class MissingTableException(TacticException):
    pass

class MissingColumnException(TacticException):
    pass

class MissingException(TacticException):
    pass


class SObjectUndo:
    '''separate class which manages the undo capability of an sobject'''

    def log_undo(sobject, search_code, search_id, is_insert, prev_code=None):

        # do not log the command log - DEPRECATED
        if sobject.get_search_type() in [
                "sthpw/command_log",
                "sthpw/wdg_settings",
                "sthpw/transaction_log",
                "sthpw/change_timestamp",
                "sthpw/ticket",

                # NOTE: do not log sync jobs changes in transaction log
                "sthpw/sync_job",
                "sthpw/sync_log",
                "sthpw/sync_server",
                "sthpw/cache",
                "sthpw/queue",

                'sthpw/message',
                'sthpw/message_log'
        ]:
            return
        if sobject.get_search_type() == "sthpw/transaction_log":
            return


        old_data = sobject.data
        new_data = sobject.update_data

        # don't bother logging if there is no new data for edits.  Inserts
        # are always registered
        if not is_insert and len(new_data.keys()) == 0:
            return

        # get the transaction, if there is one
        transaction = Transaction.get()
        if not transaction:
            return

        # build the sobject xml action description
        xml = transaction.get_transaction_log()

        sobject_node = transaction.create_log_node("sobject")
        search_type = sobject.get_search_type()
        Xml.set_attribute(sobject_node,"search_type",sobject.get_search_type())

        column_types = SearchType.get_column_types(search_type)

        if search_code:
            Xml.set_attribute(sobject_node,"search_code", search_code)
        else:
            Xml.set_attribute(sobject_node,"search_id", search_id)

        if prev_code:
            Xml.set_attribute(sobject_node,"prev_search_code", prev_code)


        from pyasm.security import Site
        site = Site.get_site()
        if site:
            Xml.set_attribute(sobject_node,"site", site)


        if is_insert:
            Xml.set_attribute(sobject_node,"action","insert")

            for key,value in new_data.items():

                node = xml.create_element("column")
                Xml.set_attribute(node,"name",key)
                if value == None:
                    value = ""
                elif column_types.get(key) == 'timestamp':
                    value = SPTDate.add_gmt_timezone(value)
                    value = str(value)
                elif column_types.get(key) == 'boolean':
                    if value in [True,'true',1, '1']:
                        value = "true"
                    else:
                        value = "false"

                Xml.set_attribute(node,"to",value)
                xml.append_child(sobject_node, node)
        else:
            Xml.set_attribute(sobject_node,"action","update")

            # store the old values
            for key in new_data.keys():
                node = xml.create_element("column")
                Xml.set_attribute(node,"name",key)

                # make sure that none values are treated as empty ""
                # In an sobject, it is ok for data to be "None"
                from_data = old_data.get(key)
                if from_data == None:
                    from_data = ""
                elif isinstance(from_data, str):
                    # this could be slow, but remove bad characters
                    if not IS_Pv3:
                        from_data = unicode(from_data, errors='ignore').encode('utf-8')
                to_data = new_data[key]
                if to_data == None:
                    to_data = ""
                elif isinstance(to_data, str):
                    # this could be slow, but remove bad characters
                    if not IS_Pv3:
                        to_data = unicode(to_data, errors='ignore').encode('utf-8')
                elif column_types.get(key) == 'timestamp':
                    to_data = SPTDate.add_gmt_timezone(to_data)
                    to_data = str(to_data)
                    from_data = SPTDate.add_gmt_timezone(from_data)
                    from_data = str(from_data)
                elif column_types.get(key) == 'boolean':
                    if to_data in [True,'true']:
                        to_data = "true"
                    else:
                        to_data = "false"
                    if from_data in [True,'true']:
                        from_data = "true"
                    else:
                        from_data = "false"
                
                
                Xml.set_attribute(node,"from",from_data)
                Xml.set_attribute(node,"to",to_data)
                xml.append_child(sobject_node, node)

    log_undo = staticmethod(log_undo)




    def log_undo_for_delete(sobject):
        '''this file handles the undo mode for delete of an sobject'''
        # do not log the command log - DEPRECATED
        if sobject.get_search_type() in [
                "sthpw/command_log",
                "sthpw/change_timestamp",
                "sthpw/sync_job",
                "sthpw/sync_log",
                "sthpw/sync_server",
                "sthpw/transaction_log",
                "sthpw/ticket",
                "sthpw/cache",
                "sthpw/queue",

                'sthpw/message',
                'sthpw/message_log'

        ]:
            return

        data = sobject.data

        transaction = Transaction.get()
        if not transaction:
            return

        # build the sobject xml action description
        xml = transaction.get_transaction_log()

        sobject_node = transaction.create_log_node("sobject")
        Xml.set_attribute(sobject_node,"search_type",sobject.get_search_type())

        search_code = sobject.get_value("code", no_exception=True)
        if search_code:
            Xml.set_attribute(sobject_node,"search_code", search_code)
        else:
            search_id = sobject.get_id()
            Xml.set_attribute(sobject_node,"search_id", search_id)



        Xml.set_attribute(sobject_node,"action","delete")
        tmp_col_name = sobject.get_database_impl().get_temp_column_name()
        if tmp_col_name and data.get(tmp_col_name):
            del data[tmp_col_name]
            
        for key,value in data.items():
            node = xml.create_element("column")
            Xml.set_attribute(node,"name",key)
            if value == None:
                value = ""
            
            Xml.set_attribute(node,"from",value)
            xml.append_child(sobject_node, node)

    log_undo_for_delete = staticmethod(log_undo_for_delete)





    def undo(node):
        '''function that acutally does the undo'''

        search_type = Xml.get_attribute(node,"search_type")
        search_id = Xml.get_attribute(node,"search_id")
        search_code = Xml.get_attribute(node,"search_code")

        # ensure that this is a proper search id
        if search_id:
            try:
                search_id = int(search_id)
            except ValueError as e:
                # try to extract from quotes: example '15'
                if search_id.startswith("'") and search_id.endswith("'"):
                    try:
                        search_id = int(search_id.strip("'"))
                    except ValueError as e:
                        print("ERROR: undo error: ", e.__str__())
                        return

        # get the sobject
        search = Search(search_type)
        if search_code:
            search.add_filter("code", search_code)
        else:
            search.add_filter("id", search_id)
        sobject = search.get_sobject()

        # NOTE:
        # If the sobject is none, that means that the system thought it
        # exists but it actually didn't.  The only know reason for this
        # would be that a commit failed due to referential integrity
        # violation.  This is not reported until commit time.
        # This will at least allow backout of that error
        action = Xml.get_attribute(node,"action")


        if action == "delete":
            # if the sobject still exists, we have an inconsistency
            if sobject:
                print("WARNING: deleted sobject still exists [%s, %s]" % (search_type, search_code))

            # recreate the sobject
            sobject = SearchType.create(search_type)

            columns = Xml.xpath(node,"column")
           
            tmp_col_name = sobject.get_database_impl().get_temp_column_name()
          
            for column in columns:
                name = Xml.get_attribute(column,"name")
                # id and code are set outside of the columns.  They
                # recorded only for information purposes.  Should they
                # even be recorded at all?
                if name in ['code', 'id', tmp_col_name]:
                    continue

                value = Xml.get_attribute(column,"from")
                sobject.set_value(name,value)
            if len(columns) > 0:
                if search_code:
                    sobject.set_value("code", search_code)
                else:
                    sobject.set_id(search_id)

                sobject.set_force_insert()
                sobject.commit()


        # if no sobject exists, then don't bother updating.
        # TODO: there are some operations where the object might not exist
        # but in general it should and there should probably be more enforcement
        # on this
        if sobject == None:
            return


        if action == "insert":
            # on an insert simply delete
            sobject.delete(log=False)
        elif action == "update":
            # revert to the old values
            columns = Xml.xpath(node,"column")
            for column in columns:
                name = Xml.get_attribute(column,"name")
                value = Xml.get_attribute(column,"from")
                sobject.set_value(name,value)

            if len(columns) > 0:
                sobject.commit()


    undo = staticmethod(undo)



    def redo(node, no_exception=True):
        #no_exception=False

        import time
        start = time.time()

        from dateutil import parser
        search_type = Xml.get_attribute(node,"search_type")
        action = Xml.get_attribute(node,"action")

        column_types = SearchType.get_column_types(search_type)

        # if the code was changed, we have to use the prev search code
        search_code = Xml.get_attribute(node,"prev_search_code")
        if not search_code:
            search_code = Xml.get_attribute(node,"search_code")

        # Use of this is deprecated as of 4.0
        search_id = Xml.get_attribute(node,"search_id")


        # get the transaction time if it was supplied
        transaction_time = Xml.get_attribute(node, "timestamp")
        if transaction_time:
            transaction_time = parser.parse(transaction_time)

        # get the changed_timestamps for this sobject
        # if this in an insert, then the change_timestamp entry cannot exist
        # so skip
        if search_code and action != "insert":
            search = Search("sthpw/change_timestamp")
            search.add_filter("search_type", search_type)
            search.add_filter("search_code", search_code)
            change_log = search.get_sobject()
        else:
            change_log = None

        if not change_log:
            changed_on = {}
        else:
            changed_on = change_log.get_json_value("changed_on", {})


        search_type_obj = SearchType.get(search_type)


        database_type = DatabaseImpl.get().get_database_type()
        if action == "insert":
            # create a new sobject
            sobject = SearchType.create(search_type)

            columns = Xml.xpath(node,"column")
            for column in columns:
                name = Xml.get_attribute(column,"name")

                if not SearchType.column_exists(search_type, name):
                    msg = "Column [%s] does not exist in search_type [%s]" % (name, sobject.get_search_type() )
                    if no_exception:
                        print("WARNING: %s" % msg)
                        continue
                    else:
                        raise MissingException(msg)

                value = Xml.get_attribute(column,"to")
                quoted = True
                # only SQL server can't interpret GETDATE() function as a string
                
                column_type = column_types.get(name)
                if database_type == 'SQLServer':
                    if column_type == 'datetime2' and value =='GETDATE()':
                        quoted = False
                elif database_type == 'Sqlite':
                    if column_type == 'timestamp' and value in ["CURRENT_TIMESTAMP", "datetime('now')"]:
                        quoted = False
                elif database_type == 'MySQL':
                    if column_type in ['timestamp', 'datetime'] and value in ["CURRENT_TIMESTAMP", "UTC_TIMESTAMP()"]:
                        quoted = False


                if column_type == 'timestamp':
                    try:
                        if value == "now()":
                            value = SPTDate.now()
                        else:
                            value = SPTDate.convert(value)
                    except:
                        print("WARNING: could not parse timestamp [%s]" % value)

                elif column_type == 'boolean':
                    if value == 'true':
                        value = True
                    else:
                        value = False



                sobject.set_value(name,value, quoted=quoted)
            if search_code:
                sobject.set_value("code", search_code)
            else:
                sobject.set_id(search_id)

            sobject.commit()

        elif action == "update":

            # get the sobject
            if search_code:
                sobject = Search.get_by_code(search_type, search_code)
            else:
                sobject = Search.get_by_id(search_type, search_id)
            if not sobject:
                msg = "sobject [%s, code=%s] does not exist when trying to update in redo" % (search_type, search_code)
                if no_exception:
                    print("WARNING: %s" % msg)
                    return
                else:
                    raise MissingException(msg)
                    

            # set to the new values
            columns = Xml.xpath(node,"column")
            for column in columns:
                name = Xml.get_attribute(column,"name")
                value = Xml.get_attribute(column,"to")

                # if the col was changed later than this transaction
                # then skip
                col_changed = changed_on.get(name)
                if col_changed and transaction_time:
                    # need to convert to timestamps
                    # if the date is mangled, then change the data
                    try:
                        col_changed = parser.parse(col_changed)
                        if col_changed > transaction_time:
                            print("Column [%s] was changed after this transaction ... skipping" % name)
                            print("Transaction time: ", transaction_time)
                            print("Column modification time: ", col_changed)
                            continue
                    except:
                        print("WARNING: modification date mangled for column [%s]... skipping" % name)

                if not SearchType.column_exists(search_type, name):
                    msg = "WARNING: Column [%s] does not exist in search_type [%s]" % (name, sobject.get_search_type() )
                    if no_exception:
                        print("WARNING: %s" % msg)
                        continue
                    else:
                        raise MissingException(msg)


                quoted = True
                # only SQL server can't interpret GETDATE() function as a string
                column_type = column_types.get(name)
                if column_type == 'datetime2' and value =='GETDATE()':
                    quoted = False

                elif column_type == 'timestamp':
                    value = SPTDate.convert(value)
                elif column_type == 'boolean':
                    if value == 'true':
                        value = True
                    else:
                        value = False

                sobject.set_value(name,value, quoted=quoted)


            if len(columns) > 0:
                sobject.commit()


        elif action == "delete":
            # get the sobject
            if search_code:
                sobject = Search.get_by_code(search_type, search_code)
            else:
                # Deprecated
                sobject = Search.get_by_id(search_type, search_id)
                search_code = search_id

            if sobject == None:
                error = "Error trying to delete sobject [%s, %s] that does not exist." % (search_type, search_code)
                if no_exception:
                    print("WARNING: %s" % error)
                else:
                    raise MissingException(error)
            else:
                sobject.delete(log=False)


    redo = staticmethod(redo)




class SearchKey(object):
    '''convenience class for unique identifier for an sobject'''

    def build_search_key(cls, search_type, code, column='code', project_code=None):

        if search_type.find("?") != -1:
            search_key = "%s&%s=%s" % (search_type, column, code)
            return search_key

        if not project_code:
            from pyasm.biz import Project
            project_code = Project.get_project_code()

        if search_type.startswith("sthpw/"):
            search_key = "%s?%s=%s" % (search_type, column, code)
        else:
            search_key = "%s?project=%s&%s=%s" % (search_type, project_code, column, code)
        return search_key
    build_search_key = classmethod(build_search_key)

    def extract_search_type(cls, search_key):
        try:
            search_type, tmp = search_key.split("&", 1)
        except:
            search_type = cls.extract_base_search_type(search_key)

        return search_type
    extract_search_type = classmethod(extract_search_type)



    def _get_data(cls, search_key):
        data = {}
        if search_key.find("?") == -1:
            if search_key.startswith("sthpw/"):
                data['project'] = 'sthpw'

            return search_key, data

        base_search_type, specifics = search_key.split("?")
        exprs = specifics.split("&")

        for expr in exprs:
            name, value = expr.split("=")
            data[name] = value

        project = data.get("project")
        if project:
            search_type = "%s?project=%s" % (base_search_type, project)
        else:
            search_type = base_search_type

        data["search_type"] = search_type
        data["base_search_type"] = base_search_type


        return base_search_type, data
    _get_data = classmethod(_get_data)


    def extract_base_search_type(cls, search_key):
        base_search_type, data = cls._get_data(search_key)
        return base_search_type
    extract_base_search_type = classmethod(extract_base_search_type)


    def extract_database(cls, search_key):
        base_search_type, data = cls._get_data(search_key)
        return data.get("db")
    extract_database = classmethod(extract_database)


    def extract_project(cls, search_key):
        base_search_type, data = cls._get_data(search_key)
        return data.get("project")
    extract_project = classmethod(extract_project)


    def extract_code(cls, search_key):
        base_search_type, data = cls._get_data(search_key)
        return data.get("code")
    extract_code = classmethod(extract_code)


    def extract_id(cls, search_key):
        base_search_type, data = cls._get_data(search_key)
        return data.get("id")
    extract_id = classmethod(extract_id)



 
    def get_by_search_key(search_key):
        if not search_key:
            return None

        # fix this as a precaution ... if appears from xml occasionally
        while search_key.find("&amp;") != -1:
            search_key = search_key.replace("&amp;", "&")

        if search_key.find("|") == -1:
            if search_key.find("?") == -1:
                raise SearchException("Improper search_key format for [%s]" % search_key)

            search_type, search_expr = search_key.split("?")

            name_value_pairs = search_expr.split("&")
            data = {}
            try:
                for name_value_pair in name_value_pairs:
                    name, value = name_value_pair.split("=")
                    data[name] = value
            except ValueError as e:
                raise SearchException('Badly formatted search key found [%s]'%search_key)
            if search_type.startswith("sthpw/"):
                old_search_type = search_type
            else:
                old_search_type = "%s?project=%s" % (search_type, data['project'] )

            if data.get('id') == '-1':
                sobject = SearchType.create(old_search_type)
                return sobject

            search = Search(old_search_type)
            if data.get('code'):
                search.add_filter("code", data['code'] )
            elif data.get('id'):
                id_col = search.get_id_col()
                search.add_filter(id_col, data['id'] )
            else:
                raise SearchException("Malformed search_key [%s] in search" % search_key)

            search.set_show_retired(True)
            sobject = SObject.get_by_search(search, search_key)            
            return sobject
        else:
            # use the old way
            search_type, search_id = search_key.split("|")
            return Search.get_by_id(search_type, search_id)
    get_by_search_key = staticmethod(get_by_search_key)


    def build_by_sobject(cls, sobject, use_id=False):
        return cls.get_by_sobject(sobject, use_id=use_id)
    build_by_sobject = classmethod(build_by_sobject)


    def get_by_sobject(cls, sobject, use_id=False):
        search_type = sobject.get_base_search_type()
        if isinstance(sobject, SearchType):
            search_type = "sthpw/search_object"

        from pyasm.biz import Project
        if isinstance(sobject, Project):
            project_code = sobject.get_code()
        elif isinstance(sobject, SearchType):
            project_code = None
        else:
            project_code = sobject.get_project_code()
        # this is done like this till sthpw/task's code is working
        code = sobject.get_value('code', no_exception=True)
        if not use_id and code:
            return cls.build_search_key(search_type, code, project_code=project_code)
        else:
            id = sobject.get_id()
            return cls.build_search_key(search_type, id, column='id', project_code=project_code)
    get_by_sobject = classmethod(get_by_sobject)




    def get_by_sobjects(cls, sobjects, use_id=False):
        if not sobjects:
            return []

        sobject = sobjects[0]

        # if sobject is none, then this function will not work.
        # Not sure if this is the right response
        if not sobject:
            return [None for x in sobjects]

        search_type = sobject.get_base_search_type()
        if isinstance(sobject, SearchType):
            search_type = "sthpw/search_object"

        from pyasm.biz import Project
        if isinstance(sobject, Project):
            project_code = sobject.get_code()
        elif isinstance(sobject, SearchType):
            project_code = None
        else:
            project_code = sobject.get_project_code()

        search_keys = []
        for sobject in sobjects:

            if not sobject:
                search_keys.append(None)
                continue

            code = sobject.get_value('code', no_exception=True)
            if not use_id and code:
                search_key = cls.build_search_key(search_type, code, project_code=project_code)
            else:
                id = sobject.get_id()
                search_key = cls.build_search_key(search_type, id, column='id', project_code=project_code)

            search_keys.append(search_key)

        return search_keys
    get_by_sobjects = classmethod(get_by_sobjects)


 
    def get_by_search_keys(cls, search_keys, keep_order=False):
        '''get all the sobjects in a more effective way, assuming same search_type'''

        if not search_keys:
            return []


        if isinstance(search_keys, basestring):
            search_keys = search_keys.split(",")

        search_type_list = []
        search_code_list = []
        search_id_list = []
        for sk in search_keys:

            # fix this as a precaution ... if appears from xml occasionally
            while sk.find("&amp;") != -1:
                sk = sk.replace("&amp;", "&")

            search_type_list.append(SearchKey.extract_search_type(sk))
            code = SearchKey.extract_code(sk)
            if code:
                search_code_list.append(code)
            else:
                id = SearchKey.extract_id(sk)
                # convert to a string for ocmparison
                id = str(id)
                search_id_list.append(id)
       
        single_search_type = False
        if len(Common.get_unique_list(search_type_list)) == 1:
            single_search_type=True
        if single_search_type:
            if search_code_list and len(search_keys)==len(search_code_list):
                sobjs = Search.get_by_code(search_type_list[0], search_code_list)
                if keep_order:
                    sort_dict = {}
                    for sobj in sobjs:
                        sobj_code = sobj.get_code()
                        sort_dict[sobj] = search_code_list.index(sobj_code)
                    sorted_sobjs = sorted(sobjs, key=sort_dict.__getitem__)
                    return sorted_sobjs
                else:
                    return sobjs
            elif search_id_list and len(search_keys)==len(search_id_list):
                sobjs = Search.get_by_id(search_type_list[0], search_id_list)
                if keep_order:
                    sort_dict = {}
                    for sobj in sobjs:
                        sobj_id = str(sobj.get_id())
                        sort_dict[sobj] = search_id_list.index(sobj_id)
                    sorted_sobjs = sorted(sobjs, key=sort_dict.__getitem__)
                    return sorted_sobjs
                else:
                    return sobjs
            else:
                raise SetupException('A mixed code and id search keys detected.')
        else:
            # multiple sTypes, rearrange them first in order
            search_key_dict = {}
            for sk in search_keys:
                search_type = SearchKey.extract_search_type(sk)
                search_key_list = search_key_dict.get(search_type)
                if search_key_list == None:
                    search_key_dict[search_type] = [sk]
                else:
                    search_key_list.append(sk)
                
            results = []
            for key, sk_list in search_key_dict.items():
                result = SearchKey.get_by_search_keys(sk_list, keep_order=keep_order)
                results.extend(result)
            return results
                
            #raise SetupException('Single search type expected.')
    get_by_search_keys = classmethod(get_by_search_keys)


# use psyco if present
try:
    import psyco
    psyco.bind(Search.do_search)
    psyco.bind(SearchType.create)
except ImportError:
    pass



