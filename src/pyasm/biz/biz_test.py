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

__all__ = ["BizTest"]

import tacticenv

import unittest

from pyasm.common import *
from pyasm.security import *
from pyasm.search import Transaction, SearchType, Search
from pyasm.unittest import Person
from pyasm.checkin import FileCheckin

from project import *
from snapshot import *
from schema import *
from task import *
from naming import *
from note import Note
from pipeline import Context, Pipeline
from expression import ExpressionParser
from pyasm.unittest import UnittestEnvironment, Sample3dEnvironment


class BizTest(unittest.TestCase):

    """
    def setUp(my):
        Batch()
        Project.set_project("unittest")
    """ 

    def test_all(my):

        
        Batch()
        from pyasm.web.web_init import WebInit
        WebInit().execute()
    
        #TODO add the schema entry to the sample3d plugin first
        #sample3d_test_env = Sample3dEnvironment()
        #sample3d_test_env.create()

        test_env = UnittestEnvironment()
        test_env.create()
        my.transaction = Transaction.get(create=True)
        try:
            
            my.person = Person.create( "Unit", "Test",
                    "ComputerWorld", "Fake Unittest Person")
            my.search_type = my.person.get_search_type()
            my.search_id = my.person.get_id()
            my.search_code = my.person.get_value("code")
            my.context = "test"
            my.full_context = "test/subtest"

            my._test_instances()

            my._test_pipeline()
            my._test_pipeline_connects()

            my._test_schema()
            my._test_snapshot()
            my._test_level()
            my._test_naming_util()
            my._test_sobject_hierarchy()

            my._test_add_tasks()
        finally:
            my.transaction.rollback()
            Project.set_project('unittest')

            test_env.delete()
            #sample3d_test_env.delete()

    def _test_add_tasks(my):

        pipe = Pipeline.create('person','person','unittest/person')
        xml = '''
        <pipeline>
  <process name="design1"/>
  <process name="design2"/>
  <process name="design3"/>
  <connect to="design2" from="design1"/>
  <connect to="design3" from="design2"/>
</pipeline>'''
        pipe.set_value('pipeline', xml)
        
        pipe.set_pipeline(xml)
        pipe.commit()
        Pipeline.clear_cache()
        pipeline = Pipeline.get_by_code('person')
        my.assertEquals(pipeline != None, True)

        # add bunch of dummy initial tasks to the person
        initial_tasks = Task.add_initial_tasks(my.person, 'person', processes=['design1','design2'], mode='simple process', skip_duplicate=True)
        context_list = []
        for task in initial_tasks:
            full_context ='%s:%s' %(task.get_value('process'), task.get_value('context'))
            context_list.append(full_context)

        my.assertEquals(context_list, ['design1:design1','design2:design2'])

        initial_tasks = Task.add_initial_tasks(my.person, 'person', processes=['design1','design2'], mode='simple process', skip_duplicate=False)
        context_list = []
        for task in initial_tasks:
            full_context ='%s:%s' %(task.get_value('process'), task.get_value('context'))
            context_list.append(full_context)

        my.assertEquals(context_list, ['design1:design1/001','design2:design2/001'])

        initial_tasks = Task.add_initial_tasks(my.person, 'person', contexts=['design1:design1/hi','design2:design2/low'], mode='context', skip_duplicate=False)
        context_list = []
        for task in initial_tasks:
            full_context ='%s:%s' %(task.get_value('process'), task.get_value('context'))
            context_list.append(full_context)

        my.assertEquals(context_list, ['design1:design1/hi','design2:design2/low'])

        initial_tasks = Task.add_initial_tasks(my.person, 'person', contexts=['design1:design1/hi','design2:design2/low'], mode='context', skip_duplicate=False)
        context_list = []
        for task in initial_tasks:
            full_context ='%s:%s' %(task.get_value('process'), task.get_value('context'))
            context_list.append(full_context)

        my.assertEquals(context_list, ['design1:design1/hi/001','design2:design2/low/001'])

        initial_tasks = Task.add_initial_tasks(my.person, 'person', contexts=['design1:design1/hi','design2:design2/low'], mode='context', skip_duplicate=True)
        # these are duplicated, so nothing should be created
        my.assertEquals(initial_tasks, [])


        
        initial_tasks = Task.add_initial_tasks(my.person, 'person', contexts=['design1:design1/hi','design2:design2/low','design3:design3','design3:design3'], mode='context', skip_duplicate=False)
      
        context_list = []
        for task in initial_tasks:
            full_context ='%s:%s' %(task.get_value('process'), task.get_value('context'))
            context_list.append(full_context)

        my.assertEquals(context_list, ['design1:design1/hi/002','design2:design2/low/002', 'design3:design3','design3:design3/001'])

        
        initial_tasks = Task.add_initial_tasks(my.person, 'person', contexts=['design1:design1','design3:design3'], mode='context', skip_duplicate=False)
      
        context_list = []
        for task in initial_tasks:
            full_context ='%s:%s' %(task.get_value('process'), task.get_value('context'))
            context_list.append(full_context)

        my.assertEquals(context_list, ['design1:design1/002','design3:design3/002'])

        initial_tasks = Task.add_initial_tasks(my.person, 'person', processes=['design2','design3'], mode='standard', skip_duplicate=False)
        context_list = []
        for task in initial_tasks:
            full_context ='%s:%s' %(task.get_value('process'), task.get_value('context'))
            context_list.append(full_context)

        my.assertEquals(context_list, ['design2:design2/002','design3:design3/003'])




    def _test_snapshot(my):


        # create a new test.txt file
        for i in range(0,4):

            # create a new test.txt file
            my.file_path = "./biz_test.txt"
            for i in range(0,4):
                file = open(my.file_path, 'w')
                file.write("whatever")
                file.close()

            checkin = FileCheckin(my.person, my.file_path, "main", context=my.context)
            checkin.execute()

            # get snapshot from database
            snapshot = checkin.get_snapshot()
            code = snapshot.get_value("code")
            s = Search("sthpw/snapshot")
            s.add_filter("code", code)
            snapshot = s.get_sobject()


        # get version -1
        snapshot = Snapshot.get_by_version(my.search_type, my.search_id, context=my.context, version=-1, use_cache=False)
        version = snapshot.get_version()
        my.assertEquals(4, version)

        # latest version
        snapshot = Snapshot.get_latest(my.search_type, my.search_id, context=my.context, use_cache=False)
        version = snapshot.get_version()

        my.assertEquals('biz_test_test_v004.txt', snapshot.get_all_file_names()[0])
        my.assertEquals(4, version)
        revision = snapshot.get_value('revision')
        my.assertEquals(0, revision)

        for i in range(0,2):
            file = open(my.file_path, 'w')
            file.write("whatever")
            file.close()
            # check in 2 current revisions
            checkin = FileCheckin(my.person, my.file_path, "main", context=my.context, is_revision=True, is_current=True)
            checkin.execute()
            snapshot = checkin.get_snapshot()

            # get snapshot from database
            #snapshot = checkin.get_snapshot()
            code = snapshot.get_value("code")
            s = Search("sthpw/snapshot")
            s.add_filter("code", code)
            snapshot = s.get_sobject()


        # get current version and revision latest
        snapshot = Snapshot.get_by_version(my.search_type, my.search_code, context=my.context, version=0, revision=-1, use_cache=False)
        version = snapshot.get_version()
        my.assertEquals(4, version)
        revision = snapshot.get_value('revision')
        my.assertEquals(2, revision)
            
        # get revision
        snapshot = Snapshot.get_snapshot(my.search_type, my.search_id, context=my.context, version=-1, revision=-1, use_cache=False)
        version = snapshot.get_version()
        my.assertEquals(4, version)
        revision = snapshot.get_value('revision')
        my.assertEquals(2, revision)
        is_latest = snapshot.get_value('is_latest')
        my.assertEquals(True, is_latest)
        
        # v4r1 should not be latest
        snapshot = Snapshot.get_by_version(my.search_type, my.search_id, context=my.context, version=4, revision=1, use_cache=False)
        version = snapshot.get_version()
        my.assertEquals(4, version)
        revision = snapshot.get_value('revision')
        my.assertEquals(1, revision)
        is_latest = snapshot.get_value('is_latest')
        my.assertEquals(False, is_latest)

        # is_latest is v4r2, so can't find v4r0 any more
        snapshot = Snapshot.get_snapshot(my.search_type, my.search_id, context=my.context, version=-1, revision=None, use_cache=False)
        
        my.assertEquals(None, snapshot)

        # use max to find v4r0
        snapshot = Snapshot.get_snapshot(my.search_type, my.search_id, context=my.context, version='max', revision=None, use_cache=False)
        version = snapshot.get_version()
        my.assertEquals(4, version)
        revision = snapshot.get_value('revision')
        my.assertEquals(0, revision)
    
        # add 2 non current revisions
        for i in range(0,2):
            file = open(my.file_path, 'w')
            file.write("whatever")
            file.close()

            # check in 2 revisions
            checkin = FileCheckin(my.person, my.file_path, "main", context=my.context, is_revision=True, is_current=False)
            checkin.execute()


        # get latest version and revision
        snapshot = Snapshot.get_snapshot(my.search_type, my.search_id, context=my.context, version=-1, revision=-1, use_cache=False)
        version = snapshot.get_version()
        my.assertEquals(4, version)
        revision = snapshot.get_value('revision')
        my.assertEquals(4, revision)
        is_latest = snapshot.get_value('is_latest')
        my.assertEquals(True, is_latest)


        # get current version and latest revision (but current v4r2 takes precedence)
        snapshot = Snapshot.get_snapshot(my.search_type, my.search_id, context=my.context, version=0, revision=-1, use_cache=False)
        version = snapshot.get_version()
        my.assertEquals(4, version)
        revision = snapshot.get_value('revision')
        my.assertEquals(2, revision)
        is_latest = snapshot.get_value('is_latest')
        my.assertEquals(False, is_latest)


        # get current version and 0 revision (but current v4r2 is the real current, returns None)
        snapshot = Snapshot.get_snapshot(my.search_type, my.search_id, context=my.context, version=0, revision=None, use_cache=False)
        my.assertEquals(None, snapshot)

        
        # is_latest is v4r4, so can't find v4r0 any more
        snapshot = Snapshot.get_snapshot(my.search_type, my.search_id, context=my.context, version=-1, revision=None, use_cache=False)
        my.assertEquals(None, snapshot)
        
        
        # use max to find v4r0
        snapshot = Snapshot.get_snapshot(my.search_type, my.search_id, context=my.context, version='max', revision=None, use_cache=False)
        version = snapshot.get_version()
        my.assertEquals(4, version)
        revision = snapshot.get_value('revision')
        my.assertEquals(0, revision)

        
        # create a new test.txt file
        my.file_path = "./biz_test_version.txt"
        file = open(my.file_path, 'w')
        file.write("whatever")
        file.close()

        # check in another revision v4r5 
        checkin = FileCheckin(my.person, my.file_path, "main", context=my.context, is_revision=True, is_current=False)
        checkin.execute()
        my.assertEquals(4, checkin.snapshot.get_version())
        my.assertEquals(5, checkin.snapshot.get_value('revision'))
                
        # create a new test_version.txt file
        my.file_path = "./biz_test_version.txt"
        file = open(my.file_path, 'w')
        file.write("whatever")
        file.close()
        # check in new revision v101 with a new context
        checkin = FileCheckin(my.person, my.file_path, "main", context='rev_test', is_revision=True, is_current=False)
        checkin.execute()
        my.assertEquals(1, checkin.snapshot.get_version())
        my.assertEquals(1, checkin.snapshot.get_value('revision'))

        # create a new test_version.txt file
        my.file_path = "./biz_test_version.txt"
        file = open(my.file_path, 'w')
        file.write("whatever")
        file.close()

        checkin = FileCheckin(my.person, my.file_path, "main", context='rev_test', is_revision=False, is_current=False)
        checkin.execute()
        # this should increment to v2r1
        my.assertEquals(2, checkin.snapshot.get_version())
    
    def _test_level(my):

        # add a country
        sobject = SearchType.create("unittest/country")
        sobject.set_value("code", "canada")
        sobject.commit()


        # add a city
        sobject = SearchType.create("unittest/city")
        sobject.set_value("code", "toronto")
        sobject.set_value("country_code", "canada")
        sobject.commit()

        my.person.set_value("city_code", "toronto")
        my.person.commit()
        

        level_type = "unittest/city"
        level_code = "toronto"
        level = Search.get_by_code(level_type, level_code)
        level_id = level.get_id()


        # create a new test.txt file
        my.file_path = "./biz_test.txt"
        for i in range(0,4):
            file = open(my.file_path, 'w')
            file.write("whatever")
            file.close()
       
        # creating version 5
        checkin = FileCheckin(my.person, my.file_path, "main", context=my.context)
        checkin.execute()
        
        my.file_path = "./biz_fulltest.txt"
        file = open(my.file_path, 'w')
        file.write("whatever")
        file.close()
        # for checkin using test/subtest
        checkin = FileCheckin(my.person, my.file_path, "main", context=my.full_context)
        checkin.execute()


        snapshot = Snapshot.get_snapshot(my.search_type, my.search_id, my.context, version=-1, use_cache=True, level_type=level_type, level_id=level_id)
        # make sure we get the top level one
        my.assertEquals( 5, snapshot.get_value("version") )
        my.assertEquals( "", snapshot.get_value("level_type") )
        # integer None is now converted to 0
        my.assertEquals( 0, snapshot.get_value("level_id") )


        # checkin the file to the level
        my.file_path = "./biz_test_level.txt"
        for i in range(0,4):
            file = open(my.file_path, 'w')
            file.write("whatever")
            file.close()
        checkin = FileCheckin(my.person, my.file_path, "main", context=my.context, level_type=level_type, level_id=level_id)
        checkin.execute()

        snapshot = checkin.get_snapshot()
        version = snapshot.get_version()
        my.assertEquals(1, version)
        snapshot = Snapshot.get_snapshot(my.search_type, my.search_id, my.context, version='-1', use_cache=True, level_type=level_type, level_id=level_id)

        my.assertEquals( level_type, snapshot.get_value("level_type") )
        my.assertEquals( level_id, snapshot.get_value("level_id") )
        my.assertEquals( 1, snapshot.get_value("version") )
        my.assertEquals( True, snapshot.get_value("is_latest") )
        my.assertEquals( True, snapshot.get_value("is_current") )


        # get latest version and revision of the person and make sure 
        # it has its own is_latest
        top_snapshot = Snapshot.get_snapshot(my.search_type, my.search_id, context=my.context, version=-1, revision=-1, use_cache=False)
        version = top_snapshot.get_version()
        my.assertEquals(5, version)
        revision = top_snapshot.get_value('revision')
        my.assertEquals(0, revision)
        my.assertEquals( True, top_snapshot.get_value("is_latest") )
        my.assertEquals( True, top_snapshot.get_value("is_current") )

    def _test_schema(my):
        # prod type test
        prod_proj_code = "sample3d"
        if Project.get_by_code(prod_proj_code):
            prod_schema = Schema.get_by_project_code(prod_proj_code)
            parent_type = prod_schema.get_parent_type('prod/asset')
            my.assertEquals('prod/asset_library', parent_type)

            parent_type = prod_schema.get_parent_type('prod/sequence')
            my.assertEquals('prod/episode', parent_type)
            
            parent_type = prod_schema.get_parent_type('prod/shot')
            my.assertEquals('prod/sequence', parent_type)

            parent_type = prod_schema.get_parent_type('sthpw/task')
            my.assertEquals('*', parent_type)

            parent_type = prod_schema.get_parent_type('sthpw/note')
            my.assertEquals('*', parent_type)
            
            parent_type = prod_schema.get_parent_type('prod/render')
            my.assertEquals('*', parent_type)
            
            parent_type = prod_schema.get_parent_type('prod/submission')
            my.assertEquals('*', parent_type)
        
        schema = Schema.get_by_project_code("unittest")
        # create a new search_type
        schema.add_search_type("unittest/car", parent_type='unittest/person', commit=False)

        schema.add_search_type("unittest/house", parent_type='unittest/person', commit=False)
       
        
        
        parent_type = schema.get_parent_type('unittest/city')
        my.assertEquals('unittest/country', parent_type)

        # get all of the child types
        child_types = schema.get_child_types('unittest/person')
        expected = ['unittest/person_in_car', 'unittest/house']
        my.assertEquals(True, expected[0] in child_types)
        my.assertEquals(True, expected[1] in child_types)

        # create a new schema that has the unittest as the parent
        new_schema = SearchType.create(Schema.SEARCH_TYPE)
        new_schema.set_value("code", "unittest/custom")
        new_schema_xml = '''
        <schema parent='unittest'>
        <search_type name='unittest/account'/>
        <connect from='unittest/person' to='unittest/account' type='hierarchy'/>
        <connect from='*' to='unittest/poof' type='hierarchy'/>
        </schema>
        '''
        new_schema.set_xml(new_schema_xml)

        # get search_types defined in this schema
        search_types = new_schema.get_search_types(hierarchy=False)
        my.assertEquals(1, len(search_types) )

        # get all search_types
        search_types = new_schema.get_search_types()

        # add bunch of dummy initial tasks to the person
        initial_tasks = Task.add_initial_tasks(my.person, 'task')

        # check status_log static trigger
        single_task = initial_tasks[0]
        from pyasm.search import Search

        to_status = Search.eval('@GET(sthpw/status_log.to_status)', sobjects=[single_task], single=True)
        my.assertEquals(to_status, "Assignment")
        single_task.set_value('status', "Test Done")
        single_task.commit(triggers=True)
        

        ExpressionParser.clear_cache() 
        to_status = Search.eval("@GET(sthpw/status_log['@ORDER_BY','id desc'].to_status)", sobjects=[single_task], single=True)
        
        my.assertEquals(to_status, "Test Done")

        # get tasks with get_all_children()
        tasks = my.person.get_all_children("sthpw/task")
        my.assertEquals(len(initial_tasks), len(tasks) )

        
        # get notes with get_all_children()
        Note.create(my.person, "test note", context='default')
        Note.create(my.person, "test note2", context='default2')
        notes = my.person.get_all_children("sthpw/note")
        my.assertEquals(2, len(notes) )

        #relationship
        schema = Schema.get()
        if Project.get_by_code('sample3d'):
            relationship = schema.get_relationship('prod/asset','sthpw/snapshot')
            my.assertEquals(relationship, 'search_code')
            #my.assertEquals(relationship, 'search_type')

            relationship = schema.get_relationship('prod/asset','sthpw/task')
            my.assertEquals(relationship, 'search_code')
            #my.assertEquals(relationship, 'search_type')

            relationship = schema.get_relationship('prod/shot','sthpw/note')
            my.assertEquals(relationship, 'search_code')
            #my.assertEquals(relationship, 'search_type')

        relationship = schema.get_relationship('sthpw/file','sthpw/snapshot')
        my.assertEquals(relationship, 'code')
        relationship = schema.get_relationship('sthpw/project_type','sthpw/project')
        my.assertEquals(relationship, 'code')

        relationship = schema.get_relationship('unittest/car','unittest/house')
        my.assertEquals(relationship, None)

        # test parent filter search in sample3d
        if Project.get_by_code('sample3d'):
            from pyasm.prod.biz import *
            Project.set_project('sample3d')

            shot = Shot.get_by_code('RC_001_001')
            if not shot:
                shot = Shot.create('RC_001_001', 'Some test shot')
            asset = SearchType.create('prod/asset')
            asset.set_value('code','unittest010')
            asset.set_value('name','unittest010')
            asset.commit()
            for x in xrange(3):
                ShotInstance.create(shot, asset, 'unittest_veh_001', unique=False) 
            
            instances = ShotInstance.get_by_shot_and_asset(shot, asset)
            parent_type = 'prod/shot'
            parent_search = Search(parent_type)
            parent_search.add_filter('code','RC_001_001')
        
            search = Search('prod/shot_instance') 
            search.add_filter('asset_code', asset.get_code())
            # we want the base here
            sobject_type = search.get_search_type_obj().get_base_key()

            schema = Schema.get()
            relationship = schema.get_relationship(sobject_type, parent_type)
            parents = parent_search.get_sobjects()
            if parents:
                if relationship in ["code", "id", "search_type"]:
                    search.add_relationship_filters(parents) 
                    
            sobjects = search.get_sobjects()
            my.assertEquals(len(instances), len(sobjects))

            
            relationship_attrs = schema.get_relationship_attrs('sthpw/transaction_log','sthpw/sobject_log')
            rev_relationship_attrs = schema.get_relationship_attrs('sthpw/sobject_log','sthpw/transaction_log')
            for attrs in [ relationship_attrs,  rev_relationship_attrs]:
                my.assertEquals(attrs.get('from_col'), 'transaction_log_id')
                my.assertEquals(attrs.get('to_col'), 'id')
                my.assertEquals(attrs.get('from'), 'sthpw/sobject_log')
                my.assertEquals(attrs.get('to'), 'sthpw/transaction_log')
                my.assertEquals(attrs.get('relationship'), 'id')
                my.assertEquals(attrs.get('disabled'), None)


        Project.set_project('unittest')

    def _test_pipeline(my):

        # test project specific pipelines
        pipeline_xml = '''
        <pipeline>
            <process name='sketch'/>
            <process name='design'/>
            <process name='build'/>
            <process name='deploy'/>
        </pipeline>
        '''
        pipeline = SearchType.create("sthpw/pipeline")
        pipeline.set_value("pipeline", pipeline_xml)
        pipeline.set_value("code", "unittest/test")
        pipeline.set_value("search_type", "unittest/person")
        pipeline.commit()

        pipeline = Pipeline.get_by_code("unittest/test")
        my.assertEquals("sthpw/pipeline", pipeline.get_search_type() )

        process_names = pipeline.get_process_names()
        my.assertEquals(4, len(process_names))

        # test project specific pipelines
        pipeline_xml = '''
        <pipeline>
            <process name='think'/>
            <process name='sketch'/>
            <process name='design'/>
            <process name='build'/>
            <process name='deploy'/>
        </pipeline>
        '''
        pipeline = SearchType.create("config/pipeline")
        pipeline.set_value("pipeline", pipeline_xml)
        pipeline.set_value("code", "unittest/test")
        pipeline.set_value("search_type", "unittest/person")
        pipeline.commit()


        pipeline = Pipeline.get_by_code("unittest/test")
        my.assertEquals("config/pipeline?project=unittest", pipeline.get_search_type() )
        process_names = pipeline.get_process_names()
        my.assertEquals(5, len(process_names))

        return


        # TEST 
        # TEST 
        # TEST 
        pipeline_xml = '''
        <pipeline>
            <process name='layout'>
                <input name='instance' search_type='prod/shot_instance?project=bar' context='model' filter='asset_library=chr'/> 
                <input name='asset' search_type='prod/asset?project=bar' context='model' filter='asset_library=chr'/> 
            </process>
            <process name='animation'/>
        </pipeline>
        '''

        search = Search("prod/shot?project=bar")
        search.add_filter("code", "XG002")
        shot = search.get_sobject()

        pipeline = SearchType.create("sthpw/pipeline")
        pipeline.set_pipeline( pipeline_xml)


        snapshots = pipeline.get_input_snapshots(shot, 'layout', 'asset')

    def _test_pipeline_connects(my):

        # this is needed to prevent some trigger error on insert finding asset table
        if not Project.get_by_code('sample3d'):
            return

        Project.set_project('sample3d')
        from pipeline import Pipeline
        pipe = Pipeline.create('model_test','model_test','prod/asset')
        xml = '''
        <pipeline>  
  <process name="model"/>  
  <process name="texture"/>  
  <process name="shader"/>  
  <process name="rig"/>  
  <connect to="texture" from="model" context="model"/>  
  <connect to="shader" from="texture" context="texture"/>  
  <connect to="shot_test/layout" from="rig" context="rig"/> 
  <connect to="rig" from="texture" context="texture"/>  
  <connect to="shot_test/lighting" from="shader"/>  
</pipeline>'''
        pipe.set_value('pipeline', xml)
        pipe.set_pipeline(xml)
        pipe.commit()
        
        pipe = Pipeline.create('shot_test','shot_test','prod/shot')
        xml = '''
        <pipeline>
  <process name="layout"/>
  <process name="anim"/>
  <process name="char_final"/>
  <process name="effects"/>
  <process name="lighting"/>
  <process name="compositing"/>
  <connect to="layout" from="model_test/model" context="model"/>
  <connect to="layout" from="model_test/rig" context="rig"/>
  <connect to="anim" from="layout"/>
  <connect to="char_final" from="anim"/>
  <connect to="char_final" from="model_test/texture" context="texture"/>
  <connect to="effects" from="char_final" context='char_effects'/>
  <connect to="lighting" from="effects"/>
  <connect to="lighting" from="char_final" context='char_lgt'/>
  <connect to="compositing" from="lighting"/>
</pipeline>'''
        pipe.set_value('pipeline', xml)
        
        pipe.set_pipeline(xml)
        pipe.commit()
        from pyasm.biz import Pipeline
        pipeline = Pipeline.get_by_code('shot_test')
        back_connects = pipeline.get_backward_connects('layout')
        # we got 2 connections to layout from model_test
        my.assertEquals('model_test/model' in back_connects, True)
        my.assertEquals('model_test/rig' in back_connects, True)

   
        # test Context class
        context = Context('prod/shot', 'char_final')
        context_list = context.get_context_list()
        my.assertEquals(['char_effects','char_lgt'], context_list)
        
        context = Context('prod/shot', 'anim')
        context_list = context.get_context_list()
        my.assertEquals(['anim'], context_list)

        Project.set_project('unittest')

        



    def _test_sobject_hierarchy(my):

        # FIXME: this functionality has been disabled until further notice
        return

        snapshot_type = SearchType.create("sthpw/snapshot_type")
        snapshot_type.set_value("code", "maya_model")
        snapshot_type.commit()

        snapshot_type = SearchType.create("prod/snapshot_type")
        snapshot_type.set_value("code", "maya_model")
        snapshot_type.commit()

        snapshot_type = SnapshotType.get_by_code("maya_model")

    def _test_naming_util(my):
        ''' there is more naming test in naming_test.py'''

        naming = NamingUtil()
        snapshot = Snapshot.get_latest_by_sobject(my.person, context="test")
        snapshot2 = Snapshot.get_latest_by_sobject(my.person, context="test/subtest")



        # convert a naming pattern to a file
        template = "{name_last}_{name_first}_{context[0]}_{context[1]}.jpg"
        file_name = naming.naming_to_file(template, my.person, snapshot2)
        my.assertEquals("Test_Unit_test_subtest.jpg", file_name)

        template = "{name_last}_{name_first}_{snapshot.context[0]}_{snapshot.context[1]}.jpg"
        file_name = naming.naming_to_file(template, my.person, snapshot2)
        my.assertEquals("Test_Unit_test_subtest.jpg", file_name)

        template = "{name_last}_{name_first}_{context[0]}.png"
        file_name = naming.naming_to_file(template, my.person, snapshot)
        my.assertEquals("Test_Unit_test.png", file_name)

        # use a non-existent index , i.e. 2 
        template = "{name_last}_{name_first}_{context[2]}.png"
        file_name = naming.naming_to_file(template, my.person, snapshot)
        # unknown context index returns !
        my.assertEquals("Test_Unit_!.png", file_name)

        
        # explicit declarations of objects
        template = "{sobject.name_last}/first/{sobject.name_first}/{snapshot.context}"
        dir = naming.naming_to_dir(template, my.person, snapshot)

        my.assertEquals("Test/first/Unit/test", dir)

        template = "{sobject.name_last}_{sobject.name_first}_{snapshot.context}.jpg"
        file_name = naming.naming_to_file(template, my.person, snapshot)
        my.assertEquals("Test_Unit_test.jpg", file_name)


        # implicit declarations
        template = "{name_last}_{name_first}_{context}.jpg"
        file_name = naming.naming_to_file(template, my.person, snapshot)
        my.assertEquals("Test_Unit_test.jpg", file_name)

        # handle versions and revisions
        template = "{name_last}_{name_first}_{context}_v{version}_r{revision}.jpg"
        file_name = naming.naming_to_file(template, my.person, snapshot)
        my.assertEquals("Test_Unit_test_v005_r000.jpg", file_name)

        # create a fake file_object
        file = SearchType.create("sthpw/file")
        file.set_value("file_name", "whatever.png")
        template = "{name_last}_{name_first}_{context}_v{version}.{ext}"
        file_name = naming.naming_to_file(template, my.person, snapshot, file)
        my.assertEquals("Test_Unit_test_v005.png", file_name)

        # create a fake file_object with explicit ext
        file = SearchType.create("sthpw/file")
        file.set_value("file_name", "whatever.png")
        template = "{name_last}_{name_first}_{context}_v{version}.{ext}"
        file_name = naming.naming_to_file(template, my.person, snapshot, file, ext='bmp')
        my.assertEquals("Test_Unit_test_v005.bmp", file_name)

        # create parts of a directory
        # context = 'model/hi'
        snapshot.set_value("context", "model/hi")
        template = "{name_first}/{context[0]}/maya/{context[1]}"
        file_name = naming.naming_to_dir(template, my.person, snapshot, file)
        my.assertEquals("Unit/model/maya/hi", file_name)

        template = "{name_first}/{snapshot.context[0]}/maya/{snapshot.context[1]}"
        file_name = naming.naming_to_dir(template, my.person, snapshot, file)
        my.assertEquals("Unit/model/maya/hi", file_name)
        
        # context = 'texture'
        snapshot.set_value("context", "texture")
        template = "{name_first}/{context[0]}/maya"
        file_name = naming.naming_to_dir(template, my.person, snapshot, file)
        my.assertEquals("Unit/texture/maya", file_name)
 

        

        # build a naming from a name
        sample_name = 'chr001_model_v004.0001.ext'
        naming = naming.build_naming(sample_name)
        my.assertEquals("{0}_{1}_{2}.{3}.{4}", naming)


    def _test_instances(my):

        # test many to many relationships
        # person to car?

        # create 3 cars
        cars = []
        instances = []

        # definition
        # <connect from="unittest/person_in_car" to="unittest/person" relationship="code"/>
        # <connect from="unittest/person_in_car" to="unittest/car" relationship="code"/>
        # <connect from="unittest/person" to="unittest/car" instance_type="unittest/person_in_car" relationship="instance"/>

        # test add instances
        for model in ['Ferrari', 'Bugatti', 'Maserati']:
            car = SearchType.create("unittest/car")
            car.set_value("model", model)
            car.commit()
            instance = my.person.add_instance(car)
            cars.append(car)
            instances.append(instance)

        test_instances = my.person.get_instances("unittest/car")
        my.assertEquals(len(instances), len(test_instances))


        # test search instances
        for instance, test_instance in zip(instances, test_instances):
            search_key = instance.get_search_key()
            test_search_key = test_instance.get_search_key()
            my.assertEquals(search_key, test_search_key)


        # get the instance between two sobjects
        #instance = car.get_instance(person)


        #instances = my.person.get_related_sobjects("unittest/car")


        # test remove the first instance
        my.person.remove_instance(cars[0])

        # test remove the other way around
        cars[1].remove_instance(my.person)


        test_instances = my.person.get_instances("unittest/car")
        my.assertEquals(1, len(test_instances))
        test_instances = cars[2].get_instances("unittest/person")
        my.assertEquals(1, len(test_instances))



if __name__ == '__main__':
    unittest.main()



