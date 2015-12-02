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

    def __init__(my, **kwargs):
        my.kwargs = kwargs

        my.user = kwargs.get('user')
        my.password = kwargs.get('password')

        my.tag = kwargs.get('tab')
        my.branch = kwargs.get('branch')
        my.trunk = kwargs.get('trunk')

        my.root = kwargs.get('root')
        my.sync_dir = kwargs.get("sync_dir")

        my.log = []


    def set_root(my, root):
        '''set the root of the server depot.  Each scm will specify it's
        own root.  ie: SVN uses URLs'''


    def set_branch(my, branch):
        '''set the current branch that is being worked on'''
        my.branch = branch


    def set_sync_dir(my, sync_dir):
        '''set the absolute base directory of the sync (or workspace or
        sandbox)'''
        my.sync_dir = sync_dir


    def get_log(my):
        return my.log



    def checkout(my, repo_dir, sync_dir, depth=None):
        '''Method to check out some root from the repository to a destination
        directory

        @params
          repo_dir: directory in the repo to checkout relative to the root
          sync_dir: the directory to check these files out to
          depth: ??? (empty)
        '''
        pass



    def commit(my, sync_path):
        '''Method to check-in a list of files

        @params:
        '''
        pass



    #
    # Higher level functions
    #

    def deliver_file(my, src_path, repo_path):

        repo_dir = os.path.dirname(repo_path)

        sync_path = "%s/%s" % (my.sync_dir, repo_path)
        sync_dir = os.path.dirname(sync_path)

        # Trick to checkout a single file.  Not sure if this works
        my.checkout(repo_dir, sync_dir, depth="empty")
        try:
            my.export(repo_path, sync_path)
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
            my.add(sync_path)
        else:
            print "--> update"
            my.update(sync_path)

        my.commit(sync_path, "this is a test")



