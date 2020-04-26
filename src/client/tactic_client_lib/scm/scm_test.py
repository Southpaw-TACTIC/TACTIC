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

    def test_all(self):

        user = 'remko'
        password = getpass.getpass("Password: ")

        self.scm = Subversion(user=user, password=password)
        self.scm.set_root("file:///home/apache/test_svn_repo")


        self._test_empty_checkout()
        self._test_checkout_single_file()
        self._test_delivery()




    def _test_empty_checkout(self):
        #repo_path = "sound/sound.wav"
        repo_path = "sound.wav"
        sync_dir = "test_empty"

        branch = "1.1"
        self.scm.set_branch(branch)
        self.scm.set_sync_dir(sync_dir)

        repo_dir = os.path.dirname(repo_path)
        self.scm.checkout(repo_dir, sync_dir, depth="empty")

        self.assertEquals( False, os.path.exists(repo_path) )
        shutil.rmtree(sync_dir)



    def _test_checkout_single_file(self):

        # set the sync dir
        sync_dir = "test_checkout_single"
        self.scm.set_sync_dir(sync_dir)
        self.scm.set_branch("1.1")

        #repo_path = "sound/sound.wav"
        repo_path = "sound.wav"
        sync_path = "%s/%s" % (sync_dir, os.path.basename(repo_path))
        repo_dir = os.path.dirname(repo_path)

        # test checkout of a single file (trick)
        self.scm.checkout_file(repo_path)

        self.assertEquals( True, os.path.exists(sync_path) )
        shutil.rmtree(sync_dir)





    def _test_checkout(self):

        # set the sync dir
        sync_dir = "test_checkout"
        self.scm.set_sync_dir(sync_dir)
        self.scm.set_branch("1.1")

        #repo_path = "sound/sound.wav"
        repo_path = "sound.wav"
        sync_path = "%s/%s" % (sync_dir, os.path.basename(repo_path))
        repo_dir = os.path.dirname(repo_path)

        # test checkout of a single file (trick)
        self.scm.checkout(repo_dir, sync_dir, depth="empty")
        self.scm.export(repo_path, sync_path)

        self.assertEquals( True, os.path.exists(sync_path) )

        shutil.rmtree(sync_dir)






    def _test_delivery(self):
        '''deliver a file to the repository'''
        branch = "1.1"
        #repo_path = "docs/documents2.txt"
        repo_path = "documents2.txt"
        sync_dir = "test_delivery"


        src_path = "./document2.txt"
        f = open(src_path, 'w')
        f.write("This is a document")
        f.close()



        self.scm.set_branch(branch)

        self.scm.set_sync_dir(sync_dir)
        self.scm.deliver_file(src_path, repo_path)


        shutil.rmtree(sync_dir)




if __name__ == '__main__':
    unittest.main()
