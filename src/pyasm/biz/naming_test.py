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
from pyasm.prod.biz import Asset, ProdSetting
from file_naming import FileNaming
from dir_naming import DirNaming
from naming import NamingUtil, Naming
from pyasm.unittest import UnittestEnvironment, Sample3dEnvironment

class TestFileNaming(FileNaming):

    def unittest_person(self):

        context = self.snapshot.get_value("context")

        file_type = self.snapshot.get_file_type()
        parts = []

        asset_code = self.sobject.get_code()
        parts.append(asset_code)
        parts.append(file_type)
        parts.append('v%0.3d' %self.snapshot.get_version())
        filename = '_'.join(parts)
        ext = self.get_ext()
        if ext:
            filename = '%s%s' %(filename, ext)
        return filename

class TestFileNaming2(FileNaming):

        
    def unittest_person(self):
        '''try an empty file name'''
        return ''

class TestDirNaming(DirNaming):

    def unittest_person(self, dirs):
        context = self.snapshot.get_value("context")
        file_type = self.get_file_type()
        parts = []

        asset_code = self.sobject.get_code()
        dirs.append(asset_code)
        if self._file_object:
            file_name = self._file_object.get_file_name()
            file_ext = ''
            if file_name:
                from pyasm.biz import File
                file_ext = File.get_extension(file_name)
            dirs.append('%s.%s'%(file_ext, file_type))
        
        #dirs.append(file_type)
        dirs.append('v%0.3d' %self.snapshot.get_version())
        return dirs

class NamingTest(unittest.TestCase):

    def setUp(self):
        # start batch environment
        Batch()
        from pyasm.web.web_init import WebInit
        WebInit().execute()

        self.sample3d_env = Sample3dEnvironment(project_code='sample3d')
        self.sample3d_env.create()

        self.test_env = UnittestEnvironment()
        self.test_env.create()

    

        # set up the proper project_type, with the use the ProdDirNaming and ProdFileNaming
        search = Search('sthpw/project')
        search.add_filter('code', 'unittest')
        self.sobj = search.get_sobject()

        # store the original setting in your database
        self.original_proj_type_dict = {'dir_naming_cls': self.sobj.get_value('dir_naming_cls'),
                'file_naming_cls': self.sobj.get_value('file_naming_cls') }

        #self.transaction = Transaction.get(create=True)
        if self.sobj:
            self.sobj.set_value('dir_naming_cls', 'pyasm.prod.biz.ProdDirNaming')
            self.sobj.set_value('file_naming_cls', 'pyasm.prod.biz.ProdFileNaming')
            self.sobj.commit()
        else:
            self.sobj = SearchType.create('sthpw/project_type')
            self.sobj.set_value('dir_naming_cls', 'pyasm.prod.biz.ProdDirNaming')
            self.sobj.set_value('file_naming_cls', 'pyasm.prod.biz.ProdFileNaming')
            self.sobj.set_value('code', 'unittest')
            self.sobj.commit()

      


    def create_snapshot(self):
        # set up a real person and snapshot (as opposed to virtual)
        code = 'phil'
       
        self.person = SearchType.create( 'unittest/person' )
        self.person.set_value("code",code)
        self.person.set_value("name_first", "Philip")
        self.person.commit()


        # create a new test.txt file
        file_path = "./naming_test.txt"
        for i in range(0,4):
            file = open(file_path, 'w')
            file.write("whatever")
            file.close()
        checkin = FileCheckin(self.person, file_path, "main", context='naming_test')
        checkin.execute()
        self.snapshot = checkin.get_snapshot()

        # create another test_base.txt file
        file_path = "./naming_base_test.txt"
        for i in range(0,4):
            file = open(file_path, 'w')
            file.write("whatever")
            file.close()
        checkin = FileCheckin(self.person, file_path, "main", context='naming_base_test')
        checkin.execute()
        self.base_snapshot = checkin.get_snapshot()

        dir_path = "./naming_test_folder"
        dir_path2 = "./.tactic_test" # test . folder
        dir_path3 = "./naming_test_folder3"
        dir_path4 = "./naming_test_folder4"
        for path in [dir_path, dir_path2, dir_path3, dir_path4]:
            if not os.path.exists(path):
                os.makedirs(path)

        checkin = FileCheckin(self.person, dir_path, "main", context='naming_base_test', checkin_type='auto')
        checkin.execute()
        self.auto_snapshot = checkin.get_snapshot()
        checkin = FileCheckin(self.person, dir_path2, "main", context='naming_folder_test', snapshot_type='directory', checkin_type='auto')
        checkin.execute()
        self.auto_snapshot2 = checkin.get_snapshot()

        # test a blank checkin_type
        checkin = FileCheckin(self.person, dir_path3, "main", context='naming_base_test', snapshot_type='directory', checkin_type='')
        checkin.execute()
        self.auto_snapshot3 = checkin.get_snapshot()
    
    def test_all(self):
        
        self.transaction = Transaction.get(create=True)
        try:
            self.create_snapshot()

            self._test_base_alias()

            self._test_file_naming()
            self._test_file_naming_base()
            self._test_dir_naming()
            # this comes after test_dir_naming so the file_object doesn't get polluted
            self._test_file_naming_manual_version()
            self._test_get_naming()
            self._test_checkin_type()
            self._test_naming_util()
        finally:
            self.transaction.rollback()
            Project.set_project('unittest')

            self.test_env.delete()
            self.sample3d_env.delete()

        # reset the unittest project type to whatever it was
        """
        for key, value in self.original_proj_type_dict.items():
            self.sobj.set_value(key, value)
        self.sobj.commit()
        """


    def _test_base_alias(self):

        plugin_dir = Environment.get_web_dir(alias="plugins")
        self.assertEquals("/plugins", plugin_dir)

        plugin_dir = Environment.get_plugin_dir()
        plugin_dir2 = Environment.get_asset_dir(alias="plugins")
        self.assertEquals(plugin_dir, plugin_dir2)


    def clear_naming(self):
        Container.put("Naming:cache", None)
        Container.put("Naming:cache:latest", None)
        Container.put("Naming:cache:unittest:latest", None)
        Container.put("Naming:cache:current", None)
        Container.put("Naming:cache:unittest:current", None)
        Container.put("Naming:cache:unittest", None)
        Container.put("Naming:namings", None)

    def _test_naming_util(self):
       
        #self.clear_naming()
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

        virtual_snapshot.set_sobject(self.person)
        virtual_snapshot.set_value("version", version)

        file_name = "abc.txt"
        file_obj = File(File.SEARCH_TYPE)
        file_obj.set_value("file_name", file_name)
        
        for naming_expr in file_naming_expr1:
            file_name = naming_util.naming_to_file(naming_expr, self.person, virtual_snapshot, file=file_obj, file_type="main")
            self.assertEquals(file_name,'unittest__light__hi_abc.txt')

        for naming_expr in dir_naming_expr2:
            dir_name = naming_util.naming_to_dir(naming_expr, self.person, virtual_snapshot, file=file_obj, file_type="main")
            self.assertEquals(dir_name,'unittest/special/somedir/Philip')
    
    def _test_file_naming_manual_version(self):
       
        self.clear_naming()

        naming = SearchType.create('config/naming')
        naming.set_value('search_type','unittest/person')
        naming.set_value('context', 'naming_test')
        naming.set_value('dir_naming', '{project.code}/cut/{sobject.code}')
        naming.set_value('file_naming', '{sobject.code}_v{snapshot.version}.{ext}')
        naming.commit()

        from pyasm.common import Environment
        base_dir = Environment.get_asset_dir()
        
        preallocated = self.snapshot.get_preallocated_path(file_type='maya', file_name='what_v005.ma',ext='ma')
        self.assertEquals('%s/unittest/cut/phil/phil_v001.ma'%base_dir, preallocated)

        # now turn on manual_version
        naming.set_value('manual_version', True)
        naming.commit()

        self.clear_naming()
        preallocated = self.snapshot.get_preallocated_path(file_type='maya', file_name='what_v005.ma',ext='ma')
        self.assertEquals('%s/unittest/cut/phil/phil_v005.ma'%base_dir, preallocated)
        
        # Uppercase V and more digits
        preallocated = self.snapshot.get_preallocated_path(file_type='maya', file_name='what_V0010.ma',ext='ma')
        self.assertEquals('%s/unittest/cut/phil/phil_v010.ma'%base_dir, preallocated)
        #self.snapshot.commit()

        # zero or negative version is ignored
        # create a new manual version test.txt file
        file_path = "./naming_v0000_test.txt"
        for i in range(0,4):
            file = open(file_path, 'w')
            file.write("whatever")
            file.close()
        checkin = FileCheckin(self.person, file_path, "main", context='naming_test')
        checkin.execute()
        self.snapshot = checkin.get_snapshot()
        self.assertEquals(11, self.snapshot.get_version())

        # zero or negative version is ignored
        # create a new manual version test.txt file
        file_path = "./naming_v-23_test.txt"
        for i in range(0,4):
            file = open(file_path, 'w')
            file.write("whatever")
            file.close()
        checkin = FileCheckin(self.person, file_path, "main", context='naming_test')
        checkin.execute()
        self.snapshot = checkin.get_snapshot()
        self.assertEquals(12, self.snapshot.get_version())
        file_path = "./naming_v025_test.txt"
        for i in range(0,4):
            file = open(file_path, 'w')
            file.write("whatever")
            file.close()
        checkin = FileCheckin(self.person, file_path, "main", context='naming_test')
        checkin.execute()
        self.snapshot = checkin.get_snapshot()
        self.assertEquals(25, self.snapshot.get_version())


        naming.delete()

        self.clear_naming()


    def _test_file_naming_base(self):
       

        naming = SearchType.create('config/naming')
        naming.set_value('search_type','unittest/person')
        naming.set_value('context', 'naming_base_test')
        naming.set_value('dir_naming', '{project.code}/cut/{sobject.code}')
        naming.set_value('file_naming', '{sobject.code}_v{snapshot.version}_{basefile}.{ext}')
        naming.commit()
        
        self.clear_naming()

        # auto_snapshot is at v2
        preallocated = self.auto_snapshot.get_preallocated_path(file_type='some_dir', file_name='racoon',ext=None)
        from pyasm.common import Environment
        base_dir = Environment.get_asset_dir()
        self.assertEquals('%s/unittest/cut/phil/phil_v002_racoon'%base_dir, preallocated)
        
        preallocated = self.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon',ext=None)
        self.assertEquals('%s/unittest/cut/phil/phil_v001_racoon'%base_dir, preallocated)
        
        preallocated = self.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon.jpg',ext='jpg')
        self.assertEquals('%s/unittest/cut/phil/phil_v001_racoon.jpg'%base_dir, preallocated)


        preallocated = self.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon2.PNG')
        self.assertEquals('%s/unittest/cut/phil/phil_v001_racoon2.PNG'%base_dir, preallocated)

        
        # test file expression
        naming.set_value('file_naming', '{@GET(.code)}_v{@GET(snapshot.version)}_{$BASEFILE}.{$EXT}')
        naming.commit()
        self.clear_naming()
        
        preallocated = self.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon3.jpg',ext='jpg')
        self.assertEquals('%s/unittest/cut/phil/phil_v1_racoon3.jpg'%base_dir, preallocated)

        preallocated = self.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon4.PNG')
        self.assertEquals('%s/unittest/cut/phil/phil_v1_racoon4.PNG'%base_dir, preallocated)


        # test dir expression
        naming.set_value('dir_naming', '{$PROJECT}/exp_cut/{@GET(.code)}')
        naming.commit()
        self.clear_naming()

        preallocated = self.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon same.iff',ext='iff')
        self.assertEquals('%s/unittest/exp_cut/phil/phil_v1_racoon same.iff'%base_dir, preallocated)

        # file name clean-up is disabled in 4.2: the actual check-in logic would not replace " " with "_"
        preallocated = self.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon 5.PNG')
        self.assertEquals('%s/unittest/exp_cut/phil/phil_v1_racoon 5.PNG'%base_dir, preallocated)
 
        # this one does not need clean-up
        preallocated = self.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon_5.PNG')
        self.assertEquals('%s/unittest/exp_cut/phil/phil_v1_racoon_5.PNG'%base_dir, preallocated)


        # test dir expression 2

        naming.set_value('dir_naming', '{$PROJECT}/3D/QC/ShotWork/playblast/ByDate/{$TODAY,|([^\s]+)| }/{@GET(.name_first)}')

        naming.commit()
        self.clear_naming()

        preallocated = self.base_snapshot.get_preallocated_path(file_type='pic', file_name='racoon same.iff',ext='iff')

        today = datetime.datetime.today()
        today = datetime.datetime(today.year, today.month, today.day)
        today = today.strftime("%Y-%m-%d")
        self.assertEquals('%s/unittest/3D/QC/ShotWork/playblast/ByDate/%s/Philip/phil_v1_racoon same.iff'%(base_dir, today), preallocated)

        naming.delete()

        self.clear_naming()

    def _test_file_naming(self):
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
        self.assertEquals(expected_file_name, file_name)


        # try a default directory name

        file_obj.set_value("file_name", "test_dir")
        file_obj.set_value("base_type", "directory")
        file_naming.set_file_object(file_obj)
        
        # this should adopt the original dir name in the prefix
        expected_file_name = 'test_dir_%s_v%0.3d' %(context,version)
        file_name = file_naming.get_default()
        self.assertEquals(expected_file_name, file_name)

        #2 try a different search_type unittest/person
        version = 9
        
        
        file_obj.set_value("base_type", "file")
        # change a different input file name
        file_obj.set_value('file_name','some_maya_model.ma') 
        
        # use a real snapshot
        virtual_snapshot.set_sobject(self.person)
        virtual_snapshot.set_value("version", version)
        
        # change to the test file naming class
        self.sobj.set_value('file_naming_cls', 'pyasm.biz.naming_test.TestFileNaming')
        self.sobj.commit()
        Project.set_project('unittest')
        file_naming = Project.get_file_naming()
        file_naming.set_sobject(self.person)
        file_naming.set_snapshot(virtual_snapshot)
        file_naming.set_file_object(file_obj)
        file_name = file_naming.get_file_name()

        expected_file_name = 'phil_main_v009.ma'
        self.assertEquals(expected_file_name, file_name)

        # get_preallocated_path
        type = 'ma'
        #file_obj.set_value('type', type)
        #file_naming.set_file_object(file_obj)

        preallocated = self.snapshot.get_preallocated_path(file_type='maya', file_name='what.ma',ext='ma')
        preallocated_file_name = os.path.basename(preallocated)
        self.assertEquals("phil_main_v001.ma", preallocated_file_name)

        preallocated = self.snapshot.get_preallocated_path(file_type='houdini', file_name='what.otl',ext='otl')
        preallocated_file_name = os.path.basename(preallocated)
        self.assertEquals("phil_main_v001.otl", preallocated_file_name)

        preallocated = self.snapshot.get_preallocated_path(file_type='houdini', file_name='what_is.otl', ext='hipnc')
        preallocated_file_name = os.path.basename(preallocated)
        self.assertEquals("phil_main_v001.hipnc", preallocated_file_name)


        # try an empty file naming
        # change to the test file naming class
        self.sobj.set_value('file_naming_cls', 'pyasm.biz.naming_test.TestFileNaming2')
        self.sobj.commit()

        Project.set_project('unittest')
        file_naming = Project.get_file_naming()
        file_naming.set_sobject(self.person)
        file_naming.set_snapshot(virtual_snapshot)
        file_naming.set_file_object(file_obj)
        file_name = file_naming.get_file_name()
       
        preallocated = self.snapshot.get_preallocated_path(file_type='houdini', file_name='what_is.otl', ext='hipnc')

        if not os.path.exists(preallocated):
            os.makedirs(preallocated)
         
        from client.tactic_client_lib import TacticServerStub
        client = TacticServerStub.get()
        
        if os.path.isdir(preallocated):
            rtn = client.add_directory(self.snapshot.get_code(), preallocated, 'houdini', mode='preallocate')
        else:
            rtn = client.add_file(self.snapshot.get_code(), preallocated, 'houdini', mode='preallocate')
        rtn = client.get_snapshot(SearchKey.get_by_sobject(self.snapshot.get_parent()), context = 'naming_test', version = 1, include_files=True)
        files =  rtn.get('__files__')
        
        # assuming the file is ordered by code
        # the 1st file obj is a file and 2nd file obj is a directory
        for idx, file in enumerate(files):
            if idx ==0:
                self.assertEquals(file.get('type'), 'main')
                self.assertEquals(file.get('base_type'), 'file')
                self.assertEquals(file.get('file_name'), 'naming_test_naming_test_v001.txt')
                
            elif idx ==1:
                self.assertEquals(file.get('type'), 'houdini')
                self.assertEquals(file.get('base_type'), 'directory')
                self.assertEquals(file.get('md5'), '')
                self.assertEquals(file.get('file_name'), '')

    def _test_dir_naming(self):

        # change to the test dir naming class
        self.sobj.set_value('dir_naming_cls', 'pyasm.biz.naming_test.TestDirNaming')
        self.sobj.commit()

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
        self.assertEquals(expected_dir_name, dir_name)
        
        lib_paths = virtual_snapshot.get_all_lib_paths()
        sand_paths = virtual_snapshot.get_all_lib_paths(mode='sandbox')
        client_paths = virtual_snapshot.get_all_lib_paths(mode='client_repo')
       
        base_dir = Config.get_value("checkin", "asset_base_dir", sub_key='default')
        sand_base_dir = dir_naming.get_base_dir(protocol='sandbox')
        client_base_dir = dir_naming.get_base_dir(protocol='client_repo')
       

        self.assertEquals(lib_paths[0].startswith('%s%s'%(base_dir, expected_dir_name2)), True)
        self.assertEquals(sand_paths[0].startswith('%s%s'%(sand_base_dir[0], expected_dir_name2)), True)
        self.assertEquals(client_paths[0].startswith('%s%s'%(client_base_dir[0], expected_dir_name2)), True)

        # 2  get_preallocated_path
        # set version 1 here since it's the first snapshot for this sobject. 
        # without a virtual file_object, the file_name is empty, and so the dir ma.maya is now .maya
        self.assertEquals("phil/.maya/v001", self.get_preallocated_dir()) 
        
        # switch back to regular file naming
        self.sobj.set_value('file_naming_cls', 'pyasm.biz.naming_test.TestFileNaming')
        self.sobj.commit()

        self.assertEquals("phil/ma.maya/v001", self.get_preallocated_dir()) 
        



    def get_preallocated_dir(self):
        preallocated = self.snapshot.get_preallocated_path(file_type='maya', file_name='what.ma',ext='ma')
        preallocated_dir_name = os.path.dirname(preallocated)
        preallocated_dir_name = preallocated_dir_name.replace('%s/' %Environment.get_asset_dir(), '')
        # remove the base part
        preallocated_dir_names = preallocated_dir_name.split('/')
        
        preallocated_dir_name = '/'.join(preallocated_dir_names)
        return preallocated_dir_name





    def _test_get_naming(self):
     
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
        naming.set_value('checkin_type', 'auto')
        naming.set_value('dir_naming', '{project.code}/cut/generic/{sobject.code}')
        naming.set_value('file_naming', 'generic_{sobject.code}_v{snapshot.version}.{ext}')
        naming.commit()

        # generic with nothing    
        naming = SearchType.create('config/naming')
        naming.set_value('search_type', 'unittest/person')
        naming.set_value('context', 'naming_base_test')
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
        self.assertEquals(message, 'sandbox_dir_name should not end with /')

        naming7 = SearchType.create('config/naming')
        naming7.set_value('dir_naming', '{$PROJECT}/{@GET(.id)}/')
        try:
            naming7.commit()
        except TacticException, e:
            message = 'dir_name should not end with /'
        else:
            message = 'Pass'
        self.assertEquals(message, 'dir_name should not end with /')

        naming8 = SearchType.create('config/naming')
        naming8.set_value('sandbox_dir_naming', '{$PROJECT}/{@GET(.id)}')
        try:
            naming8.commit()
        except TacticException, e:
            message = 'sandbox_dir_name should not end with /'
        else:
            message = 'Pass'
        self.assertEquals(message, 'Pass')
        
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
        self.assertEquals(name.get_value('dir_naming'), '{project.code}/cut/{sobject.code}')

        virtual_snapshot.set_value('context', 'light/sub2')
        name = Naming.get(sobject, virtual_snapshot)
        self.assertEquals(name.get_value('dir_naming'), '{project.code}/light')
        
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        self.assertEquals(has, False)

        virtual_snapshot.set_value('context', 'asset/light')
        name = Naming.get(sobject, virtual_snapshot)
        self.assertEquals(name.get_value('dir_naming'), '{project.code}/cut')
        has = Naming.has_versionless(sobject, virtual_snapshot)
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        self.assertEquals(has, False)

        virtual_snapshot.set_value('context', 'model/sub1')
        name = Naming.get(sobject, virtual_snapshot)
        self.assertEquals(name.get_value('dir_naming'), '{project.code}/sub')
        has = Naming.has_versionless(sobject, virtual_snapshot)
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        self.assertEquals(has, False)

        virtual_snapshot.set_value('context', 'light/sub1')
        name = Naming.get(sobject, virtual_snapshot)

        self.assertEquals(name.get_value('dir_naming'), '{project.code}/light/sub1')
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        self.assertEquals(has, False)

        virtual_snapshot.set_value('context', 'unknown')
        name = Naming.get(sobject, virtual_snapshot)
        # should get the generic with snapshot_type, search_type in this case
        self.assertEquals(name.get_value('dir_naming'), '{project.code}/cut/generic_snapshot/{sobject.code}')
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        self.assertEquals(has, False)


        virtual_snapshot.set_value('context', 'icon')
        name = Naming.get(sobject, virtual_snapshot)
        # should get the chip_ICON in this case
        self.assertEquals(name.get_value('dir_naming'), '{project.code}/cut/chip_ICON/{sobject.code}')
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        self.assertEquals(has, False)
        
        sobject.set_value('name_first', 'peter')
        sobject.commit()
        name = Naming.get(sobject, virtual_snapshot)
        # should get the basic ICON in this case
        self.assertEquals(name.get_value('dir_naming'), '{project.code}/cut/ICON/{sobject.code}')
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        self.assertEquals(has, False)

        virtual_snapshot.set_value('snapshot_type', 'custom')
        virtual_snapshot.set_value('context', 'custom')
        name = Naming.get(sobject, virtual_snapshot)
        # should get the ultimate generic in this case
        self.assertEquals(name.get_value('dir_naming'), '{project.code}/cut/generic/{sobject.code}')
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        self.assertEquals(has, False)

        virtual_snapshot.set_value('snapshot_type', 'file')
        virtual_snapshot.set_value('context', 'super')
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='latest')
        self.assertEquals(has, True)
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='current')
        self.assertEquals(has, False)

    
        has = Naming.has_versionless(sobject2, virtual_snapshot2, versionless='latest')
        self.assertEquals(has, True)
     

        naming_sobj = Naming.get(sobject2, virtual_snapshot2, versionless='latest', mode='check')
        self.assertEquals(naming_sobj.get_value('dir_naming'), \
            "{project.code}/cut/{snapshot.context}/VERSIONLESS/{sobject.code}")

        naming_sobj = Naming.get(sobject2, virtual_versionless_snapshot, mode='find')
        self.assertEquals(naming_sobj.get_value('dir_naming'), \
            "{project.code}/cut/{snapshot.context}/VERSIONLESS/{sobject.code}")

        has = Naming.has_versionless(sobject2, virtual_snapshot2, versionless='current')
        self.assertEquals(has, False)

        naming_sobj = Naming.get(sobject2, virtual_snapshot2, versionless='', mode='find')
        self.assertEquals(naming_sobj.get_value('dir_naming'), \
            "{project.code}/cut/{snapshot.context}/DEFAULT/{sobject.code}")


        # this is always true in theory when versionless is empty, but the source code doesn't make use of this mode
        has = Naming.has_versionless(sobject, virtual_snapshot, versionless='')
        self.assertEquals(has, True)
   
    def _test_checkin_type(self):
        self.assertEquals(self.auto_snapshot.get_version(), 2)
        dir_name = self.auto_snapshot.get_file_name_by_type('main')
        self.assertEquals(dir_name , 'naming_test_folder_naming_base_test_v002')
        
        dir_name = self.auto_snapshot2.get_file_name_by_type('main')

        self.assertEquals(1, self.auto_snapshot2.get_version())
        self.assertEquals(dir_name , '.tactic_test_naming_folder_test_v001')

        dir_name = self.auto_snapshot3.get_file_name_by_type('main')
        # this takes the auto generated name
        self.assertEquals(dir_name , 'naming_test_folder3_naming_base_test_v003')


        # this one would take into account of the new naming entry introduced in _test_get_naming
        # test a blank checkin_type
        dir_path4 = "./naming_test_folder4"
        checkin = FileCheckin(self.person, dir_path4, "main", context='naming_base_test', snapshot_type='directory', checkin_type='', mode='copy')
        checkin.execute()
        self.auto_snapshot4 = checkin.get_snapshot()
        dir_name = self.auto_snapshot4.get_file_name_by_type('main')
        lib_dir = self.auto_snapshot4.get_dir('relative')
        self.assertEquals(dir_name , 'generic_phil_v004')
        self.assertEquals(lib_dir , 'unittest/cut/generic/phil')
        snapshot_xml = self.auto_snapshot4.get_xml_value('snapshot')
        checkin_type = snapshot_xml.get_nodes_attr('/snapshot','checkin_type')
        # un-specified checkin_type with a matching naming will default to "strict"
        self.assertEquals('strict', checkin_type[0])

        # this should pick the auto checkin_type naming convention with the _OO at the end of context
        checkin = FileCheckin(self.person, dir_path4, "main", context='naming_base_test_OO', snapshot_type='directory', checkin_type='', mode='copy')
        checkin.execute()
        self.auto_snapshot4 = checkin.get_snapshot()
        dir_name = self.auto_snapshot4.get_file_name_by_type('main')
        lib_dir = self.auto_snapshot4.get_dir('relative')
        self.assertEquals(dir_name , 'generic_phil_v001')
        self.assertEquals(lib_dir , 'unittest/cut/generic/phil')
        snapshot_xml = self.auto_snapshot4.get_xml_value('snapshot')
        checkin_type = snapshot_xml.get_nodes_attr('/snapshot','checkin_type')
        # un-specified checkin_type with a matching naming will default to "strict"
        self.assertEquals('auto', checkin_type[0])


        dir_path4 = "./naming_test_folder4"
        checkin = FileCheckin(self.person, dir_path4, "main", context='naming_base_test', snapshot_type='directory', checkin_type='auto')
        checkin.execute()
        self.auto_snapshot5 = checkin.get_snapshot()
        snapshot_xml = self.auto_snapshot5.get_xml_value('snapshot')
        checkin_type = snapshot_xml.get_nodes_attr('/snapshot','checkin_type')
        
        dir_name = self.auto_snapshot5.get_file_name_by_type('main')
        lib_dir = self.auto_snapshot5.get_dir('relative')
        self.assertEquals(dir_name , 'generic_phil_v005')
        self.assertEquals(lib_dir , 'unittest/cut/generic/phil')
        self.assertEquals('auto', checkin_type[0])

        versionless = Snapshot.get_versionless(self.auto_snapshot5.get_value('search_type'), self.auto_snapshot5.get_value('search_id'), 'naming_base_test', mode='latest', create=False)

        dir_name = versionless.get_file_name_by_type('main')
        lib_dir = versionless.get_dir('relative')
        self.assertEquals(dir_name , 'generic_phil')
        self.assertEquals(lib_dir , 'unittest/cut/generic/phil')
        path = versionless.get_lib_path_by_type()





if __name__ == '__main__':
    unittest.main()



