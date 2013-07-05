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

from pyasm.common import Environment, Config, Common
from pyasm.command import Command, UndoCmd
from pyasm.search import Transaction, SearchType, Search
from pyasm.security import Batch
from pyasm.checkin import *
from pyasm.biz import File, FileGroup, Project, FileRange, Snapshot
from pyasm.prod.checkin import TextureCheckin
from pyasm.prod.biz import Asset

#from file_checkin import *


class CheckinTest(unittest.TestCase, Command):

    def __init__(my, *args):
        unittest.TestCase.__init__(my, *args)
        Command.__init__(my)


    def test_all(my):
        '''entry point function'''
        my.description = "Checkin unit test"
        my.errors = []

        Batch()
        Project.set_project("unittest")

        Command.execute_cmd(my)

        # undo the command
        undo = UndoCmd()
        undo.execute()


    def execute(my):
        my.person = Person.create( "Unit", "Test",
                "ComputerWorld", "Fake Unittest Person")

        my._test_checkin()
        my._test_groupcheckin()
        my._test_inplace_checkin()
        my._test_preallocation_checkin()
        my._test_get_children()
        my._test_texture_checkin()
        my._test_file_owner()
        my._test_symlink()


    def _test_checkin(my):

        # create a new test.txt file
        file_path = "./test.txt"
        file = open(file_path, 'w')
        file.write("whatever")
        file.close()

        checkin = FileCheckin(my.person, file_path, "test")
        checkin.execute()

        # check that the file exists
        snapshot = checkin.get_snapshot()
        xml = snapshot.get_xml_value("snapshot")
        file_code = xml.get_value("snapshot/file/@file_code")
        file_name = xml.get_value("snapshot/file/@name")

        my.assertNotEqual(None, file)

        lib_path = "%s/%s" % (snapshot.get_lib_dir(),file_name)
        my.assertEquals(True, os.path.exists(lib_path) )

        #print "relative_dir: ", snapshot.get_relative_dir()



    def _test_groupcheckin(my):
        
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

        checkin = FileGroupCheckin(my.person, file_paths, file_types, range, \
            column="frames")
        checkin.execute()


        # delete the test files
        for expanded_path in expanded_paths:
            os.unlink(expanded_path)



    def _test_inplace_checkin(my):

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
        checkin = FileCheckin(my.person, file_path, context=context, mode=mode)
        checkin.execute()
        snapshot = checkin.get_snapshot()

        file_code = snapshot.get_file_code_by_type("main")
        file_object = File.get_by_code(file_code)

        relative_dir = file_object.get_value("relative_dir")
        # The relative dir is empty if the file is outside the repository
        #my.assertEquals("temp", relative_dir)
        my.assertEquals("", relative_dir)

        lib_dir = snapshot.get_lib_dir(file_type="main")
        file_name = snapshot.get_file_name_by_type("main")
        lib_path = "%s/%s" % (lib_dir, file_name)
        my.assertEquals( True, os.path.exists(lib_path) )
        my.assertEquals( file_path, lib_path)


        # now checkin a new version of this file (through some other means)
        checkin = FileCheckin(my.person, file_path, context=context)
        checkin.execute()
        snapshot = checkin.get_snapshot()
        #print "lib_dir: ", snapshot.get_lib_dir(), snapshot.get_file_name_by_type("main")


        if os.path.exists(file_path):
            os.unlink(file_path)





    def _test_preallocation_checkin(my):

        snapshot_type="file"
        context="preallocation"
        file_name = 'whatever.jpg'
        file_type = 'jpg'


        # create an empty snapshot
        snapshot = Snapshot.create(my.person, snapshot_type=snapshot_type, context=context)

        # preallocate with no name or type
        path = snapshot.get_preallocated_path()
        my.assertEquals(True, path.endswith('%s_preallocation_v001'%my.person.get_code()) )

        # preallocate with a file name and file type
        path = snapshot.get_preallocated_path(file_type, file_name)
        
        my.assertEquals(True, None != re.search('unittest/person/\w+/preallocation/whatever_preallocation_v001.jpg$', path) )

        # create a file directly in the path location and register in
        # transaction
        f = open(path, 'wb')
        f.write("wowow")
        f.close()

        # add this file to the snapshot and force the name
        snapshot_code = snapshot.get_code()
        checkin = FileAppendCheckin(snapshot_code, [path], [file_type], keep_file_name=True, mode='preallocate')
        checkin.execute()

        # check that it worked
        snapshot = checkin.get_snapshot()
        lib_dir = snapshot.get_lib_dir()
        file_name = snapshot.get_file_name_by_type(file_type)
        my.assertEquals(True, os.path.exists("%s/%s" % (lib_dir, file_name) ) )


        # test preallocation on a sequence
        file_name = "images_%0.4d.png"
        file_type = 'sequence'
        file_range = FileRange(1, 5)

        path = snapshot.get_preallocated_path(file_type=file_type, file_name=file_name)
        # imitate a render by building files directly to the path
        for i in range(1,6):
            cur_path = path % i
            f = open(cur_path, 'wb')
            f.write("wowow")
            f.close()

        # register these files
        snapshot_code = snapshot.get_code()
        checkin = FileGroupAppendCheckin(snapshot_code, [path], [file_type], file_range, \
                keep_file_name=True, mode='preallocate')
        checkin.execute()

        snapshot = checkin.get_snapshot()

        # get the file paths
        file_names = snapshot.get_expanded_file_names(file_type)
        lib_dir = snapshot.get_lib_dir()
        for file_name in file_names:
            path = "%s/%s" % (lib_dir, file_name)
            my.assertEquals(True, os.path.exists(path)) 
        


    def _test_get_children(my):
        # test to make sure get_all_children is able to snapshots
        snapshots = my.person.get_all_children("sthpw/snapshot")
        my.assertEquals(4, len(snapshots))


    def _test_texture_checkin(my):
        #import time
        #st = time.time()
        dir = Environment.get_install_dir()
        path = '%s/src/client/test/images/miso_ramen.0002.jpg'%(dir) 
        basename = os.path.basename(path)

        #copy the file
        server_dir = FileCheckin.get_upload_dir()
        try:
            if os.path.exists(server_dir):
                shutil.rmtree(server_dir)
            os.makedirs(server_dir)
            
        except OSError, e:
            sys.stderr.write("WARNING: could not cleanup server directory [%s]: %s" % (server_dir, e.__str__()))
        
        """
        shutil.copy(path, "%s/%s" % (server_dir, basename))
        Project.set_project("racoon")
        parent = Asset.get_by_code('prp009')
        context = 'publish'
        paths = [path]
        file_ranges = [None]
        node_names = ['Clips.prp011_prp010_umbrella_jpg']
        attrs = ["SourceFileName"]
        use_handoff_dir = False
        checkin = TextureCheckin(parent, context, paths, file_ranges, node_names, attrs, use_handoff_dir=use_handoff_dir)
        Command.execute_cmd(checkin)
        texture_file_codes = checkin.get_file_codes() 
        texture_file_paths = checkin.get_texture_paths()
        
        # remapping for duplicated file
        #my.assertEquals(texture_file_codes[0], texture_file_codes[1])
        
        texture_snapshots = checkin.texture_snapshots
        """
        #for snapshot in texture_snapshots:
        #    print "xml" , snapshot.get_snapshot_xml().to_string()
        #print "checkin time: ", time.time() -st

    def _test_file_owner(my):
        if os.name == 'nt':
            return
        # create a new test.txt file
        file_path = "./test2.txt"
        file = open(file_path, 'w')
        file.write("whatever")
        file.close()
        # owned by root
        os.system('sudo chown root.root \"%s\"'%file_path)

        stat = os.stat(file_path)
        my.assertEquals(stat.st_uid, 0)

        checkin = FileCheckin(my.person, file_path, "test")
        checkin.execute()

        # check that the file exists
        snapshot = checkin.get_snapshot()
        xml = snapshot.get_xml_value("snapshot")
        file_code = xml.get_value("snapshot/file/@file_code")
        file_name = xml.get_value("snapshot/file/@name")

        my.assertNotEqual(None, file)

        lib_path = "%s/%s" % (snapshot.get_lib_dir(),file_name)
        my.assertEquals(True, os.path.exists(lib_path) )
        stat = os.stat(lib_path)
        if Config.get_value("checkin", "sudo_no_password") == 'true': 
            my.assertEquals(stat.st_uid, 48)
        else:
            # if not set, it will remain owned by root
            my.assertEquals(stat.st_uid, 0)

    def _test_symlink(my):
        if os.name == 'nt':
            return

        # create a new test.txt file
        file_path = "./symlink.txt"
        file = open(file_path, 'w')
        file.write("symlink test")
        file.close()

        checkin = FileCheckin(my.person, file_path, context="sym_test", checkin_type='auto')
        checkin.execute()

        snap = Snapshot.get_versionless(my.person.get_search_type(), my.person.get_id(), "sym_test", mode='latest', create=False)
        my.assertEquals(True, isinstance(snap, Snapshot))
        if snap:
            lib_path =snap.get_lib_path_by_type('main')
            my.assertEquals(True, os.path.exists(lib_path)) 
            rel_path = os.readlink(lib_path)
            lib_dir = os.path.dirname(lib_path)

            # this is essentially handle_link() in FileUndo class
            wd = os.getcwd()
            os.chdir(lib_dir)
            real_path = os.path.join(lib_dir, os.path.abspath(rel_path))
            # lib_path points to real_path

            expected_rel_path  = Common.relative_path(lib_path, real_path)
            my.assertEquals(True, os.path.exists(real_path))
            my.assertEquals(expected_rel_path, rel_path)
            os.chdir(wd)

       
            

if __name__ == '__main__':
    unittest.main()





