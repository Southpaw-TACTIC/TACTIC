###########################################################
#
# Copyright (c) 2013, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


import tacticenv

from pyasm.security import Batch
from pyasm.biz import Project
from pyasm.search import SearchType, SObject, Update, Insert, Search, DbContainer


from pyasm.unittest import UnittestEnvironment

import unittest

class SqlTest(unittest.TestCase):


    def test_all(my):

        #test_env = UnittestEnvironment()
        #test_env.create()

        try:
            my._create_table()
            my._test_search()

        finally:
            #test_env.delete()
            pass




    def _create_table(my):

        from pyasm.search import CreateTable

        project = Project.get_by_code("mongodb")
        #sql = project.get_sql()
        db_resource = project.get_project_db_resource()
        sql = db_resource.get_sql()
    
        create = CreateTable()
        create.set_table("whatever")

        create.commit(sql)




    def _test_search(my):

        # test search
        search = Search("table/posts?project=mongodb")
        sobject = search.get_sobject()
        my.assertNotEquals(None, sobject)

        sobjects = search.get_sobjects()
        #for sobject in sobjects:
        #    print sobject.get_value("_id"), sobject.get_value("author")


        # test simple filter
        search = Search("table/posts?project=mongodb")
        search.add_filter("author", "Mike")
        sobjects = search.get_sobjects()
        for sobject in sobjects:
            my.assertEquals("Mike", sobject.get_value("author") )


        # do an update
        sobject = sobjects[0]
        sobject.set_value("text", "This is wonderful!!!")
        sobject.commit()

        # search by id
        object_id = sobject.get_id()
        updated_sobject = Search.get_by_id("table/posts?project=mongodb", object_id)
        my.assertNotEquals(None, updated_sobject)
        my.assertEquals("This is wonderful!!!", updated_sobject.get_value("text"))






        # search by search_key
        search_key = sobject.get_search_key()
        test_sobject = Search.get_by_search_key(search_key)
        print "search_key: ", search_key
        print "test: ", test_sobject.get_data()
        my.assertNotEquals(None, test_sobject)




        # create a new one
        sobject = SearchType.create("table/posts?project=mongodb")
        sobject.set_value("author", "Cindy")
        sobject.set_value("text", "My second blog post!")
        sobject.set_value("tags", ["mongodb", "python", "pymongo"])
        sobject.commit()

        return


        print "---"
        count = search.get_count()
        print "count: ", count


        search.add_order_by("author")
        sobjects = search.get_sobjects()
        for sobject in sobjects:
            print sobject.get_value("_id"), sobject.get_value("author")


        print "---"

        search = Search("table/posts?project=mongodb")
        search.add_order_by("author")
        search.add_filter("author", "Fred", op=">")
        sobjects = search.get_sobjects()
        for sobject in sobjects:
            print sobject.get_value("_id"), sobject.get_value("author")



    
if __name__ == "__main__":
    Batch()
    unittest.main()



