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

    def __init__(my, **kwargs):
        my.kwargs = kwargs
        my.base_dir = my.kwargs.get("base_dir")
        if my.base_dir:
            my.base_dir = my.base_dir.replace("\\", "/")

        my.depth = my.kwargs.get("depth")
        if isinstance(my.depth, basestring):
            my.depth = int(depth)
        if not my.depth:
            my.depth = 0

        my.paths = my.kwargs.get("paths")
        if my.paths == None:
            my.paths = my.read_file_system()

        my.paths.sort()

        # organize the paths into a dictionary structure
        my.organize(my.paths)


    def get_all_paths(my):
        return my.paths



    def find(my, path, use_full_path=True):
        path = path.rstrip("/")
        parts = path.split("/")

        paths = []
        cur = my.data_graph

        for part in parts:
            if part == '':
                continue
            cur = cur.get(part)

        if use_full_path == True:
            full_path = path
        else:
            full_path = None

        parts = []
        my._find(cur, full_path, paths)
        return paths




    def _find(my, cur, full_path, paths):
        for key, value in cur.items():
            if full_path:
                tmp_full_path = "%s/%s" % (full_path, key)
            else:
                tmp_full_path = key

            if value.get("__type__") == 'file':
                paths.append(tmp_full_path)
            else:
                my._find(value, tmp_full_path, paths)
        


    def read_file_system(my):
        max_count = 100000
        count = 0
        last_root = None
        paths = []

        #### FIXME: HARD CODED
        ignore_dirs = ['.svn', 'backup']

        for root, xdirs, files in os.walk(unicode(my.base_dir)):

            if my.depth != -1:
                test = root.strip("/")
                parts = test.split("/")
                if len(parts) > my.depth + 1:
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

            if count > max_count:
                break


        return paths



    def organize(my, paths):
        #dir_list = [x for x in paths]
        #dir_list.reverse()

        my.data_graph = {}

        count = 0
        for path in paths:

            parts = path.split("/")
            num = len(parts)
            cur = my.data_graph
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






