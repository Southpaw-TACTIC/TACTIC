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

__all__ = ['Perforce']

import os, re
#from popen2 import popen3
from subprocess import Popen

class PerforceException(Exception):
    pass


class Perforce(object):

    PORT = "1666"

    def get_exec_path(self):
        return "p4"

    def execute(self, cmd, input="", no_exception=False):

        no_exception = True

        p4_cmd = "%s %s" % (self.get_exec_path(), cmd)
        print p4_cmd
        #pipe = popen3(p4_cmd)
        # FIXME: this has not been fixed for the supprocess command
        pipe = Popen(pr_cmd)
        if input:
            #print input
            stdin = pipe[1]
            stdin.write(input)
            stdin.close()

        error = pipe[2].readlines()
        if error:
            for e in error:
                print "ERROR: ", e
            if no_exception:
                pass
            else:
                raise PerforceException(error[0])

        stdout = pipe[0].readlines()
        if not stdout:
            return [""]

        return stdout


    def add_file(self, path):
        path = path.replace("//", "/")
        cmd = "add \"" + path + "\""
        ret_val = self.execute(cmd)
        if ret_val[0].count("can't add existing file"):
            raise PerforceException(ret_val[0])
        print ret_val


    def get_checkout(self, path):
        cmd = "opened \"" + path + "...\""
        ret_val = self.execute(cmd.toString())
        return ret_val


    def get_repo(self, path, synced=True):
        '''find all files in the repo'''
        p4_cmd = "files"
        if synced:
            p4_cmd = "have"
        cmd = p4_cmd + " \"" + path + "...\""
        ret_val = self.execute(cmd)
        return ret_val


    def checkin(self, path):
        cmd = 'add "%s"' % path
        ret_val = self.execute(cmd)
        return "|".join(ret_val) 


    def edit(self, path):
        path = path.replace("//", "/")
        cmd = "edit \"" + path + "\""
        ret_val = self.execute(cmd)
        return "|".join(ret_val)
 

    def revert(self, path):
        cmd = "revert -a \"" + path + "\""
        ret_val = self.execute(cmd)
        return "|".join(ret_val)


    def sync(self, path):
        cmd = 'sync -f "%s"' % path
        ret_val = self.execute(cmd)
        return "|".join(ret_val) 


    def delete(self, path):
        cmd = 'delete "%s"' % path
        ret_val = self.execute(cmd)
        print ret_val
        return "|".join(ret_val)


    def get_root(self):
        ret_val = self.execute("workspaces")
        tmp = ret_val[0].split(" ")

        # HACK: big hack to overcome the bad output from perforce
        path = tmp[4];
        for i in range(5, len(tmp) ):
            if not tmp[i].startswith("'"):
                path += " " + tmp[i]
            else:
                break

        root = path.replace("\\", "/")
        return root


    def get_workspaces(self):
        ret_val = self.execute("workspaces")
        return ret_val
        #root = Common.hexify(ret_val)
        #return root;




 
     
    # param@ paths - list of file paths to be commited
    # param@ description - check in description
    # param@ root - P4 client installation root path
    def commit(self, description, paths=[], root=None):

        # if no root is specified, then get it from perforce
        if not root:
            root = self.get_root()

        info = {}
            

        # Start a new changelist
        description_key = "<enter description here>"
        output = self.execute("change -o")
       
        input = []
        files = []
        line = None

        files_flag = False

        for line in output:
            # replace description
            line = line.replace(description_key, description);

            if line.startswith("Files:" ):
                files_flag = True
            #elif files_flag and not self.match_path(paths, line):
            #    print "file: ", line
            #    continue
            if files_flag and line != "\n":
                print 'file: ', line
                files.append(line)

            input.append(line)



        # if the are no file, do nothing
        if not files:
            info['message'] = "There are no files to checkin.";
            return info


        input_str = "".join( input )

        ret_val = self.execute("change -i", input_str)
        ret_val_str = "\n".join( ret_val )

        # get the change list number
        tmp = ret_val_str.split(" ")
        changelist = int(tmp[1])

        # submit the change
        ret_val = self.execute("submit -c %s" % changelist )

        # parse the return value
        info['message'] = "|".join(ret_val)

        info['revision'] = self.extract_value("Submitting change (\d+)", ret_val[0])

        num_files = self.extract_value("Locking (\d+) files", ret_val[1])

        files = []
        for line in ret_val:
            if line.startswith("edit") or line.startswith("add"):
                values = self.extract_values("\w+ (.*)#(\d+)", line)
                path = values[0]
                version = values[1]

                files.append( {'path': path, 'version': version} )
                
        info['files'] = files


        return info






    # Match the line with one of the given paths
    def match_path(self, paths, line):
        matched = False;
        # force only the output paths to lower case
        i = 0
        while not matched and i < len(paths):
            if line.count(paths[i]):
                matched = True
                break
            i += 1
        return matched


    def extract_values(self, expr, line):
        p = re.compile(expr, re.DOTALL)
        m = p.search(line)
        if not m:
            return []
        values = m.groups()
        return values


    def extract_value(self, expr, line):
        values = self.extract_values(expr,line)
        if not values:
            return None
        return values[0]






if __name__ == '__main__':

    p = Perforce()
    root = p.get_root()
    print "root: ", root
    #print "repo: ", p.get_repo("%s/whatever/"% root)

    files = []
    files.append("%s/whatever/connector.tar.gz" % root)
    files.append("%s/whatever/fix.sql" % root)



