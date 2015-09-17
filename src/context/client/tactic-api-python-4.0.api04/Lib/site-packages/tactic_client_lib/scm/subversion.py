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

__all__ = ['Subversion']


try:
    import pysvn
    HAS_SVN = True
except Exception, e:
    HAS_SVN = False

import getpass, os

from scm_impl import ScmImpl


class Subversion(ScmImpl):

    def __init__(my, **kwargs):
        super(Subversion, my).__init__(**kwargs)

        my.client = pysvn.Client()


    def get_login( my, realm, username, may_save):
        retcode = True
        print "user: [%s]" % username
        user = my.user
        #password = getpass.getpass("xPassword: ")
        password = my.password
        save = False
        return retcode, user, password, save

    def ssl_server_trust_prompt( my, trust_dict ):
        retcode = True
        save = True
        return retcode, -1, save


    def notify( my, evt ):
        #print "action: ", evt.get("action"), evt.get("path")
        pass


    def add_default_callbacks(my):
        my.client.callback_get_login = my.get_login
        my.client.callback_ssl_server_trust_prompt = my.ssl_server_trust_prompt
        my.client.callback_notify = my.notify


    def get_repo_url(my, repo_path):
        repo_url = '%s/branches/%s/%s' % (my.root, my.branch, repo_path)
        return repo_url




    def add(my, sync_path):
        my.client.add(sync_path)


    def checkout(my, repo_dir, recurse=None, depth='empty'):
        my.add_default_callbacks()

        repo_url = my.get_repo_url(repo_dir)
        if recurse != None:
            my.client.checkout(repo_url, my.sync_dir, recurse=recurse)
        elif depth:
            depth = eval("pysvn.depth.%s" % depth)
            my.client.checkout(repo_url, my.sync_dir, depth=depth)



    def checkout_file(my, repo_path):
        '''Check out a sinlge file'''
        my.add_default_callbacks()

        repo_dir = os.path.dirname(repo_path)
        sync_path = "%s/%s" % (my.sync_dir, os.path.basename(repo_path))

        my.checkout(repo_dir, my.sync_dir, depth='empty')
        my.export(repo_path, sync_path)



    def update(my, repo_path, recurse=None, depth='empty'):
        my.add_default_callbacks()
        repo_url = my.get_repo_url(repo_path)
        if recurse != None:
            my.client.update(repo_url, dst, recurse=recurse)
        elif depth:
            depth = eval("pysvn.depth.%s" % depth)
            my.client.update(repo_url, dst, depth=depth)



    def export(my, repo_path, dst, recurse=None, depth='empty'):
        my.add_default_callbacks()
        repo_url = my.get_repo_url(repo_path)
        if recurse != None:
            my.client.export(repo_url, dst, recurse=recurse)
        elif depth != None:
            depth = eval("pysvn.depth.%s" % depth)
            my.client.export(repo_url, dst, depth=depth)
        else:
            my.client.export(repo_url, dst)




    def commit(my, paths, description):
        my.add_default_callbacks()

        full_paths = []
        for path in paths:
            if not path.startswith(my.sync_dir):
                path = "%s/%s" % (my.sync_dir, path)
            full_paths.append(path)
        my.client.checkin(full_paths, description)


    def status(my, path=None):
        path = "%s/%s" % (my.sync_dir, path)

        changes = my.client.status(path)
        info = {}
        for f in changes:
            path = f.path.replace("\\", "/")
            if f.text_status == pysvn.wc_status_kind.added:
                info[path] = "added"
            elif f.text_status == pysvn.wc_status_kind.deleted:
                info[path] = "deleted"
            elif f.text_status == pysvn.wc_status_kind.modified:
                info[path] = "modified"
            elif f.text_status == pysvn.wc_status_kind.conflicted:
                info[path] = "conflicted"
            elif f.text_status == pysvn.wc_status_kind.unversioned:
                info[path] = "unversioned"
            else:
                info[path] = "same"

        return info




    #
    # Query methods
    #

    def get_all_branches(my):
        repo_url = '%s/branches' % my.root

        my.client.callback_get_login = my.get_login
        my.client.callback_ssl_server_trust_prompt = my.ssl_server_trust_prompt
        my.client.callback_notify = my.notify

        dir_list = my.client.ls(repo_url)

        branches = []
        for dir_entry in dir_list:
            full = dir_entry.name
            branch = os.path.basename(full)
            branches.append(branch)

        return branches


    def get_all_tags(my, branch):
        repo_url = '%s/tags' % my.root

        my.client.callback_get_login = my.get_login
        my.client.callback_ssl_server_trust_prompt = my.ssl_server_trust_prompt
        my.client.callback_notify = my.notify

        dir_list = my.client.ls(repo_url)

        tags = []
        for dir_entry in dir_list:
            full = dir_entry.name
            tag = os.path.basename(full)
            tags.append(tag)

        return tags



if __name__ == '__main__':
    user = 'remko'
    password = getpass.getpass("Password: ")

    svn = Subversion(user=user, password=password)
    print "branches: ", svn.get_all_branches()
    print "tags: ", svn.get_all_tags("3.6")






