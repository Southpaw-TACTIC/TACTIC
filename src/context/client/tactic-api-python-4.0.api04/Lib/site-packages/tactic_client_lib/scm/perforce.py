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

__all__ = ['PerforceImpl']

import os

from scm_impl import ScmImpl, ScmException

try:
    from P4 import P4, P4Exception
    HAS_PERFORCE = True
except Exception, e:
    HAS_PERFORCE = False
    P4 = None


class PerforceImpl(ScmImpl):

    def __init__(self, **kwargs):
        super(PerforceImpl, self).__init__(**kwargs)

        port = self.kwargs.get("port")
        self.user = self.kwargs.get("user")
        self.depot = self.kwargs.get("depot")
        password = self.kwargs.get("password")
        client = self.kwargs.get("client")

        self.sync_dir = self.kwargs.get("sync_dir")


        if not self.depot:
            self.depot = "depot"


        use_env = False
        if use_env:
            pass
        else:
            # clear the environment to be sure nothing external gets picked up
            if os.environ.has_key("P4USER"):
                del(os.environ['P4USER'])

            if os.environ.has_key("P4PASSWD"):
                del(os.environ['P4PASSWD'])

            if os.environ.has_key("P4PORT"):
                del(os.environ['P4PORT'])

            if os.environ.has_key("P4CLIENT"):
                del(os.environ['P4CLIENT'])


        self.p4 = P4()

        self.p4.user = str(self.user)
        self.p4.port = str(port)
        self.p4.password = str(password)

        if client:
            self.p4.client = str(client)

        self.p4.connect()
        #self.log.append(str(self.p4.run("info")))

        if self.sync_dir:
            self.set_sync_dir(self.sync_dir)

    def ping(self):
        self.log.append("ping")
        return "OK"


    #
    # user specific functions
    #
    def is_logged_in(self):
        self.log.append("p4 login -s")
        try:
            msg = self.p4.run("login", "-s")
        except Exception, e:
            # for some reason, the "p4 login -s" command gives an exception
            # if you are not logged in
            msg = str(e)


        # if a list is returned, then the user is logged in
        if isinstance(msg,list):
            msg = msg[0]
            if isinstance(msg,dict):
                return True


        if msg.find("Your session has expired") != -1:
            return False
        elif msg.find("Perforce password (P4PASSWD) invalid or unset") != -1:
            return False
        elif msg.find("not connected") != -1:
            return False
        else:
            return True





    #
    # depot functions
    #
    def add_depot(self, depot):
        depot = self.p4.fetch_depot(depot)
        self.p4.save_depot(depot)
        return depot

    def get_depots(self):
        depots = self.p4.run("depots")
        return depots


    #
    # branch functions
    #
    def get_branches(self):
        return self.p4.run("branches")



    #
    # workspace functions
    #
    def get_workspaces(self, user=None):
        if not user:
            user = self.user
        if user:
            return self.p4.run("workspaces", "-u", user)
        else:
            return self.p4.run("workspaces")

    def get_workspace_info(self, workspace):
        if not workspace:
            workspace = self.client_name
        return self.p4.run("workspace", "-o", workspace)


    def check_workspace(self):

        workspaces = self.get_workspaces()
        workspaces = [x.get("client") for x in workspaces]

        clientspec = self.p4.fetch_client()
        client_name = clientspec.get("Client")

        self.log.append(workspaces)

        if client_name not in workspaces:
            return False
        else:
            return True



    def set_sync_dir(self, sync_dir):
        '''This function sets the user's workspace.  It allows for dynamic
        setting of user's workspace depending on which directory the user
        is getting the files from.  However, most will have this location
        specifically mapped through //<depot>'''

        ###### DISABLED
        return


        if not sync_dir:
            raise Exception("Sync dir is None")

        self.sync_dir = sync_dir

        # get the client
        clientspec = self.p4.fetch_client()
        clientspec["Client"] = self.client_name
        clientspec["Root"] = self.sync_dir
        clientspec["Owner"] = self.user

        view = []
        view.append("//%s/... //%s/..." % (self.depot, self.client_name) )

        clientspec["View"] = view
        self.p4.save_client(clientspec)


    def add(self, path, changelist="default"):

        if not changelist:
            changelist = "default"


        self.log.append("p4 add -c %s %s" % (changelist, path))
        self.p4.run("add", "-c", changelist, path)


    def checkout(self, repo_dir, recurse=None, depth=None):

        if not repo_dir.startswith("//"):
            repo_dir = "//%s/%s" % (self.depot, repo_dir)
        if not repo_dir.endswith("/..."):
            repo_dir = "%s/..." % repo_dir

        self.log.append("sync -f %s" % repo_dir)
        try:
            #print "sync", "-f", repo_dir
            sync_data = self.p4.run("sync", "-f", repo_dir)
        except Exception, e:
            if str(e).find("up-to-date") == -1:
                raise
            else:
                sync_data = []


        #print "sync: ", sync_data

        data = {}
        error = []
        for entry in sync_data:
            if isinstance(entry, basestring):
                # if the entry is a string, then it is likely an error
                error.append(entry)
            else:
                data[entry.get("clientFile")] = entry.get("action")

        return {
            "value": data,
            "error": error
        }

    def checkout_file(self, repo_path):
        # ????
        self.p4.run("sync", "-f", repo_path)


    def revert(self, sync_path):
        self.log.append("p4 revert %s" % sync_path)
        return self.p4.run("revert", "-a", sync_path)



    def restore(self, sync_path):
        self.log.append("p4 revert %s" % sync_path)
        return self.p4.run("revert", sync_path)


    def edit(self, repo_path, changelist="default"):
        if not changelist:
            changelist = 'default'
        self.log.append("p4 edit -c %s %s" % (changelist, repo_path))
        return self.p4.run("edit", "-c", changelist, repo_path )



    def update(self, repo_path, recurse=None, depth=None):
        pass


    def export(self, repo_path, dst, recurse=None, depth=None):
        pass



    def file_log(self, repo_path):
        self.log.append("p4 filelog %s" % repo_path)
        return self.p4.run("filelog", repo_path )



    def commit_file(self, path, description, keep_editable=False):
        '''Commit a bunch of files'''


        if not path.startswith(self.sync_dir):
            path = "%s/%s" % (self.sync_dir, path)

        status = self.status(path).get(path)

        if status == 'unversioned':
            self.add(path)
        elif status == 'missing':
            self.checkout_file(path)

        elif status == 'modified':
            # not really sure how it can be "modified" without having
            # edited it.
            self.edit(path)
        elif status == 'same':
            self.edit(path)
        elif status == None:
            # if this file is unknown, then add it.
            self.add(path)

        # first create a new changelist
        #changelist = self.add_changelist(description)

        # NOTE: you can only submit individual file to check-in
        # from the default changelist
        self.log.append("p4 submit -r -d \"%s\" \"%s\"" % (description, path))
        if keep_editable:
            ret_val = self.p4.run("submit", "-r", "-d", description, path)
        else:
            ret_val = self.p4.run("submit", "-d", description, path)
        return ret_val


    def commit_changelist(self, changelist="default", description=""):
        keep_open = False       # -r option
        if changelist in [None, 'default']:
            self.log.append("p4 submit -d \"%s\"" % description)
            ret_val = self.p4.run("submit", "-d", description)
        else:
            self.log.append("p4 submit -r -c %s" % changelist)
            ret_val = self.p4.run("submit", "-r", "-c", changelist)
        return ret_val




    def status(self, sync_dir=None):

        if not sync_dir:
            sync_dir = self.sync_dir


        sync_expr = sync_dir
        if sync_expr:
            if os.path.isdir(sync_expr) and not sync_expr.endswith("/..."):
                sync_expr = "%s/..." % sync_expr

        # FIXME: this might be slow on huge repositories

        try:
            if sync_expr:
                self.log.append("p4 diff -sl -f %s"  % sync_expr)
                diff = self.p4.run("diff", "-sl", "-f", sync_expr)
            else:
                self.log.append("p4 diff -sl -f")
                diff = self.p4.run("diff", "-sl", "-f")

        except Exception, e:
            # if there is an exception, likely this is because there are 
            # no files on the client and Perforce does not like this
            print "WARNING: ", e
            print self.p4.run("info")
            diff = []


        info = {}
        for entry in diff:
            client_file = entry.get("clientFile")
            client_file = client_file.replace("\\", "/")
            if not client_file.startswith(sync_dir):
                client_file = "%s/%s" % (sync_dir, client_file)
            status = entry.get("status")
            if status == 'diff':
                info[client_file] = 'modified'
            else:
                info[client_file] = status


        # find opened files
        opened_files = self.p4.run("opened")
        new_files = {} 
        for opened_file in opened_files:
            if opened_file['action'] != 'add':
                continue
            path = opened_file['depotFile']
            path = path.replace("//%s" % self.depot, self.sync_dir)
            new_files[path] = 'add'

        for root, dirnames, basenames in os.walk(sync_dir):
            for dirname in dirnames:
                client_path = "%s/%s" % (root, dirname)
                client_path = "%s/%s" % (root, dirname)
                client_path = client_path.replace("\\", "/")

                if client_path.find("/.tactic") != -1:
                    continue

                info[client_path] = 'directory'

            for basename in basenames:
                client_path = "%s/%s" % (root, basename)
                client_path = client_path.replace("\\", "/")

                # ignore .tactic directory
                if client_path.find("/.tactic") != -1:
                    continue

                status = info.get(client_path)

                if new_files.get(client_path):
                    info[client_path] = 'added'
                elif not status:
                    info[client_path] = 'unversioned'
                elif status == 'same' and os.access(client_path, os.W_OK):
                    info[client_path] = 'editable'


        return info




    def add_changelist(self, description, changelist=None):
        changespec = self.p4.fetch_change()
        changespec['Description'] = description
        changespec['User'] = self.user
        info = self.p4.save_change(changespec)
        return info


    def get_changelist_files(self, changelist='default'):
        files = self.p4.run("opened", "-c", changelist)
        return files

    def get_changelist_info(self, changelist='default'):
        info = self.p4.run("describe", changelist)
        return info


    def get_changelists_by_user(self, user=None):
        if not user:
            user = self.user
        changeslists = self.p4.run("changelists", "-u", user, "-s", "pending", "-c", self.client_name)
        return changeslists




    def get_changelists(self, counter='tactic'):
        changeslists = self.p4.run("review", "-t", counter)
        return changeslists


    def set_changelist_counter(self, changelist, counter='tactic'):
        changeslists = self.p4.run("review", "-t", counter, '-c', changelist)
        return changeslists





if __name__ == '__main__':
    scm = PerforceImpl()
    #print "branches: ", svn.get_all_branches()
    #print "tags: ", svn.get_all_tags("3.6")

    repo_dir = "src/main/documents"
    scm.checkout(repo_dir)






