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

    def __init__(self, **kwargs):
        super(Subversion, self).__init__(**kwargs)

        self.client = pysvn.Client()


    def get_login( self, realm, username, may_save):
        retcode = True
        print "user: [%s]" % username
        user = self.user
        #password = getpass.getpass("xPassword: ")
        password = self.password
        save = False
        return retcode, user, password, save

    def ssl_server_trust_prompt( self, trust_dict ):
        retcode = True
        save = True
        return retcode, -1, save


    def notify( self, evt ):
        #print "action: ", evt.get("action"), evt.get("path")
        pass


    def add_default_callbacks(self):
        self.client.callback_get_login = self.get_login
        self.client.callback_ssl_server_trust_prompt = self.ssl_server_trust_prompt
        self.client.callback_notify = self.notify


    def get_repo_url(self, repo_path):
        repo_url = '%s/branches/%s/%s' % (self.root, self.branch, repo_path)
        return repo_url




    def add(self, sync_path):
        self.client.add(sync_path)


    def checkout(self, repo_dir, recurse=None, depth='empty'):
        self.add_default_callbacks()

        repo_url = self.get_repo_url(repo_dir)
        if recurse != None:
            self.client.checkout(repo_url, self.sync_dir, recurse=recurse)
        elif depth:
            depth = eval("pysvn.depth.%s" % depth)
            self.client.checkout(repo_url, self.sync_dir, depth=depth)



    def checkout_file(self, repo_path):
        '''Check out a sinlge file'''
        self.add_default_callbacks()

        repo_dir = os.path.dirname(repo_path)
        sync_path = "%s/%s" % (self.sync_dir, os.path.basename(repo_path))

        self.checkout(repo_dir, self.sync_dir, depth='empty')
        self.export(repo_path, sync_path)



    def update(self, repo_path, recurse=None, depth='empty'):
        self.add_default_callbacks()
        repo_url = self.get_repo_url(repo_path)
        if recurse != None:
            self.client.update(repo_url, dst, recurse=recurse)
        elif depth:
            depth = eval("pysvn.depth.%s" % depth)
            self.client.update(repo_url, dst, depth=depth)



    def export(self, repo_path, dst, recurse=None, depth='empty'):
        self.add_default_callbacks()
        repo_url = self.get_repo_url(repo_path)
        if recurse != None:
            self.client.export(repo_url, dst, recurse=recurse)
        elif depth != None:
            depth = eval("pysvn.depth.%s" % depth)
            self.client.export(repo_url, dst, depth=depth)
        else:
            self.client.export(repo_url, dst)




    def commit(self, paths, description):
        self.add_default_callbacks()

        full_paths = []
        for path in paths:
            if not path.startswith(self.sync_dir):
                path = "%s/%s" % (self.sync_dir, path)
            full_paths.append(path)
        self.client.checkin(full_paths, description)


    def status(self, path=None):
        path = "%s/%s" % (self.sync_dir, path)

        changes = self.client.status(path)
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

    def get_all_branches(self):
        repo_url = '%s/branches' % self.root

        self.client.callback_get_login = self.get_login
        self.client.callback_ssl_server_trust_prompt = self.ssl_server_trust_prompt
        self.client.callback_notify = self.notify

        dir_list = self.client.ls(repo_url)

        branches = []
        for dir_entry in dir_list:
            full = dir_entry.name
            branch = os.path.basename(full)
            branches.append(branch)

        return branches


    def get_all_tags(self, branch):
        repo_url = '%s/tags' % self.root

        self.client.callback_get_login = self.get_login
        self.client.callback_ssl_server_trust_prompt = self.ssl_server_trust_prompt
        self.client.callback_notify = self.notify

        dir_list = self.client.ls(repo_url)

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






