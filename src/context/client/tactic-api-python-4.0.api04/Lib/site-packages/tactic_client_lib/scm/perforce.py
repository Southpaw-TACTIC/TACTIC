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

    def __init__(my, **kwargs):
        super(PerforceImpl, my).__init__(**kwargs)

        port = my.kwargs.get("port")
        my.user = my.kwargs.get("user")
        my.depot = my.kwargs.get("depot")
        password = my.kwargs.get("password")
        client = my.kwargs.get("client")

        my.sync_dir = my.kwargs.get("sync_dir")


        if not my.depot:
            my.depot = "depot"


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


        my.p4 = P4()

        my.p4.user = str(my.user)
        my.p4.port = str(port)
        my.p4.password = str(password)

        if client:
            my.p4.client = str(client)

        my.p4.connect()
        #my.log.append(str(my.p4.run("info")))

        if my.sync_dir:
            my.set_sync_dir(my.sync_dir)

    def ping(my):
        my.log.append("ping")
        return "OK"


    #
    # user specific functions
    #
    def is_logged_in(my):
        my.log.append("p4 login -s")
        try:
            msg = my.p4.run("login", "-s")
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
    def add_depot(my, depot):
        depot = my.p4.fetch_depot(depot)
        my.p4.save_depot(depot)
        return depot

    def get_depots(my):
        depots = my.p4.run("depots")
        return depots


    #
    # branch functions
    #
    def get_branches(my):
        return my.p4.run("branches")



    #
    # workspace functions
    #
    def get_workspaces(my, user=None):
        if not user:
            user = my.user
        if user:
            return my.p4.run("workspaces", "-u", user)
        else:
            return my.p4.run("workspaces")

    def get_workspace_info(my, workspace):
        if not workspace:
            workspace = my.client_name
        return my.p4.run("workspace", "-o", workspace)


    def check_workspace(my):

        workspaces = my.get_workspaces()
        workspaces = [x.get("client") for x in workspaces]

        clientspec = my.p4.fetch_client()
        client_name = clientspec.get("Client")

        my.log.append(workspaces)

        if client_name not in workspaces:
            return False
        else:
            return True



    def set_sync_dir(my, sync_dir):
        '''This function sets the user's workspace.  It allows for dynamic
        setting of user's workspace depending on which directory the user
        is getting the files from.  However, most will have this location
        specifically mapped through //<depot>'''

        ###### DISABLED
        return


        if not sync_dir:
            raise Exception("Sync dir is None")

        my.sync_dir = sync_dir

        # get the client
        clientspec = my.p4.fetch_client()
        clientspec["Client"] = my.client_name
        clientspec["Root"] = my.sync_dir
        clientspec["Owner"] = my.user

        view = []
        view.append("//%s/... //%s/..." % (my.depot, my.client_name) )

        clientspec["View"] = view
        my.p4.save_client(clientspec)


    def add(my, path, changelist="default"):

        if not changelist:
            changelist = "default"


        my.log.append("p4 add -c %s %s" % (changelist, path))
        my.p4.run("add", "-c", changelist, path)


    def checkout(my, repo_dir, recurse=None, depth=None):

        if not repo_dir.startswith("//"):
            repo_dir = "//%s/%s" % (my.depot, repo_dir)
        if not repo_dir.endswith("/..."):
            repo_dir = "%s/..." % repo_dir

        my.log.append("sync -f %s" % repo_dir)
        try:
            #print "sync", "-f", repo_dir
            sync_data = my.p4.run("sync", "-f", repo_dir)
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

    def checkout_file(my, repo_path):
        # ????
        my.p4.run("sync", "-f", repo_path)


    def revert(my, sync_path):
        my.log.append("p4 revert %s" % sync_path)
        return my.p4.run("revert", "-a", sync_path)



    def restore(my, sync_path):
        my.log.append("p4 revert %s" % sync_path)
        return my.p4.run("revert", sync_path)


    def edit(my, repo_path, changelist="default"):
        if not changelist:
            changelist = 'default'
        my.log.append("p4 edit -c %s %s" % (changelist, repo_path))
        return my.p4.run("edit", "-c", changelist, repo_path )



    def update(my, repo_path, recurse=None, depth=None):
        pass


    def export(my, repo_path, dst, recurse=None, depth=None):
        pass



    def file_log(my, repo_path):
        my.log.append("p4 filelog %s" % repo_path)
        return my.p4.run("filelog", repo_path )



    def commit_file(my, path, description, keep_editable=False):
        '''Commit a bunch of files'''


        if not path.startswith(my.sync_dir):
            path = "%s/%s" % (my.sync_dir, path)

        status = my.status(path).get(path)

        if status == 'unversioned':
            my.add(path)
        elif status == 'missing':
            my.checkout_file(path)

        elif status == 'modified':
            # not really sure how it can be "modified" without having
            # edited it.
            my.edit(path)
        elif status == 'same':
            my.edit(path)
        elif status == None:
            # if this file is unknown, then add it.
            my.add(path)

        # first create a new changelist
        #changelist = my.add_changelist(description)

        # NOTE: you can only submit individual file to check-in
        # from the default changelist
        my.log.append("p4 submit -r -d \"%s\" \"%s\"" % (description, path))
        if keep_editable:
            ret_val = my.p4.run("submit", "-r", "-d", description, path)
        else:
            ret_val = my.p4.run("submit", "-d", description, path)
        return ret_val


    def commit_changelist(my, changelist="default", description=""):
        keep_open = False       # -r option
        if changelist in [None, 'default']:
            my.log.append("p4 submit -d \"%s\"" % description)
            ret_val = my.p4.run("submit", "-d", description)
        else:
            my.log.append("p4 submit -r -c %s" % changelist)
            ret_val = my.p4.run("submit", "-r", "-c", changelist)
        return ret_val




    def status(my, sync_dir=None):

        if not sync_dir:
            sync_dir = my.sync_dir


        sync_expr = sync_dir
        if sync_expr:
            if os.path.isdir(sync_expr) and not sync_expr.endswith("/..."):
                sync_expr = "%s/..." % sync_expr

        # FIXME: this might be slow on huge repositories

        try:
            if sync_expr:
                my.log.append("p4 diff -sl -f %s"  % sync_expr)
                diff = my.p4.run("diff", "-sl", "-f", sync_expr)
            else:
                my.log.append("p4 diff -sl -f")
                diff = my.p4.run("diff", "-sl", "-f")

        except Exception, e:
            # if there is an exception, likely this is because there are 
            # no files on the client and Perforce does not like this
            print "WARNING: ", e
            print my.p4.run("info")
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
        opened_files = my.p4.run("opened")
        new_files = {} 
        for opened_file in opened_files:
            if opened_file['action'] != 'add':
                continue
            path = opened_file['depotFile']
            path = path.replace("//%s" % my.depot, my.sync_dir)
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




    def add_changelist(my, description, changelist=None):
        changespec = my.p4.fetch_change()
        changespec['Description'] = description
        changespec['User'] = my.user
        info = my.p4.save_change(changespec)
        return info


    def get_changelist_files(my, changelist='default'):
        files = my.p4.run("opened", "-c", changelist)
        return files

    def get_changelist_info(my, changelist='default'):
        info = my.p4.run("describe", changelist)
        return info


    def get_changelists_by_user(my, user=None):
        if not user:
            user = my.user
        changeslists = my.p4.run("changelists", "-u", user, "-s", "pending", "-c", my.client_name)
        return changeslists




    def get_changelists(my, counter='tactic'):
        changeslists = my.p4.run("review", "-t", counter)
        return changeslists


    def set_changelist_counter(my, changelist, counter='tactic'):
        changeslists = my.p4.run("review", "-t", counter, '-c', changelist)
        return changeslists





if __name__ == '__main__':
    scm = PerforceImpl()
    #print "branches: ", svn.get_all_branches()
    #print "tags: ", svn.get_all_tags("3.6")

    repo_dir = "src/main/documents"
    scm.checkout(repo_dir)






