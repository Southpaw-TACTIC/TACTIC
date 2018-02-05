###########################################################
#
# Copyright (c) 2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ["Directory"]

import sys, os

from common import Common
from config import Config

class Directory(object):
    '''Implementation of a virtual directory'''

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.base_dir = self.kwargs.get("base_dir")
        if self.base_dir:
            self.base_dir = self.base_dir.replace("\\", "/")

        self.depth = self.kwargs.get("depth")
        if isinstance(self.depth, basestring):
            self.depth = int(self.depth)
        if not self.depth:
            self.depth = 0

        self.paths = self.kwargs.get("paths")
        if self.paths == None:
            self.paths = self.read_file_system()

        self.paths.sort()

        # organize the paths into a dictionary structure
        self.organize(self.paths)


    def get_all_paths(self):
        return self.paths



    def find(self, path, use_full_path=True):
        path = path.rstrip("/")
        parts = path.split("/")

        paths = []
        cur = self.data_graph

        for part in parts:
            if part == '':
                continue
            cur = cur.get(part)

        if use_full_path == True:
            full_path = path
        else:
            full_path = None

        parts = []
        self._find(cur, full_path, paths)
        return paths




    def _find(self, cur, full_path, paths):
        for key, value in cur.items():
            if full_path:
                tmp_full_path = "%s/%s" % (full_path, key)
            else:
                tmp_full_path = key

            if value.get("__type__") == 'file':
                paths.append(tmp_full_path)
            else:
                self._find(value, tmp_full_path, paths)
        


    def read_file_system(self):
        max_count = 100000
        count = 0
        last_root = None
        paths = []

        #### FIXME: HARD CODED
        ignore_dirs = ['.svn', 'backup']

        for root, xdirs, files in os.walk(unicode(self.base_dir)):

            if self.depth != -1:
                test = root.replace(self.base_dir, "")
                test = test.strip("/")
                parts = test.split("/")
                if len(parts) > self.depth + 1:
                    for xdir in xdirs:
                        xdirs.remove(xdir)
                    continue

            for ignore in ignore_dirs:
                if ignore in xdirs:
                    xdirs.remove(ignore)

            for xdir in xdirs:

                path = "%s/%s/" % (root, xdir)
                paths.append(path)

                count += 1
                if count > max_count:
                    break

            for file in files:
                path = "%s/%s" % (root, file)
                paths.append(path)

                count += 1
                if count > max_count:
                    break

            # special consideration for when depth is 0
            if self.depth == 0:
                break

            if count > max_count:
                break


        return paths



    def organize(self, paths):
        #dir_list = [x for x in paths]
        #dir_list.reverse()

        self.data_graph = {}

        count = 0
        for path in paths:

            parts = path.split("/")
            num = len(parts)
            cur = self.data_graph
            for i, part in enumerate(parts):
                # skip extra from split on first slash
                if part == '':
                    continue

                #if i == num-2:
                #    cur[part] = []
                #    continue


                x = cur.get(part)
                if x == None:
                    x = {}
                    cur[part] = x

                cur = x

                # if this is a file, then mark it
                if i == num-1:
                    cur['__type__'] = 'file'
                #else:
                #    cur['__type__'] = 'directory'






