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

__all__ = ['ScmImpl', 'ScmException']

import os, shutil


class ScmException(Exception):
    pass

class ScmImpl(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.user = kwargs.get('user')
        self.password = kwargs.get('password')

        self.tag = kwargs.get('tab')
        self.branch = kwargs.get('branch')
        self.trunk = kwargs.get('trunk')

        self.root = kwargs.get('root')
        self.sync_dir = kwargs.get("sync_dir")

        self.log = []


    def set_root(self, root):
        '''set the root of the server depot.  Each scm will specify it's
        own root.  ie: SVN uses URLs'''


    def set_branch(self, branch):
        '''set the current branch that is being worked on'''
        self.branch = branch


    def set_sync_dir(self, sync_dir):
        '''set the absolute base directory of the sync (or workspace or
        sandbox)'''
        self.sync_dir = sync_dir


    def get_log(self):
        return self.log



    def checkout(self, repo_dir, sync_dir, depth=None):
        '''Method to check out some root from the repository to a destination
        directory

        @params
          repo_dir: directory in the repo to checkout relative to the root
          sync_dir: the directory to check these files out to
          depth: ??? (empty)
        '''
        pass



    def commit(self, sync_path):
        '''Method to check-in a list of files

        @params:
        '''
        pass



    #
    # Higher level functions
    #

    def deliver_file(self, src_path, repo_path):

        repo_dir = os.path.dirname(repo_path)

        sync_path = "%s/%s" % (self.sync_dir, repo_path)
        sync_dir = os.path.dirname(sync_path)

        # Trick to checkout a single file.  Not sure if this works
        self.checkout(repo_dir, sync_dir, depth="empty")
        try:
            self.export(repo_path, sync_path)
        except Exception, e:
            print "WARNING: ", e
            exists = False
        else:            
            exists = os.path.exists( sync_path )
            if exists:
                return


        # create a dummy file
        shutil.copy(src_path, sync_path)

        # if it doesn't exist, add it
        if not exists:
            print "--> add"
            self.add(sync_path)
        else:
            print "--> update"
            self.update(sync_path)

        self.commit(sync_path, "this is a test")



