############################################################
#
#    Copyright (c) 2012, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

import unittest
import getpass
import os
import shutil

from subversion import *


class ScmTest(unittest.TestCase):

    def test_all(my):

        user = 'remko'
        password = getpass.getpass("Password: ")

        my.scm = Subversion(user=user, password=password)
        my.scm.set_root("file:///home/apache/test_svn_repo")


        my._test_empty_checkout()
        my._test_checkout_single_file()
        my._test_delivery()




    def _test_empty_checkout(my):
        #repo_path = "sound/sound.wav"
        repo_path = "sound.wav"
        sync_dir = "test_empty"

        branch = "1.1"
        my.scm.set_branch(branch)
        my.scm.set_sync_dir(sync_dir)

        repo_dir = os.path.dirname(repo_path)
        my.scm.checkout(repo_dir, sync_dir, depth="empty")

        my.assertEquals( False, os.path.exists(repo_path) )
        shutil.rmtree(sync_dir)



    def _test_checkout_single_file(my):

        # set the sync dir
        sync_dir = "test_checkout_single"
        my.scm.set_sync_dir(sync_dir)
        my.scm.set_branch("1.1")

        #repo_path = "sound/sound.wav"
        repo_path = "sound.wav"
        sync_path = "%s/%s" % (sync_dir, os.path.basename(repo_path))
        repo_dir = os.path.dirname(repo_path)

        # test checkout of a single file (trick)
        my.scm.checkout_file(repo_path)

        my.assertEquals( True, os.path.exists(sync_path) )
        shutil.rmtree(sync_dir)





    def _test_checkout(my):

        # set the sync dir
        sync_dir = "test_checkout"
        my.scm.set_sync_dir(sync_dir)
        my.scm.set_branch("1.1")

        #repo_path = "sound/sound.wav"
        repo_path = "sound.wav"
        sync_path = "%s/%s" % (sync_dir, os.path.basename(repo_path))
        repo_dir = os.path.dirname(repo_path)

        # test checkout of a single file (trick)
        my.scm.checkout(repo_dir, sync_dir, depth="empty")
        my.scm.export(repo_path, sync_path)

        my.assertEquals( True, os.path.exists(sync_path) )

        shutil.rmtree(sync_dir)






    def _test_delivery(my):
        '''deliver a file to the repository'''
        branch = "1.1"
        #repo_path = "docs/documents2.txt"
        repo_path = "documents2.txt"
        sync_dir = "test_delivery"


        src_path = "./document2.txt"
        f = open(src_path, 'w')
        f.write("This is a document")
        f.close()



        my.scm.set_branch(branch)

        my.scm.set_sync_dir(sync_dir)
        my.scm.deliver_file(src_path, repo_path)


        shutil.rmtree(sync_dir)




if __name__ == '__main__':
    unittest.main()
