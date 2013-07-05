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

__all__ = ['RepoImpl', 'PerforceRepoImpl', 'TacticRepoImpl']

import os

from pyasm.common import Environment
from pyasm.biz import Snapshot
from pyasm.web import WebContainer


from perforce_data import PerforceData
from pyasm.search import Search

class RepoImpl(object):
    '''contains the functions needed to implement interactions with a repo'''

    def __init__(my, sobject):
        my.sobject = sobject

        # all of the local data is retrieved a separate structure
        # What separate structure? it's the same like others 
        web = WebContainer.get_web()
        name = my.sobject.get_name()
        # NOTE: name cannot be empty
        my.local_paths = web.get_form_value("local_%s" % name)
        #for key in web.get_form_keys():
            #print key, " = ", web.get_form_values(key)


    def get_root_path(my):
        '''gets the root path of the local repository'''
        pass


   
    def get_repo_paths(my):
        '''returns all of the files in the repo under a given directory'''
        pass

    
    def get_checkout_paths(my):
        '''returns all of the files in the repo under a given directory'''
        pass

    def get_local_paths(my):
        '''gets the root path of the local repository'''
        my.local_paths = my.local_paths.split("|")
        return my.local_paths

    def get_sync_paths(my):
        pass
        
    def get_sync_dict(my):
        pass
       
    def get_allowed_types(my):
        pass

    # actions

    def checkout(my, paths):
        pass

    def revert(my, paths):
        pass

    def sync(my, paths):
        pass

    
    def publish(my, paths, description):
        pass






class PerforceRepoImpl(RepoImpl):

    def __init__(my, sobject):
        super(PerforceRepoImpl, my).__init__(sobject)

        # get all of the perforce data through perforce data structures
        my.perforce_data = PerforceData(my.sobject)
        my.perforce_data.process_all_data()


    def get_root_path(my):
        '''gets the root path of the local repository'''
        root = my.perforce_data.get_value('workspaces', 'Root')
        return root.replace("\\", "/")



    def get_opened_paths(my):
        data = my.perforce_data.get_data('have', 0)
        return data


    def get_repo_paths(my):
        web = WebContainer.get_web()
        name = my.sobject.get_name()

        repo = web.get_form_value("repo_%s" % name)
        repo_files = repo.split("|")

        # the file that is returned 
        files = []
        for x in repo_files:
            # TODO: repo should not be empty
            if not x:
                continue
            val = x.split(' - ')[0].strip()
            if val:
                files.append(val)


        return files

        #data = my.perforce_data.get_data('repo', 0)


    def get_sync_paths(my):
        web = WebContainer.get_web()
        name = my.sobject.get_name()

        sync = web.get_form_value("sync_%s" % name)
        sync_files = sync.split("|")
        return sync_files


    def get_sync_dict(my):
        '''a dict of sync files with respect to the expected checked 
        out file name'''
        sync_dict = {}
        sync_files = my.get_sync_paths()
        for sync in sync_files:
            # TODO: sync should not be empty
            if not sync:
                continue

            sync_file, checkout_file = sync.split(' - ')
            sync_dict[sync_file.strip()] = checkout_file.strip()
        return sync_dict
            
    def get_checkout_paths(my):
        web = WebContainer.get_web()
        name = my.sobject.get_name()

        checkout = web.get_form_value("checkout_%s" % name)
        checkout_files = checkout.split("|")

        # the file that is returned 
        files = []
        for x in checkout_files:
            if not x:
                continue
            val = x.split(' - ')[0].strip()
            if val:
                files.append(val)

        return files






class TacticRepoImpl(RepoImpl):

    def get_root_path(my):
        '''gets the root path of the local repository'''
        return my.sobject.get_lib_dir()


    def get_sync_paths(my):
        snapshot = Snapshot.get_latest_by_sobject(my.sobject, "icon")
        local_repo_dir = my.sobject.get_local_repo_dir(snapshot)

        if not os.path.exists(local_repo_dir):
            return []

        paths = os.listdir(local_repo_dir)
        paths = ["%s/%s" % (local_repo_dir, x) for x in paths]

        return paths

    def get_sync_dict(my):
        ''' for tactic repo, it is not needed'''
        return {}

    def get_repo_paths(my):
        '''get all of the files in the repo'''
        # TODO: this makes no sense at all!!!!
        """
        snapshot = Snapshot.get_latest_by_sobject(my.sobject, "icon")
        lib_dir = my.sobject.get_lib_dir(snapshot)

        if not os.path.exists(lib_dir):
            return []

        # add the lib_dir back
        paths = os.listdir(lib_dir)
        paths = ["%s/%s" % (lib_dir, x) for x in paths]
        return paths
        """
        return []


    def get_allowed_types(my):
        ''' types of file that can be checked out '''
        # FIXME: added texture and source temporarily for Spin
        return ['file', 'main', 'psd', 'texture', 'source', 'max', 'maya', 'None']

    def get_checkout_paths(my):
        snapshots = TacticRepoImpl.get_repo_snapshots(my.sobject)
        if not snapshots:
            return []
        """
        #sandbox_dir = my.sobject.get_sandbox_dir(snapshots[0])
        
        lib_dir = my.sobject.get_lib_dir(snapshots[0])
        if not os.path.exists(lib_dir):
            return []
        """
        paths = []
        for snapshot in snapshots:
            for type in my.get_allowed_types():
                file_name =  snapshot.get_file_name_by_type(type)
                if not file_name:
                    continue
                sandbox_dir = snapshot.get_sandbox_dir()
                paths.append("%s/%s" % (sandbox_dir,file_name))

        return paths


    def get_repo_snapshots(sobject):
        '''we want all snapshots to recognize any checked out files from repo'''
        search = Search("sthpw/snapshot")
        search.add_filter("search_type", sobject.get_search_type() )
        search.add_filter("search_id", sobject.get_id() )
        #search.add_order_by("context")
        #search.add_order_by("version desc")
        search.add_order_by("timestamp desc")
        snapshots = search.get_sobjects()

        return snapshots
    
    get_repo_snapshots = staticmethod(get_repo_snapshots)



class SubversionRepoImpl(RepoImpl):
    pass




