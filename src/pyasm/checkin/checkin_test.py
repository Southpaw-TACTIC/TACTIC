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

import tacticenv
import re
import os,unittest, shutil, sys

from pyasm.unittest import *

from pyasm.common import Environment, Config, Common, Container, Xml
from pyasm.command import Command, UndoCmd
from pyasm.search import Transaction, SearchType, Search
from pyasm.security import Batch
from pyasm.checkin import *
from pyasm.biz import File, FileGroup, Project, FileRange, Snapshot, Naming

from pyasm.unittest import UnittestEnvironment

class CheckinTest(unittest.TestCase, Command):

    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        Command.__init__(self)


    def test_all(self):
        '''entry point function'''
        self.description = "Checkin unit test"
        self.errors = []

        Batch()

        # FIXME: this is needed for the triggers to be registerd. These
        # triggers have nothing to do with the web
        from pyasm.web import WebInit
        WebInit().execute()


        test_env = UnittestEnvironment()
        test_env.create()
        self.transaction = Transaction.get(create=True)

        Project.set_project("unittest")
       
        try:
            #Command.execute_cmd(self)

            # undo the command
            #undo = UndoCmd()
            #undo.execute()
            self.execute()

        finally:
            self.transaction.rollback()
            test_env.delete()



    def execute(self):

        search = Search("sthpw/snapshot")

        self.person = Person.create( "Unit", "Test",
                "ComputerWorld", "unittest/checkin_test")

       
        
        self._test_checkin()
        self._test_copycheckin()
        self._test_groupcheckin()
        self._test_inplace_checkin()
        self._test_preallocation_checkin()
        self._test_get_children()
        self._test_file_owner()

        self._test_symlink()
        self._test_with_naming()
        
        self._test_auto_checkin()
        self._test_strict_checkin()
   
        self._test_base_dir_alias()

        # clear the xml and config cache introduced by test_base_dir_alias
        data = {}
        Container.put(Config.CONFIG_KEY, data)


        Xml.XML_FILE_CACHE = {}
        Xml.XML_FILE_MTIME = {}


    def clear_naming(self):
        Container.put("Naming:cache", None)
        Container.put("Naming:cache:unittest:latest", None)
        Container.put("Naming:cache:unittest:current", None)
        Container.put("Naming:cache:unittest", None)
        Container.put("Naming:namings", None)

    def _test_copycheckin(self):

        # create a new copy_test.txt file
        file_path = "./copy_test.txt"
        file = open(file_path, 'w')
        file.write("copy contents")
        file.close()

        file_paths = [file_path]
        file_types = ['main']
        context = "publish"
        from pyasm.checkin import FileCheckin
        checkin = FileCheckin(
                    self.person,
                    file_paths=file_paths,
                    file_types=file_types,
                    context=context,
                    mode="copy"
            )
        checkin.execute()
        self.assertEqual(True, os.path.exists(file_path) )

        snap = checkin.get_snapshot()
        file_obj = snap.get_file_by_type('main')
        file_name = file_obj.get_file_name()
        self.assertEqual(file_name, 'copy_test_publish_v002.txt')

    def _test_checkin(self):

        # create a new test.txt file
        file_path = "./test.txt"
        file = open(file_path, 'w')
        file.write("whatever")
        file.close()

        checkin = FileCheckin(self.person, file_path, "test")
        checkin.execute()

        # check that the file exists
        snapshot = checkin.get_snapshot()
        xml = snapshot.get_xml_value("snapshot")
        file_code = xml.get_value("snapshot/file/@file_code")
        file_name = xml.get_value("snapshot/file/@name")

        self.assertNotEqual(None, file)

        lib_path = "%s/%s" % (snapshot.get_lib_dir(),file_name)
        self.assertEqual(True, os.path.exists(lib_path) )

        #print "relative_dir: ", snapshot.get_relative_dir()



    def _test_groupcheckin(self):
        
        # FIXME: can't find maya_render.####.iff
        return


        file_path = "./maya_render.####.iff"
        range = FileRange(1, 12)

        # create new test files
        expanded_paths = FileGroup.expand_paths(file_path, range)
        for expanded_path in expanded_paths:
            file = open(expanded_path, 'w')
            file.write("file: %s" % expanded_path)
            file.close()


        # checkin the frames
        file_types = ["main"]
        file_paths = [file_path]

        checkin = FileGroupCheckin(self.person, file_paths, file_types, range, \
            column="frames")
        checkin.execute()


        # delete the test files
        for expanded_path in expanded_paths:
            os.unlink(expanded_path)



    def _test_inplace_checkin(self):

        # create a new test.txt file
        tmp_dir = Environment.get_tmp_dir()
        dir = "%s/temp" % tmp_dir
        if not os.path.exists(dir):
            os.makedirs(dir)
        file_path = "%s/test_inplace.txt" % dir

        if os.path.exists(file_path):
            os.unlink(file_path)

        file = open(file_path, 'w')
        file.write("whatever")
        file.close() 


        # inplace checkin: tell tactic that this is the correct path
        mode = "inplace"
        base_dir = tmp_dir
        context = "inplace"
        checkin = FileCheckin(self.person, file_path, context=context, mode=mode)
        checkin.execute()
        snapshot = checkin.get_snapshot()

        file_code = snapshot.get_file_code_by_type("main")
        file_object = File.get_by_code(file_code)

        relative_dir = file_object.get_value("relative_dir")
        # The relative dir is empty if the file is outside the repository
        self.assertEqual("", relative_dir)

        lib_dir = snapshot.get_lib_dir(file_type="main")
        file_name = snapshot.get_file_name_by_type("main")
        lib_path = "%s/%s" % (lib_dir, file_name)
        self.assertEqual( True, os.path.exists(lib_path) )
        self.assertEqual( file_path, lib_path)




        # check in a file alredy in the repository
        asset_dir = Config.get_value("checkin", "asset_base_dir", sub_key="default")
        file_path2 = "%s/unittest/text.txt" % asset_dir

        file = open(file_path2, 'w')
        file.write("whatever")
        file.close() 

        checkin = FileCheckin(self.person, file_path2, context=context, mode=mode)
        checkin.execute()
        snapshot = checkin.get_snapshot()

        file_code = snapshot.get_file_code_by_type("main")
        file_object = File.get_by_code(file_code)

        # check that the relative dir is as expected
        relative_dir = file_object.get_value("relative_dir")
        self.assertEqual( relative_dir, "unittest" )

        # check that the path returned correctly
        lib_path = snapshot.get_path_by_type("main")
        self.assertEqual( file_path2, lib_path )

        if os.path.exists(file_path):
            os.unlink(file_path)
        if os.path.exists(file_path2):
            os.unlink(file_path2)






    def _test_preallocation_checkin(self):
        """
        Test preallocation of empty snapshots and sequences, and creating and adding a file(s) to the snapshot/sequence.

        """

        snapshot_type="file"
        context="preallocation"
        file_name = 'whatever.jpg'
        file_type = 'jpg'


        # create an empty snapshot
        snapshot = Snapshot.create(self.person, snapshot_type=snapshot_type, context=context)

        # preallocate with no name or type
        path = snapshot.get_preallocated_path()
        server = Config.get_value("install", "server")

        expected = "%s/preallocation/versions" % (self.person.get_code())

        self.assertEqual(True, path.endswith( expected ) )

        # preallocate with a file name and file type
        # since it's meant for FileAppendCheckin, the checkin_type should be 'strict'
        path = snapshot.get_preallocated_path(file_type, file_name, checkin_type='strict')
        if server:
            self.assertEqual(True, None != re.search('unittest/person/\w+/preallocation/whatever_preallocation_\w+_v001.jpg$', path) )
        else:
            self.assertEqual(True, None != re.search('unittest/person/\w+/preallocation/whatever_preallocation_v001.jpg$', path) )

        # create a file directly in the path location and register in
        # transaction
        f = open(path, 'wb')
        f.write(b"wowow")
        f.close()

        # add this file to the snapshot and force the name
        snapshot_code = snapshot.get_code()
        checkin = FileAppendCheckin(snapshot_code, [path], [file_type], keep_file_name=True, mode='preallocate')
        checkin.execute()

        # check that it worked
        snapshot = checkin.get_snapshot()
        lib_dir = snapshot.get_lib_dir()
        file_name = snapshot.get_file_name_by_type(file_type)
        self.assertEqual(True, os.path.exists("%s/%s" % (lib_dir, file_name) ) )


        # test preallocation on a sequence
        file_name = "images_%0.4d.png"
        file_type = 'sequence'
        file_range = FileRange(1, 5)

        # should specify strict checkin_type for Append checkin after
        path = snapshot.get_preallocated_path(file_type=file_type, file_name=file_name, checkin_type='strict')
        # imitate a render by building files directly to the path
        for i in range(1,6):
            cur_path = path % i
            f = open(cur_path, 'wb')
            f.write(b"wowow")
            f.close()

        # register these files
        snapshot_code = snapshot.get_code()

        # should specify strict checkin_type for Append checkin
        checkin = FileGroupAppendCheckin(snapshot_code, [path], [file_type], file_range, \
                keep_file_name=True, mode='preallocate', checkin_type='strict')
        checkin.execute()

        snapshot = checkin.get_snapshot()

        # get the file paths
        file_names = snapshot.get_expanded_file_names(file_type)
        lib_dir = snapshot.get_lib_dir()
        for file_name in file_names:
            path = "%s/%s" % (lib_dir, file_name)
            self.assertEqual(True, os.path.exists(path)) 
        


    def _test_get_children(self):
        '''
        Test to make sure get_all_children is able to get all the snapshots
        '''

        return
        snapshots = self.person.get_all_children("sthpw/snapshot")
        #for snap in snapshots:
        #    print snap.get_version() ,  snap.get_description()
        # 2 versionless + 5 new snapshots = 7
        num_snapshots = 7
        self.assertEqual(num_snapshots, len(snapshots))



    def _test_file_owner(self):
        # FIXME: this test has hard coded st_uids that only work on very
        # specific conditions
        return

        if os.name == 'nt':
            return
        # create a new test.txt file
        file_path = "./test2.txt"
        file = open(file_path, 'w')
        file.write("whatever")
        file.close()
        # owned by root
        os.system('echo south123paw | sudo -S chown root.root \"%s\"'%file_path)

        stat = os.stat(file_path)
        self.assertEqual(stat.st_uid, 0)

        checkin = FileCheckin(self.person, file_path, "test")
        checkin.execute()

        # check that the file exists
        snapshot = checkin.get_snapshot()
        xml = snapshot.get_xml_value("snapshot")
        file_code = xml.get_value("snapshot/file/@file_code")
        file_name = xml.get_value("snapshot/file/@name")

        self.assertNotEqual(None, file)

        lib_path = "%s/%s" % (snapshot.get_lib_dir(),file_name)
        self.assertEqual(True, os.path.exists(lib_path) )
        stat = os.stat(lib_path)
        if Config.get_value("checkin", "sudo_no_password") == 'true': 
            self.assertEqual(stat.st_uid, 48)
        else:
            # if not set, it will remain owned by root
            self.assertEqual(stat.st_uid, 0)




    def _test_symlink(self):
        """
        Tests versionless snapshot and symbolic links.
        """

        if os.name == 'nt':
            return

        # create a new test.txt file
        file_path = "./symlink.txt"
        file = open(file_path, 'w')
        file.write("symlink test")
        file.close()

        file_path2 = "./symlink_append.txt"
        file = open(file_path2, 'w')
        file.write("append test")
        file.close()


        checkin = FileCheckin(self.person, file_path, context="sym_test", checkin_type='auto')
        checkin.execute()
        snap = checkin.get_snapshot()
        versionless_snap = Snapshot.get_versionless(self.person.get_search_type(), self.person.get_id(), "sym_test", mode='latest', create=False)
        self.assertEqual(True, isinstance(versionless_snap, Snapshot))

        main_lib_path = snap.get_lib_path_by_type('main')
        self.assertEqual(main_lib_path.endswith('/sym_test/versions/symlink_sym_test_v001.txt'), True)
        if versionless_snap:
            lib_path =versionless_snap.get_lib_path_by_type('main')
            self.assertEqual(True, os.path.exists(lib_path)) 
            rel_path = os.readlink(lib_path)
            lib_dir = os.path.dirname(lib_path)

            # this is essentially handle_link() in FileUndo class
            wd = os.getcwd()
            os.chdir(lib_dir)
            real_path = os.path.join(lib_dir, os.path.abspath(rel_path))
            # lib_path points to real_path

            expected_rel_path  = Common.relative_path(lib_path, real_path)
            self.assertEqual(True, os.path.exists(real_path))
            self.assertEqual(expected_rel_path, rel_path)
            os.chdir(wd)

        # if not inplace or preallocate mode, keep_file_name should be False
        checkin = FileAppendCheckin(snap.get_code(), [file_path2], file_types=['add'], keep_file_name=False, checkin_type='auto')
        checkin.execute()
        snap = checkin.get_snapshot()
        main_lib_path = snap.get_lib_path_by_type('add')
        self.assertEqual(snap.get_value('is_current'), True)
        self.assertEqual(snap.get_value('is_latest'), True)
        self.assertEqual(main_lib_path.endswith('/sym_test/versions/symlink_append_sym_test_v001.txt'), True)
        versionless_snap = Snapshot.get_versionless(self.person.get_search_type(), self.person.get_id(), "sym_test", mode='latest', create=False)
        if versionless_snap:
            lib_path = versionless_snap.get_lib_path_by_type('add')
            self.assertEqual(lib_path.endswith('/sym_test/symlink_append_sym_test.txt'), True)
            self.assertEqual(os.path.exists(lib_path), True)



    def _test_auto_checkin(self):
        """
        Tests file checkin and correctness/functionality of snapshots for multiple subdirectories.
        """

        server = Config.get_value("install", "server")
        process = "process"
        person_code = self.person.get_code()

        filename = "filename.jpg"

        process = "process"

        subdirs = [
            '', '', # do 2 checkins
            'subdir',
            'subdir/subsubdir'
        ]

        for i, subdir in enumerate(subdirs):

            if subdir:
                context = "%s/%s/%s" % (process, subdir, filename)
            else:
                context = "%s/%s" % (process, filename)

            # create a new test.txt file
            file_path = "./%s" % filename
            file = open(file_path, 'w')
            file.write("test")
            file.close()


            #import time
            #start = time.time()

            checkin = FileCheckin(self.person, file_path, context=context, checkin_type='auto')
            checkin.execute()

            #print "time: ", time.time() - start
            #print "---"


            # check the returned snapshot
            snapshot = checkin.get_snapshot()
            self.assertEqual(context, snapshot.get_value("context") )
            if i != 1: # the second checkin is version 2
                version = 1
                self.assertEqual(1, snapshot.get_value("version") )
            else:
                version = 2
            self.assertEqual(version, snapshot.get_value("version") )

            # check the file object data
            file_objects = snapshot.get_all_file_objects()
            self.assertEqual(1, len(file_objects))
            file_object = file_objects[0]
            repo_filename = file_object.get_value("file_name")

            if server:
                expected = "filename_process_%s_v%0.3d.jpg" % (server, version)
            else:
                expected = "filename_process_v%0.3d.jpg" % (version)
            self.assertEqual(expected, repo_filename)

            relative_dir = file_object.get_value("relative_dir")
            if subdir:
                expected = "unittest/person/%s/process/versions/%s" % (person_code, subdir)
            else:
                expected = "unittest/person/%s/process/versions" % person_code
            self.assertEqual(expected, relative_dir)

            asset_dir = Config.get_value("checkin", "asset_base_dir", sub_key="default")
            path = "%s/%s/%s" % (asset_dir, relative_dir, repo_filename)


            # make sure the path from the snapshot is correct
            snapshot_path = snapshot.get_path_by_type("main")
            self.assertEqual(path, snapshot_path)


            exists = os.path.exists(path)
            self.assertEqual(True, exists)


            # check that a versionless has been created
            versionless = Snapshot.get_versionless(self.person.get_search_type(), self.person.get_id(), context, mode='latest', create=False)

            self.assertNotEqual( None, versionless)

            self.assertEqual(-1, versionless.get_value("version") )

            versionless_path = versionless.get_path_by_type("main", "lib")
            versionless_dir = os.path.dirname(versionless_path)

            # test that it is a link
            lexists = os.path.lexists(versionless_path)
            self.assertEqual(True, lexists)

            # check the real path links to the versioned path
            real_path = os.path.realpath(versionless_path)
            self.assertEqual(real_path, path)

            # check that it actually points to a valid path
            exists = os.path.exists(versionless_path)
            self.assertEqual(True, exists)





    def _test_strict_checkin(self):
        """
        Tests functionality of checkin/snapshot with different subcontexts and with the strict checkin type.
        """

        return

        server = Config.get_value("install", "server")
        #process = "process"
        person_code = self.person.get_code()

        filename = "filename.jpg"

        process = "strict"

        subcontexts = [
            '', '', # do 2 checkins
            'hi', 'hi',
            'medium',
            'low',
        ]

        for i, subcontext in enumerate(subcontexts):

            if subcontext:
                context = "%s/%s" % (process, subcontext)
            else:
                context = process

            # create a new test.txt file
            file_path = "./%s" % filename
            file = open(file_path, 'w')
            file.write("test")
            file.close()


            #import time
            #start = time.time()

            checkin = FileCheckin(self.person, file_path, context=context, checkin_type='strict')
            checkin.execute()
            snapshot = checkin.get_snapshot()
            #print "time: ", time.time() - start
            #print "---"

            # make sure there is no latest versionless except for process/low
            versionless = Snapshot.get_versionless(self.person.get_search_type(), self.person.get_id(), context, mode='latest', create=False)

            versionless_current = Snapshot.get_versionless(self.person.get_search_type(), self.person.get_id(), context, mode='current', create=False)

            if context == 'strict/low':
                self.assertNotEqual(None, versionless)
                file_objects = versionless.get_all_file_objects()
                self.assertEqual(1, len(file_objects))

                file_object = file_objects[0]
                relative_dir = file_object.get_value("relative_dir")
                file_name = file_object.get_value("file_name")
                self.assertEqual(file_name ,'filename_latest.jpg')
            else:
                self.assertEqual(None, versionless)

            # make sure there is no current versionless except for process/hi
            if context == 'strict/hi':
                self.assertNotEqual(None, versionless_current)
                file_objects = versionless_current.get_all_file_objects()
                self.assertEqual(1, len(file_objects))

                file_object = file_objects[0]
                relative_dir = file_object.get_value("relative_dir")
                file_name = file_object.get_value("file_name")
                self.assertEqual(file_name, 'filename_current.jpg')
                
            else:
                self.assertEqual(None, versionless_current)

            
            path = snapshot.get_path_by_type("main")

            asset_dir = Config.get_value("checkin", "asset_base_dir", sub_key="default")

            file_objects = snapshot.get_all_file_objects()
            self.assertEqual(1, len(file_objects))

            file_object = file_objects[0]
            relative_dir = file_object.get_value("relative_dir")
            file_name = file_object.get_value("file_name")

            test_path = "%s/%s/%s" % (asset_dir, relative_dir, file_name)
            self.assertEqual(test_path, path)




    def _test_with_naming(self):

        server = Config.get_value("install", "server")
        process = "process"
        person_code = self.person.get_code()

        filename = "filename.jpg"

        process = "naming"

        subdirs = ['']

        # create a naming
        naming = SearchType.create("config/naming")
        naming.set_value("search_type", "unittest/person")
        naming.set_value("context", "naming/*")
        naming.set_value("file_naming", "TEST{basefile}_v{version}.{ext}")
        naming.commit()

        # create 2nd naming where 
        naming = SearchType.create("config/naming")
        naming.set_value("search_type", "unittest/person")
        naming.set_value("context", "naming/empty_dir_test")
        naming.set_value("file_naming", "TEST{basefile}_v{version}.{ext}")
        naming.set_value("dir_naming", "{@GET(.description)}")
        naming.commit()

        # create 3rd latest_versionless naming where 
        naming = SearchType.create("config/naming")
        naming.set_value("search_type", "unittest/person")
        naming.set_value("context", "strict/low")
        naming.set_value("file_naming", "{basefile}_latest.{ext}")
        naming.set_value("dir_naming", "{@GET(.description)}")
        naming.set_value("latest_versionless", "1")
        naming.commit()

        # create 4th current_versionless naming where 
        naming = SearchType.create("config/naming")
        naming.set_value("search_type", "unittest/person")
        naming.set_value("context", "strict/hi")
        naming.set_value("file_naming", "{basefile}_current.{ext}")
        naming.set_value("dir_naming", "{@GET(.description)}")
        naming.set_value("current_versionless", "1")
        naming.commit()

        self.clear_naming()


        for i, subdir in enumerate(subdirs):

            if subdir:
                context = "%s/%s/%s" % (process, subdir, filename)
            else:
                context = "%s/%s" % (process, filename)

            # create a new test.txt file
            file_path = "./%s" % filename
            file = open(file_path, 'w')
            file.write("test")
            file.close()

           
 


            #checkin = FileCheckin(self.person, file_path, context=context, checkin_type='auto')
            #checkin = FileCheckin(self.person, file_path, context=context, checkin_type='strict')
            checkin = FileCheckin(self.person, file_path, context=context)
            checkin.execute()

            # ensure that the check-in type is strict
            checkin_type = checkin.get_checkin_type()
            self.assertEqual("strict", checkin_type)

            snapshot = checkin.get_snapshot()

            checked_context = snapshot.get_value("context")


            path = snapshot.get_path_by_type("main")
            basename = os.path.basename(path)
            expected = "TESTfilename_v001.jpg"
            self.assertEqual(expected, basename)


        # create a new test.txt file
        file_path = "./%s" % filename
        file = open(file_path, 'w')
        file.write("test2")
        file.close()
        checkin = FileCheckin(self.person, file_path, context='naming/empty_dir_test')
        checkin.execute()



    def _test_base_dir_alias(self):

        Config.set_value("checkin", "asset_base_dir", {
            'default': '/tmp/tactic/default',
            'alias': '/tmp/tactic/alias',
            'alias2': '/tmp/tactic/alias2',
        });
        asset_dict = Environment.get_asset_dirs()
        default_dir = asset_dict.get("default")
        self.assertEqual( "/tmp/tactic/default", default_dir)

        aliases = asset_dict.keys()
        # "plugins" is assumed in some branch 
        if 'plugins' in aliases:
            self.assertEqual( 4, len(aliases))
        else:
            self.assertEqual( 3, len(aliases))
        self.assertNotEqual( None, "alias" in aliases )

        # create a naming
        naming = SearchType.create("config/naming")
        naming.set_value("search_type", "unittest/person")
        naming.set_value("context", "alias")
        naming.set_value("dir_naming", "alias")
        naming.set_value("file_naming", "text.txt")
        naming.set_value("base_dir_alias", "alias")
        naming.commit()

        # create 2nd naming where 
        naming = SearchType.create("config/naming")
        naming.set_value("search_type", "unittest/person")
        naming.set_value("context", "alias2")
        naming.set_value("dir_naming", "alias2")
        naming.set_value("base_dir_alias", "alias2")
        naming.set_value("file_naming", "text.txt")
        naming.set_value("checkin_type", "auto")
        naming.commit()

        self.clear_naming()

        # create a new test.txt file
        for context in ['alias', 'alias2']:
            file_path = "./test.txt"
            file = open(file_path, 'w')
            file.write("whatever")
            file.close()

            checkin = FileCheckin(self.person, file_path, context=context)
            checkin.execute()
            snapshot = checkin.get_snapshot()

            lib_dir = snapshot.get_lib_dir()
            expected = "/tmp/tactic/%s/%s" % (context, context)
            self.assertEqual(expected, lib_dir)

            path = "%s/text.txt" % (lib_dir)
            exists = os.path.exists(path)
            self.assertEqual(True, exists)

        # manually remove this from this pseudo asset_base_dir as we
        # clean up using the default asset_base_dir at the end
        os.unlink('/tmp/tactic/alias/alias/text.txt')
        os.unlink('/tmp/tactic/alias2/alias2/text.txt')





def profile():
    import profile, pstats
    path = "/tmp/profile"
    profile.run( "profile_execute()", path)
    p = pstats.Stats(path)
    p.sort_stats('cumulative').print_stats(30)
    print("*"*30)
    p.sort_stats('time').print_stats(30)


def profile_execute():
    unittest.main()

            

if __name__ == '__main__':
    unittest.main()
    #profile()





