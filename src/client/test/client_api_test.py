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


__all__ = ['ClientApiTest']

import tacticenv
import re

import unittest
import getpass
import xmlrpclib, sys, os, shutil

import imp
md5_path = "%s/src/bin/get_md5.py" % tacticenv.get_install_dir()
get_md5 = imp.load_source('get_md5', md5_path)

from pyasm.common import Xml,TacticException, Config
from pyasm.security import Batch
from pyasm.checkin import CheckinException
from pyasm.search import SObject
from pyasm.security import Batch
from pyasm.biz import Project
from pyasm.prod.service import ApiException
from pyasm.unittest import UnittestEnvironment


class ClientApiTest(unittest.TestCase):

    def test_all(my):
        Batch()
        UnittestEnvironment().create()
        Project.set_project("unittest")
        try:
            my._test_all()
        finally:
            UnittestEnvironment().delete()



    def _test_all(my):
        print "Running Client API Test"

        # There are actually a number of main tests here
        # 1. client api test
        # 2. client api abort test
        # 3. client api error test
        # 4. local using api test
        # 5. post abort query test
        
        # import the client lib
        install_dir = tacticenv.get_install_dir()
        
        my.client_lib_dir = "%s/src/client" % install_dir
        sys.path.insert( 0, my.client_lib_dir )
        from tactic_client_lib import TacticServerStub

        # set the server to test... assume it is run on the server
        server = "localhost"
        url = "http://%s/tactic/default/Api/" % server


        my.server = TacticServerStub()
        project_code = "unittest"
        my.server.set_project(project_code)
        # test getting a ticket
        test_ticket = ''
        try:
            test_ticket = my.server.get_ticket('admin', 'tactic')
        except Exception, e:
            try:
                import getpass
                password = getpass.getpass("Enter TACTIC Password -> ")
                test_ticket = my.server.get_ticket('admin', password)
            except Exception, e:
                x = e.__str__().find("Login/Password combination incorrect") == -1
                my.assertEquals(False, x, e.__str__() )
        
        
        my.server.set_ticket(test_ticket)		
        description = "run 10 or more tests"		
        my.server.start("Client API Unittest", description)		
		

        # test basic functionality in a transaction.  A new ticket is		
        # generated which is used to append to the transaction.
	 
        try:
            
            people = my.server.query("unittest/person")
            for person in people:
                my.server.delete_sobject(person.get('__search_key__') )

            
            #my._test_widget()
            my._test_version()

            my._test_get_related()
            my._test_build_search_key()
            my._test_resource_paths()
            my._test_build_search_type()
            my._test_instance()
            #my._test_missing_method()
            my._test_insert()
            my._test_insert_w_trigger()
            my._test_get_unique_sobject()
            my._test_simple()
            my._test_query()
            my._test_update()
            my._test_insert_multiple()
            my._test_update_multiple()
            my._test_insert_update()
            my._test_get_by_search_key()
            my._test_checkin()
            my._test_preallocate_checkin()
            my._test_level_checkin()
            my._test_checkin_with_handoff()
            my._test_group_checkin()
            my._test_directory_checkin()
            my._test_add_dependency()
            my._test_inplace_checkin()
            my._test_checkout()
            my._test_get_snapshot()
            my._test_get_paths()
            my._test_add_file()
            my._test_hierarchy()
            my._test_retire_delete()
            my._test_widget_config()
            my._test_pipeline()
            my._test_eval()
            my._test_execute()
            my._test_create_task()
            my._test_upload()
            my._test_check_access()
        except Exception:
            my.server.abort()
            raise
      
        # undo doesn't seem to work? or it's undoing the wrong project?
        #my.server.undo()
        my._test_local_protocol()
        my.server.abort()
        my.server.set_ticket(test_ticket)


        # test database only abort
        ticket = my.server.start("Client Api Abort Test")
        try:
            paths = []
            paths = my._test_database_only_abort()
            my.server.abort(ignore_files=True)

            # check that the files are still there
            for path in paths:
                my.assertEquals(True, os.path.exists(path))

        finally:
            for path in paths:
                if os.path.exists(path):
                    os.unlink(path)

 
        my.server.set_ticket(test_ticket)
        # test with an error
        my.server.start("Client Api Error Test")
        try:
            my._test_insert()
            my.server.test_error()
        except:
            my.server.abort()
 
        my.server.set_ticket(test_ticket)
        # person or city table must be empty now after abort
        my.server.start("Client API Unittest query after abort")
        try:
            my._test_empty_db()
        except:
            my.server.abort()

        else:
            my.server.finish()

        return

    def _test_database_only_abort(my):
        search_type = "unittest/person"

        # insert the first
        data = {
            'code': 'joe500',
            'name_first': 'Joe',
            'name_last': 'Smoe',
        }
        result = my.server.insert(search_type, data)
        search_key = result.get("__search_key__")

        # create a snapshot
        snapshot = my.server.create_snapshot(search_key, "test")
        snapshot_code = snapshot.get("code")


        file_type = 'sequence'
        file_name = "images_%0.4d.png"
        file_range = "1-5"
        path = my.server.get_preallocated_path(snapshot_code, file_type, file_name)
        # imitate a render by building files directly to the path
        for i in range(1,6):
            cur_path = path % i
            f = open(cur_path, 'wb')
            f.write("wowow")
            f.close()

        results = my.server.add_group(snapshot_code, path, file_type, file_range, mode='preallocate')

        snapshot_code = results.get('code')
        paths = my.server.get_expanded_paths_from_snapshot(snapshot_code, file_type)
        my.assertEquals( 5, len(paths))

        return paths

    def _test_simple(my):
        result = my.server.ping()
        my.assertEquals("OK", result)


    # DEPRECATED
    def _test_instance(my):
        '''Test instance support'''
        return
        instance_type = "unittest/person_car_instance"
        # it's been reversed
        from_type, parent_type = my.server.get_types_from_instance(instance_type)

        my.assertEquals("unittest/car", parent_type)
        my.assertEquals("unittest/person", from_type)


    def _test_resource_paths(my):
        path = my.server.get_resource_path('admin')
        # not a very accurate test
        my.assertEquals(True, 'etc/admin.tacticrc' in  path)

        paths = my.server.create_resource_paths()
        sys_login = getpass.getuser()
        dir = my.server.get_home_dir()
        is_dir_writeable = os.access(dir, os.W_OK) and os.path.isdir(dir)
        if dir and is_dir_writeable:
            dir = "%s/.tactic/etc" % dir
        else:
            if os.name == 'nt':
                dir = 'C:/sthpw/etc'
            else:
                dir = '/tmp/sthpw/etc'
        compared = '%s/%s.tacticrc' %(dir, sys_login) in paths
        my.assertEquals(True, compared)

        # since we use admin to get resource path , my.login should also be admin
        my.assertEquals('admin', my.server.get_login())

    def _test_build_search_type(my):
        search_type = "unittest/city"
        built = my.server.build_search_type(search_type)
        my.assertEquals("unittest/city?project=unittest", built)

        my.server.set_project('sample3d')
        built = my.server.build_search_type(search_type)
        my.assertEquals("unittest/city?project=sample3d", built)


        built = my.server.build_search_type('sthpw/task')
        my.assertEquals("sthpw/task", built)

        my.server.set_project('unittest')

    def _test_insert(my):
        '''Test an individual insert of a person and undo'''

        search_type = "unittest/person"

        # insert the first
        data = {
            'code': 'joe',
            'name_first': 'Joe',
            'name_last': 'Smoe',
        }
        info = {'person': 'legal personnel'}
        result = my.server.insert(search_type, data, info=info)
        my.assertEquals('Joe', result.get('name_first'))


        # insert the second
        data = {
            'code': 'mary',
            'name_first': 'Mary',
            'name_last': 'Smary',
        }
        result = my.server.insert(search_type, data)
        my.assertEquals('Mary', result.get('name_first'))

    def _test_insert_w_trigger(my):
        # insert a trigger
        triggers = my.server.query('config/trigger', filters=[('event','insert|unittest/city')])
        if triggers:
            raise TacticException('Delete your existing trigger for unittest project insert|unittest/city')

        data = {'event': 'insert|unittest/city',
                'mode': 'same process,same transaction',
                'class_name': 'pyasm.unittest.UnittestTrigger'}
        
        my.server.insert('config/trigger', data, triggers=False)

        # insert a city with a trigger to fire
        data = {'code': 'seoul', 'country_code': 'korea'}
        my.server.insert('unittest/city', data, triggers=True)

        result = my.server.get_by_search_key('unittest/city?project=unittest&code=incheon')
        my.assertEquals('incheon', result.get('code'))
        # since it is coming from a same p, same t trigger, it will be removed
        # at the end automatically
        



    def _test_get_unique_sobject(my):
        '''Test an individual insert of a person and undo'''

        search_type = "unittest/person"
        query_results = my.server.query(search_type, filters=[('code','mike')])
        my.assertEquals(0, len(query_results))


        # insert the first
        data = {
            'code': 'mike',
            'name_first': 'Mike',
            'name_last': 'Brown',
        }
        result = my.server.get_unique_sobject(search_type, data)
        query_results = my.server.query(search_type, filters=[('code','mike')])
        my.assertEquals(1, len(query_results))
        
        my.assertEquals('Mike', result.get('name_first'))
        my.assertEquals('Brown', result.get('name_last'))

        # no insert this time
        result = my.server.get_unique_sobject(search_type, data)
        query_results = my.server.query(search_type, filters=[('code','mike')])
        my.assertEquals(1, len(query_results))

        my.assertEquals('Mike', result.get('name_first'))
        my.assertEquals('Brown', result.get('name_last'))

    def _test_query(my):

        search_type = "unittest/person"

        # try single search
        filters = []
        filters.append( ("name_first", "Joe") )
        columns = ['id', 'name_first', 'name_last']
        results = my.server.query(search_type, filters, columns)
        my.assertEquals( 1, len(results) )
        name_first = results[0]['name_first']
        my.assertEquals('Joe', name_first)

        # since columns is 3, the total length is 4 with __search_key__
        my.assertEquals(4, len(results[0]))
        name_last = results[0]['name_last']
        my.assertEquals('Smoe', name_last)

        columns = ['name_first']
        results = my.server.query(search_type, filters, columns)
        my.assertEquals(2, len(results[0]))

        # FIXME: pretty big assumption on number of columns here!!
        # if columns is empty, return everything 14 + __search_key__
        #columns = []
        #results = my.server.query(search_type, filters, columns)
        #my.assertEquals(15, len(results[0]))

        # try search with 'and': where name_first = 'Joe' and name_last = 'Smoe'
        filters = []
        filters.append( ("name_first", "Joe") )
        filters.append( ("name_last", "Smoe") )
        results = my.server.query(search_type, filters, columns)
        my.assertEquals( 1, len(results) )


        # try search with 'or': where code in ('joe','mary')
        filters = []
        filters.append( ("code", ("joe", "mary")) )
        results = my.server.query(search_type, filters, columns)
        my.assertEquals( 2, len(results) )


        # try search with 'or': where code in ('joe','mary') order by code
        filters = []
        filters.append( ("code", ("joe", "mary")) )
        order_bys = ['name_first']

        results = my.server.query(search_type, filters, columns, order_bys)
        my.assertEquals( 2, len(results) )
        my.assertEquals( 'Joe', results[0].get('name_first'))

        order_bys = ['name_first desc']
        # order by descending
        results = my.server.query(search_type, filters, columns, order_bys)
        my.assertEquals( 'Mary', results[0].get('name_first'))

        # try search with like: where code like 'j%'
        filters = []
        filters.append( ("code", "like", "j%") )
        results = my.server.query(search_type, filters, columns)
        my.assertEquals( 1, len(results) )
        name_first = results[0]['name_first']
        my.assertEquals('Joe', name_first)


        # try with cross-db regular expression: code ~ 'ma'
        filters = []
        filters.append( ("code", "EQ", "ma") )
        results = my.server.query(search_type, filters, columns)
        my.assertEquals( 1, len(results) )
        name_first = results[0]['name_first']
        my.assertEquals('Mary', name_first)

        # try with regular expression: code EQ 'ma'
        filters = []
        filters.append( ("code", "EQ", "ma") )
        results = my.server.query(search_type, filters, columns)
        my.assertEquals( 1, len(results) )
        name_first = results[0]['name_first']
        my.assertEquals('Mary', name_first)

    
        # try with regular expression: code !~ 'ma'
        filters = []
        filters.append( ("code", "NEQ", "ma") )
        results = my.server.query(search_type, filters, columns)
        for result in results:
            name_first = result['name_first']
            my.assertNotEquals('Mary', name_first)

        # try with cross-db regular expression: code NEQI 'ma'
        filters = []
        filters.append( ("code", "NEQI", "ma") )
        results = my.server.query(search_type, filters, columns)
        for result in results:
            name_first = result['name_first']
            my.assertNotEquals('Mary', name_first)

        # test using limit and offset
        search_type = "unittest/person"
        order_bys = ['code']
        filters = []
        filters.append( ("code", ("joe", "mary")) )
        results = my.server.query(search_type, filters=filters, order_bys=order_bys, limit=1)
        my.assertEquals( 1, len(results) )
        my.assertEquals( 'joe', results[0].get('code') )

        results = my.server.query(search_type, filters=filters, order_bys=order_bys, offset=1, limit=1)
        my.assertEquals( 1, len(results) )
        my.assertEquals( 'mary', results[0].get('code') )


        # try single search something that doesn't exist
        filters = []
        filters.append( ("name_first", "Joey") )
        results = my.server.query(search_type, filters)
        my.assertEquals( 0, len(results) )

       

    def _test_local_protocol(my):
        from pyasm.security import Batch
        from tactic_client_lib import TacticServerStub
        batch = Batch('admin')
        Project.set_project('unittest')
        my.local_server = TacticServerStub(protocol='local')
        my.local_server.set_project('unittest')
        my.local_server.start('local test')

        # try single search and return_sobjects
        filters = []
        filters.append( ("name_first", "Mary") )
        result = my.local_server.query('unittest/person', filters, single=True, return_sobjects=True)
        my.assertEquals( True, isinstance(result, SObject) )
        my.assertEquals( 'Smary', result.get_value('name_last'))
        my.local_server.finish()

    def _test_empty_db(my):
        results = my.server.query('unittest/person', filters=[], columns=['id'])
        my.assertEquals( 0, len(results))


    def _test_eval(my):
        results = my.server.eval("@GET(sthpw/login['login','admin'].login)", single=True)
        my.assertEquals('admin', results)

        results = my.server.eval("@GET(sthpw/login['login','admin'].login)")
        my.assertEquals(['admin'], results)

        results = my.server.eval("@FORMAT('-35.678','-$1,234.00')")
        try:
            my.assertEquals(['-$35.68'], results)
        except:
            my.assertEquals(['($35.68)'], results)
            

        results = my.server.eval("@FORMAT('-35.678','-$1,234.00')", single=True)
        try:
            my.assertEquals('-$35.68', results)
        except:
            my.assertEquals('($35.68)', results)

    def _test_execute(my):
        script_entry = {'folder': 'uni', 'title':'unittest_script', 'script': 'print x;\nprint y;\nreturn x;'}

        my.server.insert('config/custom_script', script_entry)
        results = my.server.execute_python_script("uni/unittest_script", kwargs = {'x':5, 'y':6})
        my.assertEquals(5, results['info']['spt_ret_val'])



    def _test_get_related(my):
        results = my.server.get_related_types('unittest/person')
        my.assertEquals(['unittest/city', 'unittest/car', 'unittest/country', 'unittest/person_in_car'], results)
        results = my.server.get_related_types('unittest/country')
        my.assertEquals(['unittest/city','unittest/person'], results)


    def _test_update(my):
        '''update the person'''

        # test single update
        search_type = "unittest/person"
        code = "joe"
        search_key = my.server.build_search_key(search_type, code)

        data = {'nationality': 'WonderLand'}
        info = {'person': 'legal personnel'}

        result = my.server.update(search_key, data, info=info)
        my.assertEquals("WonderLand", result.get("nationality") )

        # test setting a value to NULL. have to use '' instead
        data = {'nationality': ''}
        result = my.server.update(search_key, data)
        my.assertEquals('', result.get("nationality") )


        # test multi-update
        data = {'nationality': 'FooLand'}

        search_type2 = "unittest/person"
        code2 = "mary"
        search_key2 = my.server.build_search_key(search_type2, code2)

        search_keys = [search_key, search_key2]

        results = my.server.update(search_keys, data)
        my.assertEquals( 2, len(results) )
        for result in results:
            my.assertEquals("FooLand", result.get("nationality") )
            

        # test multi-update with multi-data
        datas = [   {'nationality': 'WonderLand'},
                    {'nationality': 'FooLand'} ]
        results = my.server.update(search_keys, datas)
        my.assertEquals( 2, len(results) )
        my.assertEquals( 'WonderLand', results[0].get('nationality') )
        my.assertEquals( 'FooLand', results[1].get('nationality') )

        # test metadata
        metadata = {
            'color': 'blue',
            'weight': '68Kg',
            'height': '183cm'
        }
        results = my.server.update(search_keys, datas, metadata=metadata)
        metadata = results[0].get('metadata')
        my.assertEquals( '183cm', metadata.get('height'))
        my.assertEquals( '68Kg', metadata.get('weight'))

    def _test_insert_multiple(my):
        '''update multiple persons'''

        # test single update
        search_type = "unittest/city"
        code1 = "red deer"

        data1 = {'name': 'Canadian', 'code': code1}

        metadata1 = {'color':'purple', 'cost': '5000'}
        

        code2 = "seattle"
        data2 = {'name': 'West Canadian', 'code': code2}
        metadata2 = {'color':'orange', 'cost': '7000'}


        data = [data1, data2]
        metadata = [metadata1, metadata2]
        results = my.server.insert_multiple(search_type, data, metadata=metadata)
        my.assertEquals( 2, len(results) )
        check = [False, False]
        for result in results:
            if result.get('code') == 'red deer':
                my.assertEquals("Canadian", result.get("name") )
                meta = result.get('metadata')
                my.assertEquals('purple', meta.get('color'))
                check[0] = True
            elif result.get('code') == 'seattle':
                my.assertEquals("West Canadian", result.get("name") )
                meta = result.get('metadata')
                my.assertEquals('7000', meta.get('cost'))
                check[1] = True
      
        my.assertEquals( [True, True], check )

    def _test_update_multiple(my):
        '''update multiple persons'''

        # test single update
        search_type = "unittest/person"
        code = "joe"
        search_key = my.server.build_search_key(search_type, code)

        data = {'nationality': 'WonderLand'}
        
        update_data = {search_key: data}

        # test multi-update
        data = {'nationality': 'FooLand'}

        search_type2 = "unittest/person"
        code2 = "mary"
        search_key2 = my.server.build_search_key(search_type2, code2)

        update_data[search_key2] = data
        search_keys = [search_key, search_key2]

        results = my.server.update_multiple(update_data)
        my.assertEquals( 2, len(results) )
        for result in results:
            if result.get('code') == 'mary':
                my.assertEquals("FooLand", result.get("nationality") )
            elif result.get('code') == 'joe':
                my.assertEquals("WonderLand", result.get("nationality") )
            

      
        my.assertEquals( 2, len(results) )

     

    def _test_insert_update(my):
        '''test an insert or update the person'''
        # test on one that already exists
        search_type = "unittest/person"
        code = "joe"
        search_key = my.server.build_search_key(search_type, code)

        data = { 'name_last': 'smith' }
        person = my.server.insert_update(search_key, data)
        my.assertEquals("smith", person.get('name_last') )

        # test a new person
        search_type = "unittest/person"
        code = "cindy"
        search_key = my.server.build_search_key(search_type, code)
        data = { 'name_last': 'boisclair' }
        person = my.server.insert_update(search_key, data)
        my.assertEquals("boisclair", person.get('name_last') )
       


    def _test_get_by_search_key(my):
        '''Simple function the tests getting an sobject by search key'''
        search_type = "unittest/person"
        code = "joe"
        search_key = my.server.build_search_key(search_type, code)
        sobject = my.server.get_by_search_key(search_key)
        sobject_code = sobject.get("code")

        my.assertEquals(code, sobject_code)




    def _test_checkin(my):
        # upload a file
        file_path = "%s/test/miso_ramen.jpg" % my.client_lib_dir

        my.server.upload_file(file_path)

        # now check in the file
        search_type = "unittest/person"
        code = "joe"
        context = "test_checkin"
        search_key = my.server.build_search_key(search_type, code)
        # simple checkin of a file.  No dependencies
        desc = 'A Simple Checkin'
        info = {'person': 'legal personnel'}

        result = my.server.simple_checkin(search_key, context, file_path, description=desc, info=info)
        
        # No real test needed here.  If it failed, it will stack trace
        my.assertNotEquals(result, None)

        snapshot_code = result.get("code")
        my.assertEquals(1, result.get("version") )
        
        snapshot_description = result.get("description")
        my.assertEquals(snapshot_description, desc)

        # get the filename
        file_type = "main"
        path = my.server.get_path_from_snapshot(snapshot_code, file_type, mode='client_repo')

        exists = os.path.exists(path)
        my.assertEquals(True, exists)

        # check that the file name is correct
        filename = os.path.basename(path)
        server = Config.get_value("install", "server")
        if server:
            my.assertEquals("miso_ramen_test_checkin_%s_v001.jpg" % server, filename)
        else:
            my.assertEquals("miso_ramen_test_checkin_v001.jpg", filename)


        # get all the filename
        paths = my.server.get_all_paths_from_snapshot(snapshot_code)
        for path in paths:
            exists = os.path.exists(path)
            my.assertEquals(True, exists)


        # simple checkin of a file with file_type.  No dependencies
        my.server.upload_file(file_path)
        result = my.server.simple_checkin(search_key, context, file_path, file_type="foo")
        # No real test needed here.  If it failed, it will stack trace
        my.assertNotEquals(result, None)

        my.assertEquals(True, result.get("is_current") )
        my.assertEquals(2, result.get("version") )


        # do another checkin, but with currency set off
        my.server.upload_file(file_path)
        result = my.server.simple_checkin(search_key, context, file_path, file_type="foo", is_current=False)

        my.assertNotEquals(True, result.get("is_current") )
        my.assertEquals(3, result.get("version") )

        # do another checkin, but leaving a breadcrumb
        my.server.upload_file(file_path)
        result = my.server.simple_checkin(search_key, context, file_path, file_type="foo", is_current=False, breadcrumb=True)

        
        breadcrumb_file = "%s.snapshot" % file_path
        my.assertEquals( True, os.path.exists(file_path) )
        # remove it
        os.unlink(breadcrumb_file)

        # test create an empty snapshot
        snapshot = my.server.create_snapshot(search_key, "test_empty")
        my.assertEquals("<snapshot/>", snapshot.get('snapshot') )
        my.assertEquals(1, snapshot.get('version') )


        # simple checkin of a file adding arbitrary metadata
        my.server.upload_file(file_path)
        context = 'metadata'
        metadata = {
            'color': 'blue',
            'weight': '68Kg',
            'height': '183cm'
        }
        result = my.server.simple_checkin(search_key, context, file_path, metadata=metadata)
        # No real test needed here.  If it failed, it will stack trace
        my.assertNotEquals(result, None)

        # get the latest version
        version = -1
        snapshot = my.server.get_snapshot(search_key, context, version)
        metadata = snapshot.get("metadata")
        my.assertEquals('blue', metadata.get('color'))

        # update metadata through data
        data = { 'metadata': {
                    'color': 'red', 
                    'speed': '165Km/h' }
               }

        snapshot = my.server.update( snapshot.get('__search_key__'), data )
        metadata = snapshot.get("metadata")
        my.assertEquals('red', metadata.get('color'))

        # update metadata through metadata argument
        metadata['color'] = 'orange'
        snapshot = my.server.update( snapshot.get('__search_key__'), metadata=metadata )
        metadata = snapshot.get("metadata")
        my.assertEquals('orange', metadata.get('color'))


        # test include paths
        snapshot = my.server.get_snapshot(search_key, context, "-1", include_paths=True, include_paths_dict=True)
        my.assertEquals( 3, len(snapshot.get('__paths__')) )

        my.assertEquals( 3, len(snapshot.get('__paths_dict__').keys()) )

        # test versionless
        versionless_snapshot = my.server.get_snapshot(search_key, context, -1, include_paths=True, include_paths_dict=True, versionless=True)
        paths_dict = versionless_snapshot.get('__paths_dict__')

        asset_dir = my.server.get_base_dirs().get('asset_base_dir')
        my.assertEquals(paths_dict.get('main') , ['%s/unittest/person/joe/metadata/miso_ramen_metadata.jpg'%asset_dir])
        #my.assertEquals( {}, versionless_snapshot)
        versionless_snapshot = my.server.get_snapshot(search_key, context, 0, include_paths=True, include_paths_dict=True, versionless=True)
        my.assertEquals( {}, versionless_snapshot)
        
        

        # test querying of snapshots
        filters = [['context', 'metadata']]
        snapshots = my.server.query_snapshots(filters=filters, include_paths=True, include_parent=True, include_files=True)
        # the 2nd one is the versionless one auto-created.
        # now back to '' checkin_type as default in 4.2 
        my.assertEquals( 2, len(snapshots))
        my.assertEquals( 3, len(snapshots[0].get('__paths__')) )

        my.assertEquals( "joe",  snapshots[0].get('__parent__').get('code'))

        # check the file object that are included
        files = snapshots[0].get('__files__')
        my.assertEquals( 3, len(snapshots[0].get('__files__')) )





    def _test_checkin_with_handoff(my):

        search_type = "unittest/person"
        code = "joe"
        search_key = my.server.build_search_key(search_type, code)

        # copy file to handoff dir
        path = "%s/test/miso_ramen.jpg" % my.client_lib_dir
        handoff_dir = my.server.get_handoff_dir()
        shutil.copy(path, handoff_dir)

        # check the file in
        snapshot = my.server.simple_checkin(search_key, "publish", path, use_handoff_dir=True)
        snapshot_code = snapshot.get("code")

        # get the filename
        file_type = "main"
        path = my.server.get_path_from_snapshot(snapshot_code, file_type)
        exists = os.path.exists(path)
        my.assertEquals(True, exists)

        # check that the file name is correct
        filename = os.path.basename(path)
        # changed naming.. adds "publish"
        my.assertEquals("miso_ramen_publish_v001.jpg", filename)


    def _test_group_checkin(my):
        # copy file to handoff dir
        file_path = "%s/test/images/miso_ramen.####.jpg" % my.client_lib_dir
        file_range = "1-5"

        # copy files to the handoff dir
        handoff_dir = my.server.get_handoff_dir()
        for i in range(1,6):
            file_name = "miso_ramen.%0.4d.jpg" % i
            expanded_path = "%s/test/images/%s" % (my.client_lib_dir, file_name)
            to_path = "%s/%s" % (my.client_lib_dir, handoff_dir)
            shutil.copy(expanded_path, handoff_dir)

        search_type = "unittest/person"
        code = "joe"
        search_key = my.server.build_search_key(search_type, code)

        context = "range_checkin"
        file_type="main"


        # do a group checkin
        desc = "A Group Checkin"
        result = my.server.group_checkin(search_key, context, file_path, file_type=file_type, file_range=file_range, description=desc)
        
        snapshot_description = result.get("description")
        my.assertEquals(snapshot_description, desc)

        # run it with mode='copy'
        file_range = "1-4"
        result = my.server.group_checkin(search_key, context, file_path, file_type=file_type, file_range=file_range, description=desc, mode='copy')
        snapshot_description = result.get("description")
        my.assertEquals(snapshot_description, desc)

    def _test_directory_checkin(my):
        search_type = "unittest/person"
        code = "joe"
        context = 'directory_checkin'
        search_key = my.server.build_search_key(search_type, code)

        # checkin directory of files
        dir = "%s/test/images" % my.client_lib_dir


        # 1.  checkin the directory
        mode = "copy"
        snapshot = my.server.directory_checkin(search_key, context, dir, mode=mode)
        snapshot_code = snapshot.get("code")

        # get all the filename and test they exist
        paths = my.server.get_all_paths_from_snapshot(snapshot_code)


        # asset that this is a directory
        my.assertEquals( True, os.path.isdir(paths[0]) )


        # 2. checkin directory of files with trailing /
        dir = "%s/test/images/" % my.client_lib_dir
        # checkin the directory
        mode = "copy"
        snapshot = my.server.directory_checkin(search_key, context, dir, mode=mode)
        snapshot_code = snapshot.get("code")

        # get all the filename and test they exist
        paths = my.server.get_all_paths_from_snapshot(snapshot_code)
        # asset that this is a directory
        my.assertEquals( True, os.path.isdir(paths[0]) )


    def _test_add_dependency(my):
        search_type = "unittest/person"
        code = "dan"
        search_key = my.server.build_search_key(search_type, code)


        # add another person

        data = {
            'code': 'dan',
            'name_first': 'Dan',
            'name_last': 'Kitchen',
        }
        info = {'person': 'commentator'}
        result = my.server.insert(search_type, data, info=info)
        context = "third"
        third_snapshot = my.server.create_snapshot(search_key, context)
        third_snapshot_code = third_snapshot.get('code')
        path ="%s/test/images/miso_ramen.0003.jpg" % my.client_lib_dir
        third_snapshot = my.server.add_file(third_snapshot_code, path, file_type='hp', mode='copy')
        

        search_type = "unittest/person"
        code = "joe"
        search_key = my.server.build_search_key(search_type, code)


        context = "upstream"
        up_snapshot = my.server.create_snapshot(search_key, context)
        up_snapshot_code = up_snapshot.get('code')


        up_snapshot = my.server.add_dependency_by_code(up_snapshot_code, third_snapshot_code)
        up_snapshot = my.server.add_dependency_by_code(up_snapshot_code, third_snapshot_code, tag='zz')
        all_dep_snapshots = my.server.get_all_dependencies(up_snapshot_code, include_paths=True)

        # this only gets tag='main', skipping tag='zz'
        dep_snapshots = my.server.get_dependencies(up_snapshot_code, include_files=True)
        my.assertEquals(2, len(all_dep_snapshots))
        my.assertEquals(1, len(dep_snapshots))

        # retired third snapshot
        rtn = my.server.retire_sobject(third_snapshot.get('__search_key__'))
        my.assertEquals( rtn.get('s_status'), 'retired')

        dep_snapshots = my.server.get_dependencies(up_snapshot_code, include_files=True, show_retired=False)
        all_dep_snapshots = my.server.get_all_dependencies(up_snapshot_code, include_paths=True, show_retired=False)
        my.assertEquals(0, len(all_dep_snapshots))
        my.assertEquals(0, len(dep_snapshots))
       
        all_dep_snapshots = my.server.get_all_dependencies(up_snapshot_code, include_paths=True, show_retired=True)
        my.assertEquals(2, len(all_dep_snapshots))

        

        # add a file in
        path = "%s/test/miso_ramen.jpg" % my.client_lib_dir
        path2 ="%s/test/images/miso_ramen.0005.jpg" % my.client_lib_dir
        up_snapshot = my.server.add_file(up_snapshot_code, path, file_type='blah', mode='upload')
        up_snapshot = my.server.add_file(up_snapshot_code, path2, file_type='blah2', mode='upload')

        # ensure that the path returned is empty
        ret_path = my.server.get_path_from_snapshot(up_snapshot_code)
        my.assertEquals("", ret_path)

        
        
        # ensure if the correct file_type is given, it can retrieve the corresponding file
        ret_path = my.server.get_path_from_snapshot(up_snapshot_code, file_type="blah2")
        ret_dir = my.server.get_client_dir(up_snapshot_code, file_type="blah2", mode='lib')
        ret_path_dir_portion = os.path.dirname(ret_path)
        my.assertEquals(ret_path_dir_portion, ret_dir)

        # ensure if the correct file_type is given, it can retrieve the corresponding file
        ret_path = my.server.get_path_from_snapshot(up_snapshot_code, file_type="blah")
        ret_dir = my.server.get_client_dir(up_snapshot_code, file_type="blah", mode='lib')
        ret_path_dir_portion = os.path.dirname(ret_path)
        my.assertEquals(ret_path_dir_portion, ret_dir)

        # ensure if None or '' is given to file_type, 
        # it can retrieve the dir of the first one automatically
        ret_dir = my.server.get_client_dir(up_snapshot_code, file_type=None, mode='lib')
        my.assertEquals(ret_path_dir_portion, ret_dir)
        
        context = "downstram"
        down_snapshot = my.server.create_snapshot(search_key, context)
        down_snapshot_code = down_snapshot.get('code')

        down_snapshot = my.server.add_dependency_by_code(down_snapshot_code, up_snapshot_code)
        my.assertEquals('search_code=' in down_snapshot.get('snapshot'), True)
        my.assertEquals(down_snapshot.get('search_code'), code)

        dep_snapshots = my.server.get_all_dependencies(down_snapshot_code, include_paths=True)
       
        paths = dep_snapshots[0].get('__paths__')

        base_dirs = my.server.get_base_dirs()
        linux_client_repo_dir = base_dirs.get('linux_client_repo_dir')
        if not linux_client_repo_dir:
            linux_client_repo_dir = base_dirs.get('asset_base_dir')

        if isinstance(linux_client_repo_dir, dict):
            linux_client_repo_dir = linux_client_repo_dir.get('default')

        my.assertEquals(1, len(dep_snapshots))
        my.assertEquals(2, len(paths))

        for path in paths:
            my.assertEquals(path.startswith('%s/unittest/person'%linux_client_repo_dir), True)
    
        dep_snapshots = my.server.get_all_dependencies(down_snapshot_code, include_paths=True, repo_mode='web')

        paths = dep_snapshots[0].get('__paths__')
        web_base_dir = base_dirs.get('web_base_dir')
        if isinstance(web_base_dir, dict):
            web_base_dir = web_base_dir.get('default')
        for path in paths:
            my.assertEquals(path.startswith('%s/unittest/person/'%web_base_dir), True)
    
        my.assertEquals(1, len(dep_snapshots))
        my.assertEquals(2, len(paths))


        my.assertEquals(dep_snapshots[0].get('code'), up_snapshot_code)


        # test levels with dependency
        city_search_type = "unittest/city"
        city_code = "toronto"
        city_search_key = my.server.build_search_key(city_search_type, city_code)

        context = "level"
        level_snapshot = my.server.create_snapshot(search_key, context, level_key=city_search_key)
        level_snapshot_code = level_snapshot.get('code')

        down_snapshot = my.server.add_dependency_by_code(down_snapshot_code, level_snapshot_code)

        dep_snapshots = my.server.get_all_dependencies(down_snapshot_code, include_files=True)
        my.assertEquals(2, len(dep_snapshots))
        my.assertEquals(dep_snapshots[1].get('code'), level_snapshot_code)


        # add a tagged dependency
        tag = 'whatever'
        down_snapshot = my.server.add_dependency_by_code(down_snapshot_code, up_snapshot_code, tag=tag)

        depend_snapshots = my.server.get_dependencies(down_snapshot_code, tag='main')
        my.assertEquals(2, len(depend_snapshots) )


        depend_snapshots = my.server.get_dependencies(down_snapshot_code, tag='whatever', include_paths=True, include_paths_dict=True, include_files=True)
        my.assertEquals(1, len(depend_snapshots) )


        paths  = depend_snapshots[0].get('__paths__') 
        
        # check that there is a path
        my.assertEquals(2, len(paths) )

        for path in paths:
            my.assertEquals(path.startswith('%s/unittest/person'%linux_client_repo_dir), True)
    
        # check that the paths_dict has 2 keys
        my.assertEquals(2, len(depend_snapshots[0].get('__paths_dict__').keys() ) )

        depend_snapshots = my.server.get_dependencies(down_snapshot_code, tag='whatever', include_paths=True, include_paths_dict=True, include_files=True, repo_mode='web')
        my.assertEquals(1, len(depend_snapshots) )
        paths  = depend_snapshots[0].get('__paths__') 
        for path in paths:
            my.assertEquals(path.startswith('%s/unittest/person'%web_base_dir), True)
    


    def _test_inplace_checkin(my):
        if os.name == "nt":
            path = "C:/temp/inplace_test.txt"
        else:
            path = "/tmp/inplace_test.txt"

        f = open(path, 'wb')
        f.write("inplace checkin")
        f.close()

        search_type = "unittest/person"
        code = "joe"
        context = 'test_checkin'
        search_key = my.server.build_search_key(search_type, code)

        context = "inplace"
        snapshot = my.server.simple_checkin(search_key, context, path, mode='inplace')
        snapshot_code = snapshot.get('code')
        checkin_path = my.server.get_path_from_snapshot(snapshot_code)

        # make sure the checkin path is equal to the original path
        my.assertEquals(path, checkin_path)

        snapshot2 = my.server.add_file(snapshot_code, path, file_type='inplace_type', mode='inplace')
        #checkin_path = my.server.get_path_from_snapshot(snapshot_code, 'pig')
        #my.assertEquals("", checkin_path)

    def _test_checkout(my):
        search_type = "unittest/person"
        code = "joe"
        context = 'test_checkin'
        search_key = my.server.build_search_key(search_type, code)

        dir = "."
        file_type = 'foo'

        # checkout latest
        paths = my.server.checkout(search_key, context, file_type=file_type)
        my.assertEquals(1, len(paths))
        path = paths[0]
        my.assertEquals('./miso_ramen_test_checkin_v004.jpg', path)
        my.assertEquals(True, os.path.exists(path) )

        os.unlink(path)


        paths = my.server.checkout(search_key, context, file_type=file_type, mode='download')
        my.assertEquals(1, len(paths))
        path = paths[0]
        my.assertEquals('./miso_ramen_test_checkin_v004.jpg', path)
        my.assertEquals(True, os.path.exists(path) )
        os.unlink(path)


        return



        # get a snapshot and all of its dependencies ... checkout the files
        #server.simple_checkout()

        # get all of the files recursively? Where to stop
        #paths = server.get_all_paths_from_snapshot(snapshot_code, recurse=True, search_types=['prod/asset','prod/texture'], contexts=['model'])






       




    def _test_get_snapshot(my):
        '''get an expanded version of the snapshot xml'''

        search_type = "unittest/person"
        code = "joe"
        context = "test_checkin"
        search_key = my.server.build_search_key(search_type, code)

        # get a version that does not exist
        version = 256
        snapshot = my.server.get_snapshot(search_key, context, version)
        my.assertEquals( {}, snapshot )


        # get current version
        version = 0
        snapshot = my.server.get_snapshot(search_key, context, version)
        my.assertNotEquals( {}, snapshot )
        my.assertEquals( 2, snapshot.get("version") )

        # get latest version
        version = -1 
        latest_snapshot = my.server.get_snapshot(search_key, context, version)
        my.assertNotEquals( {}, latest_snapshot )
        my.assertEquals( 4, latest_snapshot.get("version") )

        # get current version again and show it is not the latest
        version =  0
        snapshot = my.server.get_snapshot(search_key, context, version)
        my.assertNotEquals( {}, snapshot )
        my.assertEquals( 2, snapshot.get("version") )

        # set this as the current
        my.server.set_current_snapshot(latest_snapshot.get("code"))

        # get current version again
        version =  0
        snapshot = my.server.get_snapshot(search_key, context, version)
        my.assertNotEquals( {}, snapshot )
        my.assertEquals( 4, snapshot.get("version") )

          
        # get version number 1
        version = 1
        snapshot = my.server.get_snapshot(search_key, context, version, include_files=True)
        my.assertNotEquals( {}, snapshot )
        my.assertEquals( 1, snapshot.get("version") )



        # get full xml
        snapshot_xml = my.server.get_full_snapshot_xml( snapshot.get("code") )
        assert(snapshot_xml)

        # versionless
        versionless_snapshot = my.server.get_snapshot(search_key, context, 0, include_paths=True, include_paths_dict=False, versionless=True)
        my.assertEquals( {}, versionless_snapshot)

   
    def _test_get_paths(my):
        '''get snapshot file paths'''

        search_type = "unittest/person"
        code = "joe"
        context = "test_checkin"
        search_key = my.server.build_search_key(search_type, code)

        # get a version that does not exist
        try:
            version = 256
            snapshot = my.server.get_paths(search_key, context, version)
        except Exception, e:
            if 'version [256] does not exist' in e.__str__():
                pass
            else:
                raise

        # get current version
        version = 0
        paths = my.server.get_paths(search_key, context, version, file_type='*', versionless=False)
        my.assertNotEquals( {}, paths )
        lib_paths = paths.get('lib_paths')

        
        asset_dir = my.server.get_base_dirs().get('asset_base_dir')
        lib_path_exist = '%s/unittest/person/joe/test_checkin/.versions/miso_ramen_test_checkin_v004.jpg'%asset_dir in lib_paths
        my.assertEquals( lib_path_exist, True )

        
      
        # get current version
        try:
            version = -1
            paths = my.server.get_paths(search_key, context, version, file_type='*', versionless=True)
        except Exception, e:
            if 'version [-1] does not exist' in e.__str__():
                pass
            else:
                raise
        # create a latest versionless
        file_path = "%s/test/miso_ramen.jpg" % my.client_lib_dir
        my.server.simple_checkin(search_key, context, file_path, mode='copy', checkin_type='auto')

        version = -1
        paths = my.server.get_paths(search_key, context, version, file_type='*', versionless=True)
        my.assertNotEquals( {}, paths )
        lib_paths = paths.get('lib_paths')
       

        lib_path_exist = '%s/unittest/person/joe/test_checkin/miso_ramen_test_checkin.jpg'%asset_dir in lib_paths
        my.assertEquals( lib_path_exist, True )


        # create a directory latest versionless
        # TODO: test a strict check_type directory check-in
        file_path = "%s/test/images/subfolder" % my.client_lib_dir
        my.server.directory_checkin(search_key, context, file_path, mode='copy', checkin_type='auto')

        version = -1
        paths = my.server.get_paths(search_key, context, version, file_type='*', versionless=True)
        my.assertNotEquals( {}, paths )
        lib_paths = paths.get('lib_paths')
        lib_path_exist = '%s/unittest/person/joe/test_checkin/subfolder_test_checkin'%asset_dir == lib_paths[0]
        my.assertEquals( lib_path_exist, True )

    def _test_level_checkin(my):

        # create a fake city
        data = { 
            'code': 'toronto'
        }
        search_key = 'unittest/city'
        my.server.insert(search_key, data)
        
        return

        # we use the joe user
        search_type = "unittest/person"
        code = "joe"
        context = "test_checkin"
        search_key = my.server.build_search_key(search_type, code)


        # set the level
        level_type = 'unittest/city'
        level_code = 'toronto'
        level_key = my.server.build_search_key(level_type, level_code)

        file_path = "%s/test/miso_ramen.jpg" % my.client_lib_dir


        # get the latest snapshot
        result = my.server.get_snapshot(search_key, context)
        my.assertEquals(4, result.get("version") )

        # check that the level get_snapshot also receives current snapshot
        result = my.server.get_snapshot(search_key, context, level_key=level_key)
        my.assertEquals(2, result.get("version") )

        # check that the snapshot recieved has no level
        my.assertEquals("", result.get('level_type'))


        # use a different path to avoid the exact same file name
        file_path = "%s/test/images/miso_ramen.0001.jpg" % my.client_lib_dir
        # check in with level checkin
        my.server.upload_file(file_path)
        result = my.server.simple_checkin(search_key, context, file_path, file_type="foo", is_current=False, level_key=level_key)

        my.assertEquals(1, result.get("version") )

        # get the snapshot back again with the level
        result = my.server.get_snapshot(search_key, context, level_key=level_key)
        my.assertEquals(1, result.get("version") )
        my.assertEquals("unittest/city?project=unittest", result.get('level_type'))

        # get snapshot with no level
        result = my.server.get_snapshot(search_key, context)
        my.assertEquals(4, result.get("version") )



    def _test_add_file(my):

        search_type = "unittest/person"
        code = "joe"
        context = "publish"
        search_key = my.server.build_search_key(search_type, code)

        dir = "%s/test/images" % my.client_lib_dir
        path1 = "%s/miso_ramen.0001.jpg" % dir
        path2 = "%s/miso_ramen.0002.jpg" % dir
        path3 = "%s/miso_ramen.0003.jpg" % dir
        path4 = "%s/miso_ramen.0004.jpg" % dir

        # check the file in
        my.server.upload_file(path1)
        my.server.upload_file(path2)

        snapshot = my.server.simple_checkin(search_key, "publish", path1)
        snapshot_code = snapshot.get("code")

        snapshot = my.server.add_file(snapshot_code, path2, "second")
        assert snapshot

        filters = [('search_type','unittest/person?project=unittest'), ('search_code','joe'), ('revision','0'), ('context','publish'), ('is_latest','1')]
        query_snap = my.server.query_snapshots(filters=filters, include_files=False, single=True)
        #test multi file add_file using upload
        paths = [path3, path4]
        snapshot = my.server.add_file(snapshot_code, paths, ["third", "fourth"], mode='upload')
        res_snap = my.server.get_snapshot(search_key, include_files=True)
        
        my.assertEquals(query_snap[0].get('code'), res_snap.get('code'))

        files = res_snap.get('__files__')
        if files:
            for file in files:
                if file.get('type')=='third':
                    my.assertEquals(file.get('source_path'), path3)
                    my.assertEquals(file.get('file_name'), 'miso_ramen.0003_v002.jpg')

                elif file.get('type')=='fourth':
                    my.assertEquals(file.get('source_path'), path4)
        # TODO: parse the xml to make sure the files are there

        # test mode='preallocate'
        file_type = 'test_file_type'

        # this name doesn't matter
        file_name = 'miso_ramen.jpg'
        path = my.server.get_preallocated_path(snapshot_code, file_type, file_name, checkin_type='strict')
        new_dir = os.path.dirname(path)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        shutil.copy(path3, path)

        my.server.add_file(snapshot_code, path, file_type, mode='preallocate')
        res_snap = my.server.get_snapshot(search_key, include_files=True)
        files = res_snap.get('__files__')

        # verify source_path
        for file in files:
            if file.get('type')==file_type:
                my.assertEquals(file.get('source_path'), path)

        
        # test group checkin
        file_path = "%s/test/images/miso_ramen.####.jpg" % my.client_lib_dir
        new_path = "%s/test/images/group_miso_ramen.####.jpg" % my.client_lib_dir
        file_range = "1-5"

        # copy files to the handoff dir
        handoff_dir = my.server.get_handoff_dir()
        for i in range(1,6):
            file_name = "miso_ramen.%0.4d.jpg" % i
            expanded_path = "%s/test/images/%s" % (my.client_lib_dir, file_name)
            #to_path = "%s/%s" % (my.client_lib_dir, handoff_dir)
            shutil.copy(expanded_path, '%s/group_%s' %(handoff_dir, file_name ))
            # make another copy for upload/copy checkin
            to_path = "%s/test/images/group_%s" % (my.client_lib_dir, file_name)
            shutil.copy(expanded_path, to_path )

        # avoid checking in the same files to the repo, which would cause an exception
        file_type = "group"
        result = my.server.add_group(snapshot_code, new_path, file_type, '1-2', use_handoff_dir=True)


        # add the group with upload mode
        file_type = "group"
        result = my.server.add_group(snapshot_code, new_path, file_type, '3-4', mode='upload')
        # add the group with copy mode
        file_type = "group"
        result = my.server.add_group(snapshot_code, new_path, file_type, '5-5', mode='copy')

        # add the directory
        mode = "copy"
        file_type = "directory"
        snapshot = my.server.add_directory(snapshot_code, dir, file_type, mode=mode)
        snapshot_code = snapshot.get("code")

        # get all the filename and test they exist
        paths = my.server.get_all_paths_from_snapshot(snapshot_code)

        # asset that this is a directory
        my.assertEquals( True, os.path.isdir(paths[-1]) )

        mode = "copy"
        file_type = 'custom_dir'
        # test custom dir and file_naming for add_directory
        snapshot = my.server.add_directory(snapshot_code, dir, file_type, mode=mode,\
            dir_naming='{project.code}/person/{sobject.code}/custom_dir', file_naming='{snapshot.version}_dir')
        snapshot_code = snapshot.get("code")

        # get all the filename and test they exist
        path = my.server.get_path_from_snapshot(snapshot_code, file_type=file_type)
        my.assertEquals( path.endswith('unittest/person/joe/custom_dir/002_dir'), True)
        # test custom file_naming and create_icon = True

        file_type = 'custom_icon'
        file_naming = '{sobject.code}_snapIcon_V{snapshot.version}.{ext}'
        dir_naming='{project.title}/12_TACTIC/snapshot_icon'
        snap = my.server.add_file(snapshot_code, path4, file_type, create_icon=False, mode='copy', file_naming=file_naming, dir_naming= dir_naming)
        #print snap
        snapshot = my.server.query_snapshots(filters=[('code',snap.get('code'))], include_files=True)
        files = snapshot[0].get('__files__')
        asset_dir = my.server.get_base_dirs().get('asset_base_dir')

        for file in files:
            if file.get('type') == file_type:
                print "ooo: ", file.get('checkin_dir')
                my.assertEquals(file.get('checkin_dir'), '%s/Unittest/12_TACTIC/snapshot_icon'%asset_dir)

    def _test_hierarchy(my):

        # we use the joe user
        parent_type = "unittest/country"
        code = "canada"
        data = { 'code': code }
        parent = my.server.insert(parent_type, data)

        search_key = my.server.build_search_key(parent_type, code)

        child_type = "unittest/city"
        data = { 'code': 'vancouver', 'country_code': 'canada' }
        my.server.insert(child_type, data)
        data = { 'code': 'montreal', 'country_code': 'canada' }
        my.server.insert(child_type, data)


        # get the parent type
        parent_type = my.server.get_parent_type("unittest/city")
        my.assertEquals("unittest/country", parent_type)

        # get all of the child types
        child_types = my.server.get_child_types("unittest/country")
        #FIXME:
        #my.assertEquals(["unittest/city"], child_types)


        # get the country
        country = my.server.get_by_search_key(search_key)
        country_key = country.get('__search_key__')

        # get all the children
        children = my.server.get_all_children(country_key, child_type)
        child_codes = [x.get('code') for x in children]
        my.assertEquals(['montreal','vancouver'], child_codes)

        # get the parent
        city = children[0]
        city_key = city.get('__search_key__')
        country = my.server.get_parent(city_key)
        my.assertEquals('canada', country.get('code'))

        my.server.retire_sobject(parent.get('__search_key__'))
        country = my.server.get_parent(city_key)
        my.assertEquals({}, country)

        country = my.server.get_parent(city_key, show_retired=True)
        my.assertEquals('canada', country.get('code'))
        
        
        # get all the children, with columns sepecified
        columns = ['code']
        children = my.server.get_all_children(country_key, child_type, columns=columns)
        child = children[0]
        # code, __search_type__,  and __search_key__
        my.assertEquals(3, len(child.keys() ) )

        # test setting parent
        data = { 'code': 'calgary' }
        child = my.server.insert(child_type, data, parent_key=parent.get('__search_key__'))
        my.assertEquals("canada", child.get('country_code') )

        # create a new country
        parent_type = "unittest/country"
        country = 'holland'
        data = { 'code': country }
        parent = my.server.insert(parent_type, data)

        # change the parent of calgary
        child_key = child.get('__search_key__')
        parent_key = parent.get('__search_key__')
        child = my.server.update(child_key, parent_key=parent_key)
        my.assertEquals("holland", child.get('country_code') )

 


    def _test_retire_delete(my):

        # we use the joe user
        search_type = "unittest/country"
        code = "canada"
        data = { 'code': 'france' }
        country = my.server.insert(search_type, data)

        search_key = country.get('__search_key__')

        # retire the sobject
        country = my.server.retire_sobject(search_key)
        my.assertEquals('retired', country.get('s_status') )

        # general query for it and ensure it is not found
        filters = [[ 'code', country.get('code')]]
        results = my.server.query(search_type, filters)
        my.assertEquals(0, len(results) )

        # general query for it with show_retired and ensure it is found
        filters = [[ 'code', country.get('code')]]
        results = my.server.query(search_type, filters, show_retired=True)
        my.assertEquals(1, len(results) )

        # reactive the object
        country = my.server.reactivate_sobject(search_key)
        my.assertEquals('', country.get('s_status') )

        # general query for it and ensure it is found
        filters = [[ 'code', country.get('code')]]
        countries = my.server.query(search_type, filters)
        my.assertEquals(1, len(countries) )



    def _test_preallocate_checkin(my):
        
        # now check in the file
        search_type = "unittest/person"
        code = "joe"
        search_key = my.server.build_search_key(search_type, code)
        """
        # have to import some server module to get sandbox dir
        from pyasm.common import Config
        if os.name =='nt':
            base_dir = Config.get_value("checkin","win32_sandbox_dir")
            if base_dir == "":
                base_dir = Config.get_value("checkin","win32_local_base_dir")
                base_dir += "/sandbox"
        else:
            base_dir = Config.get_value("checkin","linux_sandbox_dir")
        """

        from pyasm.biz import DirNaming
        from pyasm.security import Batch
        Batch()
        dir_naming = DirNaming()
        base_dir = dir_naming.get_base_dir(protocol='sandbox')[0]

        # test virtual snapshot path
        context = 'virtual'
        ext = ".jpg"
        path = my.server.get_virtual_snapshot_path(search_key, context, ext=ext, checkin_type='auto')
        expected = "assets/unittest/person/\w+/%s/.versions/joe_virtual_v001.jpg$" %context
        my.assertEquals(True, None != re.search(expected, path))

        path = my.server.get_virtual_snapshot_path(search_key, context, ext=ext, checkin_type='strict')
        expected = "assets/unittest/person/\w+/%s/joe_virtual_v001.jpg$" %context
        my.assertEquals(True, None != re.search(expected, path))

        # test with no extension
        file_name = 'cow.mov'
        path = my.server.get_virtual_snapshot_path(search_key, context, file_name=file_name, checkin_type='strict')
        expected = "assets/unittest/person/\w*/%s/cow_virtual_v001.mov$" %context
        my.assertEquals(True, None != re.search(expected, path))

        # test sandbox protocol
        path = my.server.get_virtual_snapshot_path(search_key, context, file_name=file_name, protocol='sandbox')
        expected = "%s/unittest/person/\w+/%s/cow_virtual_v001.mov$" %(base_dir, context)
        my.assertEquals(True, None != re.search(expected, path))

        """
        # COmment this for now since we cache the base_dir
        # fake a linux client_repo path to test client_repo protocol, delete the prod_setting right after
        if os.name=='nt':
            dir_value = 'C:/unittest_repo/assets'
            sk = my.server.insert('config/prod_setting',data={'key': 'win32_client_repo_dir', 'value' : dir_value} )
            my.assertEquals(True, None != re.search(expected, path))
        else:
            dir_value = '/tmp/unittest_repo/assets'
            sk = my.server.insert('config/prod_setting',data={'key': 'linux_client_repo_dir', 'value' : dir_value})
            my.assertEquals(True, None != re.search(expected, path))

        path = my.server.get_virtual_snapshot_path(search_key, context, file_name=file_name, protocol='client_repo')

        expected = "%s/unittest/person/\w+/%s/cow_virtual_v001.mov$" %(dir_value, context)

        my.assertEquals(True , None != re.match(expected, path))
        
        my.server.delete_sobject(sk['__search_key__'])
        """
        # test with forced extension (test without starting period)
        ext = "jpg"
        path = my.server.get_virtual_snapshot_path(search_key, context, file_name=file_name, ext=ext, checkin_type='')
        expected = "assets/unittest/person/\w+/%s/.versions/cow_virtual_v001.jpg$" %context
        my.assertEquals(True, None != re.search(expected, path))




        # create an empty snapshot
        context = "preallocate"
        snapshot = my.server.create_snapshot(search_key, context)
        snapshot_code = snapshot.get('code')

        # preallocate a single file, don't give a file_name
        file_type = 'mov'
        path = my.server.get_preallocated_path(snapshot_code, file_type, checkin_type='strict')
        my.assertEquals( True, None != re.search('unittest/person/\w+/%s/joe_preallocate_v001'%context, path))

        # preallocate with a file_name 
        file_name = 'whatever.mov'
        path = my.server.get_preallocated_path(snapshot_code, file_type, file_name, checkin_type='strict')
        my.assertEquals( True, None != re.search('unittest/person/\w+/%s/whatever_preallocate_v001.mov$'%context, path))

        # preallocate with a file_name, protocol=sandbox 
        file_name = 'whatever.mov'
        path = my.server.get_preallocated_path(snapshot_code, file_type, file_name, protocol='sandbox', checkin_type='strict')
        my.assertEquals( True, None != re.search('unittest/person/\w+/%s/whatever_preallocate_v001.mov$'%context, path))
        my.assertEquals( True, path.startswith( base_dir ))

        # preallocate a sequence of files
        file_type = 'sequence'
        file_name = "images_%0.4d.png"
        file_range = "1-5"
        path = my.server.get_preallocated_path(snapshot_code, file_type, file_name, checkin_type='strict')
        my.assertEquals( True, None != re.search('unittest/person/\w+/%s/images_%%0.4d_preallocate_v001.png$'%context, path))


        # imitate a render by building files directly to the path
        for i in range(1,6):
            cur_path = path % i
            f = open(cur_path, 'wb')
            f.write("wowow")
            f.close()

        results = my.server.add_group(snapshot_code, path, file_type, file_range, mode='preallocate')

        snapshot_code = results.get('code')
        paths = my.server.get_expanded_paths_from_snapshot(snapshot_code, file_type)
        my.assertEquals( 5, len(paths))


        # add another preallocated file to the checkin using a specific file_type my_icon
        file_type = 'my_icon'
        file_name = 'icon.png'
        path = my.server.get_preallocated_path(snapshot_code, file_type, file_name, checkin_type='strict')
        f = open(path, 'wb')
        f.write("preallocated add_file()")
        f.close()

        snapshot = my.server.add_file(snapshot_code, path, file_type, mode='preallocate')
        added_path = my.server.get_path_from_snapshot(snapshot_code, file_type)
        my.assertEquals(path, added_path)
        my.assertEquals(True, os.path.exists(path), 'Path [%s] does not exist' % path)

        # add another preallocated file "extra" to the checkin with icon creation
        file_type = 'extra'
        file_name = 'miso_ramen.jpg'
        path = my.server.get_preallocated_path(snapshot_code, file_type, file_name, checkin_type='strict')
       
        src_path = "%s/test/miso_ramen.jpg" % my.client_lib_dir
        shutil.copy(src_path, path)

        snapshot = my.server.add_file(snapshot_code, path, file_type, mode='preallocate', create_icon=True)


        added_path = my.server.get_path_from_snapshot(snapshot_code, file_type)
        my.assertEquals(path, added_path)
        my.assertEquals(True, os.path.exists(path), 'Path [%s] does not exist' % path)



    def _test_version(my):
        server_version = my.server.get_server_api_version()
        client_api_version = my.server.get_client_api_version()
        my.assertEqual(server_version, client_api_version)
        
    def _test_build_search_key(my):
        sk = my.server.build_search_key('sthpw/login', 'admin',column='code')
        my.assertEqual('sthpw/login?code=admin', sk)

        split_sk = my.server.split_search_key(sk)
        my.assertEqual(('sthpw/login','admin'), split_sk)

        sk = my.server.build_search_key('unittest/person', 'p1',column='code', project_code='unittest')
        my.assertEqual('unittest/person?project=unittest&code=p1', sk)

        # defaults to code
        sk = my.server.build_search_key('unittest/person', 'p1', project_code='unittest')
        my.assertEqual('unittest/person?project=unittest&code=p1', sk)
        
        split_sk = my.server.split_search_key(sk)
        my.assertEqual(('unittest/person?project=unittest','p1'), split_sk)

   

    def _test_widget_config(my):
        search_type = "SideBarWdg_UNI"
        view = "project_view"
        element_names = ['user', 'group','task', 'rule']
        # simple reordering
        my.server.update_config(search_type, view, element_names)
        config_str = my.server.get_config_definition(search_type, view, 'user')
        try:
            my.assertEqual('<element name="user"/>', config_str.strip('\n'))
        except:
            my.assertEqual("<element name='user'/>", config_str.strip('\n'))
            
        data_dict = {
            'class_name': 'LinkWdg',
            'display_options': { 'search_type': 'unittest/person',
                                 'search_view': 'link_search:my_table',
                                 'view' : 'table'},
            'action_class_name': "tactic.ui.table.DropElementAction",

            'action_options': {'instance_type': 'sthpw/login_in_group'},

            'element_attrs': {'title': 'User List'},
            'unique': True}

        # add an inline element to definition (should error out)
        try:
            my.server.add_config_element(search_type, 'project_view', 'user', class_name = data_dict['class_name'], display_options=data_dict['display_options'], element_attrs=data_dict['element_attrs'], unique=data_dict['unique'])
        except Exception, e:
            my.assertEquals("<Fault 1: 'This view name [user] has been taken.'>", e.__str__())

        # add an invalid element name with space and special chars
        for name in ['user A', 'user\tY', '!hello user#', 'user\n', '\ruser']:
            try:
                my.server.add_config_element(search_type, 'project_view', name, class_name = data_dict['class_name'], display_options=data_dict['display_options'], element_attrs=data_dict['element_attrs'], unique=data_dict['unique'])
            except Exception, e:
                my.assertEquals(True, 'contains special characters or spaces' in e.__str__())
        
        # add an invalid element name starting with numbers
        for name in ['1user', '0 user', '90 users']:
            try:
                my.server.add_config_element(search_type, 'project_view', name, class_name = data_dict['class_name'], display_options=data_dict['display_options'], element_attrs=data_dict['element_attrs'], unique=data_dict['unique'])
            except Exception, e:
                my.assertEquals(True, 'should not start with a number' in e.__str__())
        my.server.add_config_element(search_type, 'definition', 'user',  class_name = data_dict['class_name'], display_options=data_dict['display_options'], element_attrs=data_dict['element_attrs'], unique=data_dict['unique'])


        new_element = my.server.add_config_element(search_type, 'definition', 'user2',  class_name = data_dict['class_name'], display_options=data_dict['display_options'], element_attrs=data_dict['element_attrs'], unique=data_dict['unique'], action_class_name=data_dict['action_class_name'], action_options=data_dict['action_options'])

        # not the plain element on the project_view level 
        # since it does not have title
        config_str = my.server.get_config_definition(search_type, view, 'user')
        my.assertNotEqual("<element name='user'/>", config_str.strip('\n'))

        my.server.add_config_element(search_type, view, 'user',\
            element_attrs={'title':'Users'}, unique=False)

        config_str = my.server.get_config_definition(search_type, view, 'user')
        try:
            my.assertEqual('<element name="user" title="Users"/>', config_str.strip('\n'))
        except: 
            my.assertEqual("<element name='user' title='Users'/>", config_str.strip('\n'))

        from pyasm.common import Environment

        # get display handler/options to verify
        rtn = my.server.execute_cmd('pyasm.widget.WidgetConfigTestCmd',\
            args={'search_type': search_type, 'view': view,
                'element_name': 'user', 'match':'LinkWdg'})

        my.assertEqual(rtn.get('info').get('display_handler'), 'LinkWdg')
        my.assertEqual(rtn.get('info').get('display_options').get('search_view'), 'link_search:my_table')

        config_str = my.server.get_config_definition(search_type, "definition", 'user')

        # verify the xml
        try:
            from Ft.Xml.Domlette import NonvalidatingReader
            from Ft.Xml.XPath import Evaluate
            my.doc = NonvalidatingReader.parseString(config_str, "XmlWrapper")
            xml_mode = 'xml'
        except ImportError:
            import lxml.etree as etree
            parser = etree.XMLParser(remove_blank_text=True)

            my.doc = etree.fromstring(config_str, parser)
            xml_mode = 'lxml'

        xml = Xml(string=config_str)
        xpath = "element[@name='user']/display"
        node = xml.get_node(xpath)
        my.assertEquals(Xml.get_attribute(node, 'class'), data_dict['class_name'])
        xpath = "element[@name='user']"
        node = xml.get_node(xpath)
        my.assertEqual(Xml.get_attribute(node, 'title'), "User List")
        xpath = "element[@name='user']/display/search_type"
        node = xml.get_node(xpath)
        my.assertEquals(xml.get_node_value(node), 'unittest/person')

        # no such definition
        config_str = my.server.get_config_definition(search_type, "abc", "group")
        my.assertEqual("", config_str)

        # plain group element here
        config_str = my.server.get_config_definition(search_type, view, "group")
        try:
            my.assertEqual('<element name="group"/>', config_str.strip('\n'))
        except: 
            my.assertEqual("<element name='group'/>", config_str.strip('\n'))
        config_str = my.server.get_config_definition(search_type, view, "wow")
        my.assertEqual("", config_str)

        # equivalent xml snippet
        src_xml = '''
        <element name='my_preference' title='MY pref' icon='CHECK'>
          <display class='LinkWdg'>
            <search_type>sthpw/pref_list</search_type>
            <view>user</view>
          </display>
        </element>
        '''
        element_name = 'my_preference'
        display_cls = "LinkWdg"
        options = {'search_type': 'sthpw/pref_list', 'view': 'user'}
        element_attrs= {'title' : 'MY pref', 'icon' : 'CHECK'}
        try: 
            my.server.add_config_element(search_type, view, element_name, \
                class_name=display_cls, display_options=options,\
                element_attrs=element_attrs)
        except Exception, e:
            my.assertEquals("<Fault 1: 'This view name [my_preference] is reserved for internal use.'>", e.__str__())
        
        element_name = "unit_preference"
        my.server.add_config_element(search_type, view, element_name, \
                class_name=display_cls, display_options=options,\
                element_attrs=element_attrs)

        config_str = my.server.get_config_definition(search_type, view, element_name)
        
        # verify the xml

        xml = Xml(string=config_str)
        xpath = "element[@name='unit_preference']/display"
        node = xml.get_node(xpath)

        my.assertEquals(Xml.get_attribute(node,'class'), display_cls)
        xpath = "element[@name='unit_preference']"
        node = xml.get_node(xpath)
        my.assertEquals(Xml.get_attribute(node, 'icon'), "CHECK")
        xpath = "element[@name='unit_preference']/display/search_type"
        node = xml.get_node(xpath)
        my.assertEquals(xml.get_node_value(node), 'sthpw/pref_list')



        search_type = "SideBarWdg_UNI"
        view = "my_view_admin"

        data_dict['element_attrs'] = {'title' : 'MY User', 'icon' : 'MY USER'}

        my.server.add_config_element(search_type, 'definition', 'my_user',  class_name = data_dict['class_name'], display_options=data_dict['display_options'], element_attrs=data_dict['element_attrs'], unique=data_dict['unique'], login='admin')

        my.server.add_config_element(search_type, 'my_view_admin', 'my_user', login='admin');

        config_str = my.server.get_config_definition(search_type, 'my_view_admin', 'my_user', personal=True)
        xml = Xml(string=config_str)
        xpath = "element[@name='my_user']/display"
        node = xml.get_node(xpath)
        my.assertEquals(Xml.get_attribute(node,'class'), display_cls)

        xpath = "element[@name='my_user']"
        node = xml.get_node(xpath)
        my.assertEquals(Xml.get_attribute(node,'title'), 'MY User')
        config_str = my.server.get_config_definition(search_type, 'project_view', 'my_user')
        my.assertEquals(config_str, '')

    def _test_create_task(my):
        search_type = "unittest/person"

        # insert the person
        data = {
            'code': 'wheat',
            'name_first': 'Mr.',
            'name_last': 'Wheat',
            'pipeline_code': 'person_pipe'
        }
        result = my.server.insert(search_type, data)
        person_sk = result.get('__search_key__')
        task = my.server.create_task(person_sk, process='start', assigned='ben')
        my.assertEquals(task.get('assigned'), 'ben')

    def _test_upload(my):
        from pyasm.common import Environment
        
        file_path = "%s/test/miso_ramen.jpg" % my.client_lib_dir
        size  = os.path.getsize(file_path)
        checksum = get_md5.get_md5(file_path)
       
        my.server.upload_file(file_path)
        transaction_ticket = my.server.get_transaction_ticket()

        upload_dir = Environment.get_upload_dir(transaction_ticket)
        upload_path = "%s/miso_ramen.jpg" % upload_dir

        exists = os.path.exists(upload_path)
        my.assertEquals(True, exists)
    
        upload_size = os.path.getsize(upload_path)
        my.assertEquals(size, upload_size)

        upload_checksum = get_md5.get_md5(upload_path)
        my.assertEquals(checksum, upload_checksum)

        # Do further upload tests if test files exist
        file_name = "large_file.jpg"
        file_path = "%s/test/%s" % (my.client_lib_dir, file_name)
        if os.path.exists(file_path):
            my._test_multipart_upload(file_name)

        file_name = "base64_file.png"
        file_path = "%s/test/%s" % (my.client_lib_dir, file_name)
        if os.path.exists(file_path):
            my._test_base64_upload(file_name)
      
        file_name = "large_base64_file.png"
        file_path = "%s/test/%s" % (my.client_lib_dir, file_name)
        if os.path.exists(file_path):
            my._test_base64_upload(file_name)

    def _test_multipart_upload(my, file_name):
        from pyasm.common import Environment

        file_path = "%s/test/%s" % (my.client_lib_dir, file_name)
        my.server.upload_file(file_path)
        transaction_ticket = my.server.get_transaction_ticket()
        upload_dir = Environment.get_upload_dir(transaction_ticket)
        upload_path = "%s/%s" % (upload_dir, file_name)
        size = os.path.getsize(file_path)
        checksum = get_md5.get_md5(upload_path) 

        exists = os.path.exists(upload_path)
        my.assertEquals(True, exists)

        upload_size = os.path.getsize(upload_path)
        my.assertEquals(size, upload_size)

        upload_checksum = get_md5.get_md5(upload_path)
        my.assertEquals(checksum, upload_checksum)

    def _test_base64_upload(my, file_name):
        from pyasm.common import Environment
        file_path = "%s/test/%s" % (my.client_lib_dir, file_name)
        my.server.upload_file(file_path)
        transaction_ticket = my.server.get_transaction_ticket()
        upload_dir = Environment.get_upload_dir(transaction_ticket)
        
        # On upload, an action file should be created in the same
        # upload directory.
        upload_path = "%s/%s" % (upload_dir, file_name)
        action_path = "%s.action" % upload_path
        file_exists = os.path.exists(upload_path)
        action_exists = os.path.exists(action_path)
        my.assertEquals(True, file_exists)
        my.assertEquals(True, action_exists)
        
        decoded_data = open(upload_path, "rb")
        header = decoded_data.read(22)
        my.assertNotEqual(header, "data:image/png;base64,")
        decoded_data.close()

        # On upload a file of the same name, the original action 
        # file should be deleted.
        unencoded_file = "%s/test/miso_ramen.jpg" % my.client_lib_dir
        temporary_name = "%s/test/base64_original.png" % my.client_lib_dir
        os.rename(file_path, temporary_name) 
        os.rename(unencoded_file, file_path)

        my.server.upload_file(file_path)

        upload_exists = os.path.exists(upload_path)
        action_exists = os.path.exists(action_path)
        my.assertEquals(True, upload_exists)
        my.assertEquals(False, action_exists)
        
        # Revert names
        os.rename(file_path, unencoded_file)
        os.rename(temporary_name, file_path) 

    def _test_check_access(my):
        returned = my.server.check_access('project', {'code':'unittest'}, 'allow')
        my.assertEquals(True, returned)
        
        # all project is allowed for admin
        returned = my.server.check_access('project', {'code':'sample3d'}, 'allow')
        my.assertEquals(True, returned)

    def _test_pipeline(my):
        search_type = "unittest/person"

        # insert the person
        data = {
            'code': 'drkitchen',
            'name_first': 'Dr.',
            'name_last': 'Kitchen',
            'pipeline_code': 'person_pipe'
        }
        result = my.server.insert(search_type, data)
        person_sk = result.get('__search_key__')

        search_type = "sthpw/pipeline"

        # insert the pipeline
        data = {
            'code': 'person_pipe',
            'search_type': 'unittest/person',
            'pipeline': '''<pipeline type="serial">  
  <process name="model"/>  
  <process name="texture"/>  
  <process name="shader"/>  
  <process name="rig"/>  
  <connect to="texture" from="model" context="model"/>  
  <connect to="shader" from="texture" context="texture"/>  
  <connect to="shot/layout" from="rig" context="rig"/> 
  <connect to="rig" from="texture" context="texture"/>  
  <connect to="shot/lighting" from="shader"/>  
</pipeline>'''
        }
        if not my.server.eval("@SOBJECT(sthpw/pipeline['code','person_pipe'])"):
            result = my.server.insert(search_type, data)
        
        processes = my.server.get_pipeline_processes(person_sk)
        my.assertEqual(['model','texture','shader','rig'], processes)
        info = my.server.get_pipeline_processes_info(person_sk, related_process='texture')
        my.assertEqual({'input_processes': ['model'], 'output_processes': ['shader','rig'], 'input_contexts': ['model'],\
                'output_contexts': ['texture','texture']}, info)


        info = my.server.get_pipeline_xml_info(person_sk, include_hierarchy=True)
        info = my.server.get_pipeline_xml(person_sk)

    def _test_missing_method(my):
        my.server.pig('a', 'b', 'c')



    # NOT IMPLEMENTED 
    def _test_multicall(my):
        '''NOTE: Not supported by cherrypy yet!!'''

        # start a multicall transaction

        search_type = "prod/shot"

        multicall = xmlrpclib.MultiCall(my.server)

        for i in range(0, 3):
            sequence_code = "FG"
            code = "%s%0.3d" % (sequence_code, i)
            data = {
                'code': code,
                'sequence_code': sequence_code,
                'description': 'Dynamic Shot'
            }

            #multicall.insert(search_type, data)
            multicall.test()

        result = multicall()

        #my.server.commit()







if __name__ == "__main__":
    unittest.main()


