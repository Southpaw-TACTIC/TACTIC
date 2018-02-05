###########################################################
#
# Copyright (c) 2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['DbIntrospect']

import tacticenv

from pyasm.common import Common
from pyasm.search import Search, SearchType, DbResource, DbContainer


class DbIntrospect(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.db_resources = {}


    def get_db_resource(self, name):
        return self.db_resources.get(name)


    def register(self, name, db_resource, tables=None):

        db_name = db_resource.get_database()

        project_code = "db_resource/%s" % db_name

        # create a virtual project
        project = SearchType.create("sthpw/project")
        # FIXME: what is this conflicts with an existing project
        project.set_value("code", project_code)
        project.set_value("db_resource", db_resource)

        # put this sobject into the cache
        from pyasm.biz import Project
        key = "sthpw/project|%s" % project_code
        Project.cache_sobject(key, project)



        if tables == None:
            # introspect and resister all of the tables
            sql = DbContainer.get(db_resource)
            table_info = sql.get_table_info()

            if table_info.get("spt_search_type"):
                print "has search_type"

            tables = table_info.keys()


        for table in tables:

            # FIXME: how is this created
            search_type = "table/%s?project=%s" % (table, db_name)

            #search_type_obj = SearchType.create("config/search_type")
            search_type_obj = SearchType.create("sthpw/search_type")
            search_type_obj.set_value("search_type", "table/%s" % table)
            search_type_obj.set_value("title", Common.get_display_title(table) )
            search_type_obj.set_value("table_name", table)
            search_type_obj.set_value("database", db_name)

            SearchType.set_virtual(search_type, search_type_obj)



        self.db_resources[name] = db_resource



def execute(db_resource):

    # This works if there is a project set up already with the appropriate
    # db_resource.
    search_type = "table/foofoo?project=db2_test"
    search_type_obj = SearchType.get(search_type)
    search = Search(search_type)
    sobjects = search.get_sobjects()
    print "length: ", len(sobjects)


    # or (note that there is no project here).  The two arguments
    # are sufficient to determine a search.  Here we want to just "casually"
    # connect to a separate database resource.
    table = 'foofoo'
    search = db_resource.get_search(table)
    sobjects = search.get_sobjects()
    print "length: ", len(sobjects)
    for sobject in sobjects:
        print sobject.get_code(), sobject.get_value("description")


    table = 'widget_config'
    search = db_resource.get_search(table)
    sobjects = search.get_sobjects()
    print "length: ", len(sobjects)
    for sobject in sobjects:
        print sobject.get_code(), sobject.get_value("config")



    db_resource = DbResource(vendor="MySQL", database="fifi", user="root")
    introspect = DbIntrospect()
    introspect.register("fifi", db_resource)
    table = 'cards'
    search = db_resource.get_search(table)
    sobjects = search.get_sobjects()
    print "length: ", len(sobjects)
    for sobject in sobjects:
        print sobject.get_code(), sobject.get_value("description")


    print "sqlite: transaction_log"
    db_resource = DbResource.get_by_code('sqlite','sthpw')
    introspect = DbIntrospect()
    introspect.register("sqlite", db_resource)
    search = db_resource.get_search("transaction_log")
    sobjects = search.get_sobjects()
    print "length: ", len(sobjects)



    print "selfsql: fifi"
    db_resource = DbResource.get_by_code('mysql','fifi')
    introspect = DbIntrospect()
    introspect.register("fifi", db_resource)
    search = db_resource.get_search("cards")
    sobjects = search.get_sobjects()
    print "length: ", len(sobjects)


    print "selfsql: fifi"
    search_type = "table/node0?project=db3_test"
    search = Search(search_type)
    sobjects = search.get_sobjects()
    print "length: ", len(sobjects)





 


if __name__ == '__main__':

    from pyasm.security import Batch
    Batch(project_code="project")

    # register this resource
    db_resource = DbResource(vendor="MySQL", host="localhost", database="db2_test", user="root")

    # auto register all of the tables there
    introspect = DbIntrospect()
    import time
    start = time.time()
    introspect.register("db2_test", db_resource)
    print "time: ", time.time() - start

    execute(db_resource)


