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

__all__ = ["NamingTest", "TestFileNaming"]

import tacticenv
import os
import unittest

from pyasm.common import *
from pyasm.security import *
from pyasm.checkin import FileCheckin
from pyasm.search import SearchType, Search, SearchKey, Transaction
from project import Project
from snapshot import Snapshot
from file import File 
from pyasm.prod.biz import Asset
from file_naming import FileNaming
from dir_naming import DirNaming
from naming import NamingUtil, Naming
from pyasm.unittest import UnittestEnvironment, Sample3dEnvironment

class TestFileNaming(FileNaming):

    def unittest_person(my):

        context = my.snapshot.get_value("context")

        file_type = my.snapshot.get_file_type()
        parts = []

        asset_code = my.sobject.get_code()
        parts.append(asset_code)
        parts.append(file_type)
        parts.append('v%0.3d' %my.snapshot.get_version())
        filename = '_'.join(parts)
        ext = my.get_ext()
        if ext:
            filename = '%s%s' %(filename, ext)
        return filename

class TestFileNaming2(FileNaming):

        
    def unittest_person(my):
        '''try an empty file name'''
        return ''

class TestDirNaming(DirNaming):

    def unittest_person(my, dirs):
        context = my.snapshot.get_value("context")
        file_type = my.get_file_type()
        parts = []

        asset_code = my.sobject.get_code()
        dirs.append(asset_code)
        if my._file_object:
            file_name = my._file_object.get_file_name()
            file_ext = ''
            if file_name:
                from pyasm.biz import File
                file_ext = File.get_extension(file_name)
            dirs.append('%s.%s'%(file_ext, file_type))
        
        #dirs.append(file_type)
        dirs.append('v%0.3d' %my.snapshot.get_version())
        return dirs

class NamingTest(unittest.TestCase):

    def setUp(my):
        # start batch environment
        Batch()
        from pyasm.web.web_init import WebInit
        WebInit().execute()

        my.sample3d_env = Sample3dEnvironment(project_code='sample3d')
        my.sample3d_env.create()

        my.test_env = UnittestEnvironment()
        my.test_env.create()

    

        # set up the proper project_type, with the use the ProdDirNaming and ProdFileNaming
        search = Search('sthpw/project')
        search.add_filter('code', 'unittest')
        my.sobj = search.get_sobject()

        # store the original setting in your database
        my.original_proj_type_dict = {'dir_naming_cls': my.sobj.get_value('dir_naming_cls'),
                'file_naming_cls': my.sobj.get_value('file_naming_cls') }

        #my.transaction = Transaction.get(create=True)
        if my.sobj:
            my.sobj.set_value('dir_naming_cls', 'pyasm.prod.biz.ProdDirNaming')
            my.sobj.set_value('file_naming_cls', 'pyasm.prod.biz.ProdFileNaming')
            my.sobj.commit()
        else:
            my.sobj = SearchType.create('sthpw/project_type')
            my.sobj.set_value('dir_naming_cls', 'pyasm.prod.biz.ProdDirNaming')
            my.sobj.set_value('file_naming_cls', 'pyasm.prod.biz.ProdFileNaming')
            my.sobj.set_value('code', 'unittest')
            my.sobj.commit()

      


    def create_snapshot(my):
        # set up a real person and snapshot (as opposed to virtual)
        code = 'phil'
       
        my.person = SearchType.create( 'unittest/person' )
        my.person.set_value("code",code)
        my.person.set_value("name_first", "Philip")
        my.person.commit()


        # create a new test.txt file
        file_path = "./naming_test.txt"
        for i in range(0,4):
            file = open(file_path, 'w')
            file.write("whatever")
            file.close()
        checkin = FileCheckin(my.person, file_path, "main", context='naming_test')
        checkin.execute()
        my.snapshot = checkin.get_snapshot()

        # create another test_base.txt file
        file_path = "./naming_base_test.txt"
        for i in range(0,4):
            file = open(file_path, 'w')
            file.write("whatever")
            file.close()
        checkin = FileCheckin(my.person, file_path, "main", context='naming_base_test')
        checkin.execute()
        my.base_snapshot = checkin.get_snapshot()

        dir_path = "./naming_test_folder"
        dir_path2 = "./.tactic_test" # test . folder
        dir_path3 = "./naming_test_folder3"
        dir_path4 = "./naming_test_folder4"
        for path in [dir_path, dir_path2, dir_path3, dir_path4]:
            if not os.path.exists(path):
                os.makedirs(path)

        checkin = FileCheckin(my.person, dir_path, "main", context='naming_base_test', checkin_type='auto')
        checkin.execute()
        my.auto_snapshot = checkin.get_snapshot()
        checkin = FileCheckin(my.person, dir_path2, "main", context='naming_folder_test', snapshot_type='directory', checkin_type='auto')
        checkin.execute()
        my.auto_snapshot2 = checkin.get_snapshot()

        # test a blank checkin_type
        checkin = FileCheckin(my.person, dir_path3, "main", context='naming_base_test', snapshot_type='directory', checkin_type='')
        checkin.execute()
        my.auto_snapshot3 = checkin.get_snapshot()
    
    def test_all(my):
        
        my.transaction = Transaction.get(create=True)
        try:
            my.create_snapshot()
            my._test_file_naming()
            my._test_file_naming_base()
            my._test_dir_naming()
            # this comes after test_dir_naming so the file_object doesn't get polluted
            my._test_file_naming_manual_version()
            my._test_get_naming()
            my._test_checkin_type()
            my._test_naming_util()
        finally:
            my.transaction.rollback()
            Project.set_project('unittest')

            my.test_env.delete()
            my.sample3d_env.delete()

        # reset the unittest project type to whatever it was
        """
        for key, value in my.original_proj_type_dict.items():
            my.sobj.set_value(key, value)
        my.sobj.commit()
        """

    def clear_naming(my):
        Container.put("Naming:cache", None)
        Container.put("Naming:cache:latest", None)
        Container.put("Naming:cache:unittest:latest", None)
        Container.put("Naming:cache:current", None)
        Container.put("Naming:cache:unittest:current", None)
        Container.put("Naming:cache:unittest", None)
        Container.put("Naming:namings", None)

    def _test_naming_util(my):
       
        #my.clear_naming()
        naming_util = NamingUtil()
        # these should evaluate to be the same
        file_naming_expr1 = ['{$PROJECT}__{context[0]}__hi_{$BASEFILE}.{$EXT}','{project.code}__{context[0]}__hi_{basefile}.{ext}']
        dir_naming_expr2 = ['{$PROJECT}/{context[1]}/somedir/{@GET(.name_first)}','{project.code}/{snapshot.context[1]}/somedir/{sobject.name_first}']

        process= 'light'
        context = 'light/special'
        type = 'ma'
        version = 2

        virtual_snapshot = Snapshot.create_new()
        virtual_snapshot_xml = '<snapshot process=\'%s\'><file type=\'%s\'/></snapshot>' % (process, type)
        virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
        virtual_snapshot.set_value("process", process)
        virtual_snapshot.set_value("context", context)
        virtual_snapshot.set_value("snapshot_type", 'file')

        virtual_snapshot.set_sobject(my.person)
        virtual_snapshot.set_value("version", version)

        file_name = "abc.txt"
        file_obj = File(File.SEARCH_TYPE)
        file_obj.set_value("file_name", file_name)
        
        for naming_expr in file_naming_expr1:
            file_name = naming_util.naming_to_file(naming_expr, my.person, virtual_snapshot, file=file_obj, file_type="main")
            my.assertEquals(file_name,'unittest__light__hi_abc.txt')

        for naming_expr in dir_naming_expr2:
            dir_name = naming_util.naming_to_dir(naming_expr, my.person, virtual_snapshot, file=file_obj, file_type="main")
            my.assertEquals(dir_name,'unittest/special/somedir/Philip')
    
    def _test_file_naming_manual_version(my):
       
        my.clear_naming()

        naming = SearchType.create('config/naming')
        naming.set_value('search_type','unittest/person')
        naming.set_value('context', 'naming_test')
        naming.set_value('dir_naming', '{project.code}/cut/{sobject.code}')
        naming.set_value('file_naming', '{sobject.code}_v{snapshot.version}.{ext}')
        naming.commit()

        
        preallocated = my.snapshot.get_preallocated_path(file_type='maya', file_name='what_v005.ma',ext='ma')
        my.assertEquals('/home/apache/assets/unittest/cut/phil/phil_v001.ma', preallocated)

        # now turn on manual_version
        naming.set_value('manual_version', True)
        naming.commit()

        my.clear_naming()
        preallocated = my.snapshot.get_preallocated_path(file_type='maya', file_name='what_v005.ma',ext='ma')
        my.assertEquals('/home/apache/assets/unittest/cut/phil/phil_v005.ma', preallocated)
        
        # Uppercase V and more digits
        preallocated = my.snapshot.get_preallocated_path(file_type='maya', file_name='what_V0010.ma',ext='ma')
        my.assertEquals('/home/apache/assets/unittest/cut/phil/phil_v010.ma', preallocated)
        #my.snapshot.commit()

        # zero or negative version is ignored
        # create a new manual version test.txt file
        file_path = "./naming_v0000_test.txt"
        for i in range(0,4):
            file = open(file_path, 'w')
            file.write("whatever")
            file.close()
        checkin = FileCheckin(my.person, file_path, "main", context='naming_test')
        checkin.execute()
        my.snapshot = checkin.get_snapshot()
        my.assertEquals(11, my.snapshot.get_version())

        # zero or negative version is ignored
        # create a new manual version test.txt file
        file_path = "./naming_v-23_test.txt"
        for i in range(0,4):
            file = open(file_path, 'w')
            file.write("whatever")
            file.close()
        checkin = FileCheckin(my.person, file_path, "main", context='naming_test')
        checkin.execute()
        my.snapshot = checkin.get_snapshot()
        my.assertEquals(12, my.snapshot.get_version())
        file_path = "./naming_v025_test.txt"
        for i in range(0,4):
            file = open(file_path, 'w')
            file.write("whatever")
            file.close()
        checkin = FileCheckin(my.person, file_path, "main", context='naming_test')
        checkin.execute()
        my.snapshot = checkin.get_snapshot()
        my.assertEquals(25, my.snapshot.get_version())


        naming.delete()

        my.clear_naming()


    def _test_file_naming_base(my):
       

        naming = SearchType.create('config/naming')
        naming.set_value('search_type','unittest/person')
        naming.set_value('context', 'naming_base_test')
        naming.set_value('dir_naming', '{project.code}/cut/{sobject.code}')
        naming.set_value('file_naming', '{sobject.code}_v{snapshot.version}_{basefile}.{ext}')
        naming.commit()
        
        my.clear_naming()

        # auto_snapshot is at v2
        preallocated = my.auto_snapshot.get_preallocated_path(file_type='some_dir', file_name='racoon',ext=None)
        my.assertEquals('/home/apache/assets/unittest/cut/phil/phil_v002_racoon', preallocated)
        
        preallocated = my.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon',ext=None)
        my.assertEquals('/home/apache/assets/unittest/cut/phil/phil_v001_racoon', preallocated)
        
        preallocated = my.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon.jpg',ext='jpg')
        #TODO: just get the base asset_path for the os first
        if os.name == 'nt':
            my.assertEquals('C:/spt/assets/unittest/cut/phil/phil_v001_racoon.jpg', preallocated)
        else:
            my.assertEquals('/home/apache/assets/unittest/cut/phil/phil_v001_racoon.jpg', preallocated)


        preallocated = my.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon2.PNG')
        my.assertEquals('/home/apache/assets/unittest/cut/phil/phil_v001_racoon2.PNG', preallocated)

        
        # test file expression
        naming.set_value('file_naming', '{@GET(.code)}_v{@GET(sthpw/snapshot.version)}_{$BASEFILE}.{$EXT}')
        naming.commit()
        my.clear_naming()

        preallocated = my.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon3.jpg',ext='jpg')
        my.assertEquals('/home/apache/assets/unittest/cut/phil/phil_v1_racoon3.jpg', preallocated)

        preallocated = my.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon4.PNG')
        my.assertEquals('/home/apache/assets/unittest/cut/phil/phil_v1_racoon4.PNG', preallocated)


        # test dir expression
        naming.set_value('dir_naming', '{$PROJECT}/exp_cut/{@GET(.code)}')
        naming.commit()
        my.clear_naming()

        preallocated = my.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon same.iff',ext='iff')
        my.assertEquals('/home/apache/assets/unittest/exp_cut/phil/phil_v1_racoon_same.iff', preallocated)

        # note: the actual check-in logic would replace " " with "_"
        preallocated = my.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon 5.PNG')
        my.assertEquals('/home/apache/assets/unittest/exp_cut/phil/phil_v1_racoon_5.PNG', preallocated)


        # test dir expression 2

        naming.set_value('dir_naming', '{$PROJECT}/3D/QC/ShotWork/playblast/ByDate/{$TODAY,|([^\s]+)| }/{@GET(.name_first)}')

        naming.commit()
        my.clear_naming()

        preallocated = my.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon same.iff',ext='iff')

        today = datetime.datetime.today()
        today = datetime.datetime(today.year, today.month, today.day)
        today = today.strftime("%Y-%m-%d")
        my.assertEquals('/home/apache/assets/unittest/3D/QC/ShotWork/playblast/ByDate/%s/Philip/phil_v1_racoon_same.iff'%today, preallocated)

        naming.delete()

        my.clear_naming()

    def _test_file_naming(my):
        process = 'model'
        type = 'main'
        context = 'modeling'
        version = 10
        file_name = 'testing_image.jpg'
        code = name = 'vehicle001'
        asset_library = 'vehicle'

        asset = SearchType.create( Asset.SEARCH_TYPE )
        asset.set_value("code",code)
        asset.set_value("name",name)
        asset.set_value("asset_library",asset_library)
        asset.set_value("asset_type","asset")

        virtual_snapshot = Snapshot.create_new()
        virtual_snapshot_xml = '<snapshot process=\'%s\'><file type=\'%s\'/></snapshot>' % (process, type)
        virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
        virtual_snapshot.set_value("context", context)
        virtual_snapshot.set_value("version", version)

        virtual_snapshot.set_sobject(asset)


        file_obj = File(File.SEARCH_TYPE)
        file_obj.set_value("file_name", file_name)
        

        file_naming = Project.get_file_naming()

        file_naming.set_sobject(asset)
        file_naming.set_snapshot(virtual_snapshot)
        file_naming.set_file_object(file_obj)

        expected_file_name = 'vehicle001_%s_v%0.3d.jpg' %(context,version)
        file_name = file_naming.get_file_name()
        my.assertEquals(expected_file_name, file_name)


        # try a default directory name

        file_obj.set_value("file_name", "test_dir")
        file_obj.set_value("base_type", "directory")
        file_naming.set_file_object(file_obj)
        
        # this should adopt the original dir name in the prefix
        expected_file_name = 'test_dir_%s_v%0.3d' %(context,version)
        file_name = file_naming.get_default()
        my.assertEquals(expected_file_name, file_name)

        #2 try a different search_type unittest/person
        version = 9
        
        
        file_obj.set_value("base_type", "file")
        # change a different input file name
        file_obj.set_value('file_name','some_maya_model.ma') 
        
        # use a real snapshot
        virtual_snapshot.set_sobject(my.person)
        virtual_snapshot.set_value("version", version)
        
        # change to the test file naming class
        my.sobj.set_value('file_naming_cls', 'pyasm.biz.naming_test.TestFileNaming')
        my.sobj.commit()
        Project.set_project('unittest')
        file_naming = Project.get_file_naming()
        file_naming.set_sobject(my.person)
        file_naming.set_snapshot(virtual_snapshot)
        file_naming.set_file_object(file_obj)
        file_name = file_naming.get_file_name()

        expected_file_name = 'phil_main_v009.ma'
        my.assertEquals(expected_file_name, file_name)

        # get_preallocated_path
        type = 'ma'
        #file_obj.set_value('type', type)
        #file_naming.set_file_object(file_obj)

        preallocated = my.snapshot.get_preallocated_path(file_type='maya', file_name='what.ma',ext='ma')
        preallocated_file_name = os.path.basename(preallocated)
        my.assertEquals("phil_main_v001.ma", preallocated_file_name)

        preallocated = my.snapshot.get_preallocated_path(file_type='houdini', file_name='what.otl',ext='otl')
        preallocated_file_name = os.path.basename(preallocated)
        my.assertEquals("phil_main_v001.otl", preallocated_file_name)

        preallocated = my.snapshot.get_preallocated_path(file_type='houdini', file_name='what_is.otl', ext='hipnc')
        preallocated_file_name = os.path.basename(preallocated)
        my.assertEquals("phil_main_v001.hipnc", preallocated_file_name)


        # try an empty file naming
        # change to the test file naming class
        my.sobj.set_value('file_naming_cls', 'pyasm.biz.naming_test.TestFileNaming2')
        my.sobj.commit()

        Project.set_project('unittest')
        file_naming = Project.get_file_naming()
        file_naming.set_sobject(my.person)
        file_naming.set_snapshot(virtual_snapshot)
        file_naming.set_file_object(file_obj)
        file_name = file_naming.get_file_name()
       
        preallocated = my.snapshot.get_preallocated_path(file_type='houdini', file_name='what_is.otl', ext='hipnc')
        from client.tactic_client_lib import TacticServerStub
        client = TacticServerStub.get()
        rtn = client.add_file(my.snapshot.get_code(), preallocated, 'houdini', mode='preallocate')
        rtn = client.get_snapshot(SearchKey.get_by_sobject(my.snapshot.get_parent()), context = 'naming_test', version = 1, include_files=True)
        files =  rtn.get('__files__')
        
        # assuming the file is ordered by code
        # the 1st file obj is a file and 2nd file obj is a directory
        for idx, file in enumerate(files):
            if idx ==0:
                my.assertEquals(file.get('type'), 'main')
                my.assertEquals(file.get('base_type'), 'file')
                my.assertEquals(file.get('file_name'), 'naming_test_naming_test_v001.txt')
                
            elif idx ==1:
                my.assertEquals(file.get('type'), 'houdini')
                my.assertEquals(file.get('base_type'), 'directory')
                my.assertEquals(file.get('md5'), '')
                my.assertEquals(file.get('file_name'), '')

    def _test_dir_naming(my):

        # change to the test dir naming class
        my.sobj.set_value('dir_naming_cls', 'pyasm.biz.naming_test.TestDirNaming')
        my.sobj.commit()

        # 1. try a different search_type unittest/person
        version = 9
        code = 'phil2'
        process = 'model'
        type = 'main'
        context = 'modeling'

        asset = SearchType.create( 'unittest/person' )
        asset.set_value("code",code)
        asset.set_value("name_first", "Philip")
        asset.commit()

        # change a different input file name
        file_obj = File(File.SEARCH_TYPE)
        # due to new restriction of set_sobject_value().. we can't use it any more
        #file_obj.set_sobject_value(asset)
        sk = SearchKey.get_by_sobject(asset, use_id =True)
        st = SearchKey.extract_search_type(sk)
        sid = SearchKey.extract_id(sk)
        file_obj.set_value('search_type', st)
        file_obj.set_value('search_id', sid)
        file_obj.set_value('file_name','some_maya_model.mb') 
        file_obj.set_value('type', type)
        file_obj.set_value('base_type', 'file')
        file_obj.commit()

        virtual_snapshot = Snapshot.create_new()
        virtual_snapshot_xml = '<snapshot process=\'%s\'><file type=\'%s\' file_code=\'%s\'/></snapshot>' % (process, type, file_obj.get_code())
        virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
        virtual_snapshot.set_value("context", context)

        virtual_snapshot.set_sobject(asset)
        virtual_snapshot.set_value("version", version)
        
       
        

        Project.set_project('unittest')
        dir_naming = Project.get_dir_naming()
        dir_naming.set_sobject(asset)
        dir_naming.set_snapshot(virtual_snapshot)
        dir_naming.set_file_object(file_obj)
        dir_name = dir_naming.get_dir()
        expected_dir_name = '/assets/phil2/mb.main/v009'
        expected_dir_name2 = '/phil2/mb.main/v009'
        my.assertEquals(expected_dir_name, dir_name)
        
        lib_paths = virtual_snapshot.get_all_lib_paths()
        sand_paths = virtual_snapshot.get_all_lib_paths(mode='sandbox')
        client_paths = virtual_snapshot.get_all_lib_paths(mode='client_repo')
       
        base_dir = Config.get_value("checkin", "asset_base_dir")
        sand_base_dir = dir_naming.get_base_dir(protocol='sandbox')
        client_base_dir = dir_naming.get_base_dir(protocol='client_repo')
        
        my.assertEquals(lib_paths[0].startswith('%s%s'%(base_dir, expected_dir_name2)), True)
        my.assertEquals(sand_paths[0].startswith('%s%s'%(sand_base_dir[0], expected_dir_name2)), True)
        my.assertEquals(client_paths[0].startswith('%s%s'%(client_base_dir[0], expected_dir_name2)), True)

        # 2  get_preallocated_path
        # set version 1 here since it's the first snapshot for this sobject. 
        # without a virtual file_object, the file_name is empty, and so the dir ma.maya is now .maya
        my.assertEquals("phil/.maya/v001", my.get_preallocated_dir()) 
        
        # switch back to regular file naming
        my.sobj.set_value('file_naming_cls', 'pyasm.biz.naming_test.TestFileNaming')
        my.sobj.commit()

        my.assertEquals("phil/ma.maya/v001", my.get_preallocated_dir()) 
        



    def get_preallocated_dir(my):
        preallocated = my.snapshot.get_preallocated_path(file_type='maya', file_name='what.ma',ext='ma')
        preallocated_dir_name = os.path.dirname(preallocated)
        preallocated_dir_name = preallocated_dir_name.replace('%s/' %Environment.get_asset_dir(), '')
        # remove the base part
        preallocated_dir_names = preallocated_dir_name.split('/')
        
        preallocated_dir_name = '/'.join(preallocated_dir_names)
        return preallocated_dir_name





    def _test_get_naming(my):
     
        # versionless
        naming = SearchType.create('config/naming')
        naming.set_value('search_type', 'unittest/person')
        naming.set_value('context', 'super')
        naming.set_value('latest_versionless', 'true')
        naming.set_value('dir_naming', '{project.code}/cut/VERSIONLESS/{sobject.code}')
        naming.set_value('file_naming', 'versionless_{sobject.code}_v{snapshot.version}.{ext}')
        naming.commit()

        # a context-less versionless entry for city
        naming = SearchType.create('config/naming')
        naming.set_value('search_type', 'unittest/city')
        naming.set_value('latest_versionless', 'true')
        #naming.set_value('context', 'ingest')
        naming.set_value('dir_naming', '{project.code}/cut/{snapshot.context}/VERSIONLESS/{sobject.code}')
        naming.set_value('file_naming', 'versionless_{sobject.code}_v{snapshot.version}.{ext}')
        naming.commit()


        naming = SearchType.create('config/naming')
        naming.set_value('search_type', 'unittest/city')
        naming.set_value('dir_naming', '{project.code}/cut/{snapshot.context}/DEFAULT_CONTEXTLESS/{sobject.code}')
        naming.set_value('file_naming', 'versionless_{sobject.code}_v{snapshot.version}.{ext}')
        naming.commit()

        naming = SearchType.create('config/naming')
        naming.set_value('search_type', 'unittest/city')
        naming.set_value('context', 'ingest')
        naming.set_value('dir_naming', '{project.code}/cut/{snapshot.context}/DEFAULT/{sobject.code}')
        naming.set_value('file_naming', 'versionless_{sobject.code}_v{snapshot.version}.{ext}')
        naming.commit()

        naming = SearchType.create('config/naming')
        naming.set_value('search_type', 'unittest/person')
        naming.set_value('context', 'icon')
        naming.set_value('dir_naming', '{project.code}/cut/ICON/{sobject.code}')
        naming.set_value('file_naming', 'icon_{sobject.code}_v{snapshot.version}.{ext}')
        naming.commit()

        # use condition 
        naming = SearchType.create('config/naming')
        naming.set_value('search_type', 'unittest/person')
        naming.set_value('context', 'icon')
        naming.set_value('condition', "@GET(.name_first)=='chip'")
        naming.set_value('dir_naming', '{project.code}/cut/chip_ICON/{sobject.code}')
        naming.set_value('file_naming', 'chip_icon_{sobject.code}_v{snapshot.version}.{ext}')
        naming.commit()

        # generic with search_type, snapshot_type
        naming = SearchType.create('config/naming')
        naming.set_value('search_type', 'unittest/person')
        naming.set_value('snapshot_type', 'file')
        naming.set_value('dir_naming', '{project.code}/cut/generic_snapshot/{sobject.code}')
        naming.set_value('file_naming', 'generic_snapshot_{sobject.code}_v{snapshot.version}.{ext}')
        naming.commit()

            
        # generic with nothing    
        naming = SearchType.create('config/naming')
        naming.set_value('search_type', 'unittest/person')
        naming.set_value('context', '')
        naming.set_value('dir_naming', '{project.code}/cut/generic/{sobject.code}')
        naming.set_value('file_naming', 'generic_{sobject.code}_v{snapshot.version}.{ext}')
        naming.commit()


        naming = SearchType.create('config/naming')
        naming.set_value('search_type', 'unittest/person')
        naming.set_value('context', 'light')
        naming.set_value('dir_naming', '{project.code}/cut/{sobject.code}')
        naming.set_value('file_naming', '{sobject.code}_v{snapshot.version}.{ext}')
        naming.commit()

        naming2 = SearchType.create('config/naming')
        naming2.set_value('search_type', 'unittest/person')
        naming2.set_value('context', '*/light')
        naming2.set_value('dir_naming', '{project.code}/cut')
        naming2.commit()
        
        naming3 = SearchType.create('config/naming')
        naming3.set_value('search_type', 'unittest/person')
        naming3.set_value('context', 'light/*')
        naming3.set_value('dir_naming', '{project.code}/light')
        naming3.commit()
        naming4 = SearchType.create('config/naming')
        naming4.set_value('search_type', 'unittest/person')
        naming4.set_value('context', '*/sub1')
        naming4.set_value('dir_naming', '{project.code}/sub')
        naming4.commit()

        naming5 = SearchType.create('config/naming')
        naming5.set_value('search_type', 'unittest/person')
        naming5.set_value('context', 'light/sub1')
        naming5.set_value('dir_naming', '{project.code}/light/sub1')
        naming5.commit()

        sobject = SearchType.create('unittest/person')
        sobject.set_value('name_first', 'chip')
        sobject.commit()
  
       
        naming6 = SearchType.create('config/naming')
        naming6.set_value('sandbox_dir_naming', '{$PROJECT}/{@GET(.id)}/')
        try:
            naming6.commit()
        except TacticException, e:
            message = 'sandbox_dir_name should not end with /'
        else:
            message = 'Pass'
        my.assertEquals(message, 'sandbox_dir_name should not end with /')

        naming7 = SearchType.create('config/naming')
        naming7.set_value('dir_naming', '{$PROJECT}/{@GET(.id)}/')
        try:
            naming7.commit()
        except TacticException, e:
            message = 'dir_name should not end with /'
        else:
            message = 'Pass'
        my.assertEquals(message, 'dir_name should not end with /')

        naming8 = SearchType.create('config/naming')
        naming8.set_value('sandbox_dir_naming', '{$PROJECT}/{@GET(.id)}')
        try:
            naming8.commit()
        except TacticException, e:
            message = 'sandbox_dir_name should not end with /'
        else:
            message = 'Pass'
        my.assertEquals(message, 'Pass')
        
        process= 'lgt'
        context = 'light'
        type = 'ma'
        version = 2
        virtual_snapshot = Snapshot.create_new()
        virtual_snapshot_xml = '<snapshot process=\'%s\'><file type=\'%s\'/></snapshot>' % (process, type)
        virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
        virtual_snapshot.set_value("process", process)
        virtual_snapshot.set_value("context", context)
        virtual_snapshot.set_value("snapshot_type", 'file')

        virtual_snapshot.set_sobject(sobject)
        virtual_snapshot.set_value("version", version)

        # city
        sobject2 = SearchType.create('unittest/city')
        sobject2.set_value('code', 'san diego')
        sobject2.commit()
        process= 'ingest'
        context = 'ingest'
        type = 'ma'
        version = 3
        virtual_snapshot2 = Snapshot.create_new()
        virtual_snapshot_xml = '<snapshot process=\'%s\'><file type=\'%s\'/></snapshot>' % (process, type)
        virtual_snapshot2.set_value("snapshot", virtual_snapshot_xml)
        virtual_snapshot2.set_value("process", process)
        virtual_snapshot2.set_value("context", context)
        virtual_snapshot2.set_value("snapshot_type", 'file')
        virtual_snapshot2.set_sobject(sobject2)
        virtual_snapshot2.set_value("version", version)

        type = 'ma'
        version = -1
        virtual_versionless_snapshot = Snapshot.create_new()
        virtual_snapshot_xml = '<snapshot process=\'%s\'><file type=\'%s\'/></snapshot>' % (process, type)
        virtual_versionless_snapshot.set_value("snapshot", virtual_snapshot_xml)
        virtual_versionless_snapshot.set_value("process", process)
        virtual_versionless_snapshot.set_value("context", context)
        virtual_versionless_snapshot.set_value("snapshot_type", 'file')
        virtual_versionless_snapshot.set_sobject(sobject2)
        virtual_versionless_snapshot.set_value("version", version)

        Container.put("Naming:cache", None)
        Container.put("Naming:cache:latest", None)
        Container.put("Naming:cache:current", None)
        Container.put("Naming:namings", None)
        name = Naming.get(sobject, virtual_snapshot)
        my.assertEquals(name.get_value('dir_naming'), '{project.code}/cut/{sobject.code}')

        virtual_snapshot.set_value('context', 'light/sub2')
        name = Naming.get(sobject, virtual_snapshot)
        my.assertEquals(name.get_value('dir_naming'), '{project.code}/light')
        
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        my.assertEquals(has, False)

        virtual_snapshot.set_value('context', 'asset/light')
        name = Naming.get(sobject, virtual_snapshot)
        my.assertEquals(name.get_value('dir_naming'), '{project.code}/cut')
        has = Naming.has_versionless(sobject, virtual_snapshot)
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        my.assertEquals(has, False)

        virtual_snapshot.set_value('context', 'model/sub1')
        name = Naming.get(sobject, virtual_snapshot)
        my.assertEquals(name.get_value('dir_naming'), '{project.code}/sub')
        has = Naming.has_versionless(sobject, virtual_snapshot)
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        my.assertEquals(has, False)

        virtual_snapshot.set_value('context', 'light/sub1')
        name = Naming.get(sobject, virtual_snapshot)

        my.assertEquals(name.get_value('dir_naming'), '{project.code}/light/sub1')
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        my.assertEquals(has, False)

        virtual_snapshot.set_value('context', 'unknown')
        name = Naming.get(sobject, virtual_snapshot)
        # should get the generic with snapshot_type, search_type in this case
        my.assertEquals(name.get_value('dir_naming'), '{project.code}/cut/generic_snapshot/{sobject.code}')
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        my.assertEquals(has, False)


        virtual_snapshot.set_value('context', 'icon')
        name = Naming.get(sobject, virtual_snapshot)
        # should get the chip_ICON in this case
        my.assertEquals(name.get_value('dir_naming'), '{project.code}/cut/chip_ICON/{sobject.code}')
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        my.assertEquals(has, False)
        
        sobject.set_value('name_first', 'peter')
        sobject.commit()
        name = Naming.get(sobject, virtual_snapshot)
        # should get the basic ICON in this case
        my.assertEquals(name.get_value('dir_naming'), '{project.code}/cut/ICON/{sobject.code}')
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        my.assertEquals(has, False)

        virtual_snapshot.set_value('snapshot_type', 'custom')
        virtual_snapshot.set_value('context', 'custom')
        name = Naming.get(sobject, virtual_snapshot)
        # should get the ultimate generic in this case
        my.assertEquals(name.get_value('dir_naming'), '{project.code}/cut/generic/{sobject.code}')
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        my.assertEquals(has, False)

        virtual_snapshot.set_value('snapshot_type', 'file')
        virtual_snapshot.set_value('context', 'super')
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        my.assertEquals(has, True)
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='current')
        my.assertEquals(has, False)

    
        has = Naming.has_versionless(sobject2, virtual_snapshot2, versionless='latest')
        my.assertEquals(has, True)
     

        naming_sobj = Naming.get(sobject2, virtual_snapshot2, versionless='latest', mode='check')
        my.assertEquals(naming_sobj.get_value('dir_naming'), \
            "{project.code}/cut/{snapshot.context}/VERSIONLESS/{sobject.code}")

        naming_sobj = Naming.get(sobject2, virtual_versionless_snapshot, mode='find')
        my.assertEquals(naming_sobj.get_value('dir_naming'), \
            "{project.code}/cut/{snapshot.context}/VERSIONLESS/{sobject.code}")

        has = Naming.has_versionless(sobject2, virtual_snapshot2, versionless='current')
        my.assertEquals(has, False)

        naming_sobj = Naming.get(sobject2, virtual_snapshot2, versionless='', mode='find')
        my.assertEquals(naming_sobj.get_value('dir_naming'), \
            "{project.code}/cut/{snapshot.context}/DEFAULT/{sobject.code}")


        # this is always true in theory when versionless is empty, but the source code doesn't make use of this mode
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='')
        my.assertEquals(has, True)
   
    def _test_checkin_type(my):
        my.assertEquals(my.auto_snapshot.get_version(), 2)
        dir_name = my.auto_snapshot.get_file_name_by_type('main')
        my.assertEquals(dir_name , 'naming_test_folder_naming_base_test_v002')
        
        dir_name = my.auto_snapshot2.get_file_name_by_type('main')

        my.assertEquals(1, my.auto_snapshot2.get_version())
        my.assertEquals(dir_name , '.tactic_test_naming_folder_test_v001')

        dir_name = my.auto_snapshot3.get_file_name_by_type('main')
        # this takes the auto generated name
        my.assertEquals(dir_name , 'naming_test_folder3_naming_base_test_v003')


        # this one would take into account of the new naming entry introduced in _test_get_naming
        # test a blank checkin_type
        dir_path4 = "./naming_test_folder4"
        checkin = FileCheckin(my.person, dir_path4, "main", context='naming_base_test', snapshot_type='directory', checkin_type='')
        checkin.execute()
        my.auto_snapshot4 = checkin.get_snapshot()
        dir_name = my.auto_snapshot4.get_file_name_by_type('main')
        lib_dir = my.auto_snapshot4.get_dir('relative')
        my.assertEquals(dir_name , 'generic_phil_v004')
        my.assertEquals(lib_dir , 'unittest/cut/generic/phil')




if __name__ == '__main__':
    unittest.main()



