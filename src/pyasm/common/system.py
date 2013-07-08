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

__all__ = ["System"]

import sys, os, platform
import errno

from common import Common
from config import Config


def System():
    return _System.get()


class _System(object):
    '''Class which abstracts all system commands in TACTIC.  By default,
    TACTIC will use standard python libraries for this'''
    system_handler = None

    def get(cls):
        if not cls.system_handler:
            system_class = Config.get_value("services", "system_class")
            if not system_class:
                cls.system_handler = _System()
            else:
                cls.system_handler = Common.create_from_class_path(system_class)
        
        return cls.system_handler
    get = classmethod(get)




    def makedirs(cls, dir, mode=None):
        '''wrapper to makedirs'''
        if not os.path.exists(dir):
            # this is done to avoid multiple calls to this function causing
            # a race to make the same directory
            try:
                if mode:
                    os.makedirs(dir, mode)
                else:
                    os.makedirs(dir)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
    makedirs = classmethod(makedirs)

    def exists(cls, path):
        '''wrapper to makedirs'''
        if not os.path.exists(path):
            # Deal with some (possibly NFS) problem.
            try:
                os.listdir(os.path.dirname(path))
            except Exception:
                # if there is an error here, then report False
                return False

            # if it still does not exist
            if not os.access(path, os.F_OK):
                return False

        return True
    exists = classmethod(exists)



    def memory_usage(cls):
        """Memory usage of the current process in kilobytes."""
        """from: http://stackoverflow.com/questions/897941/python-equivalent-of-phps-memory-get-usage"""


        status = None
        result = {'peak': 0, 'rss': 0}
        system = platform.system()

        if os.name == 'nt':
            return result

        if system == "Darwin":
            return result

        try:
            try:
                # This will only work on systems with a /proc file system
                # (like Linux).
                status = open('/proc/self/status')
                for line in status:
                    parts = line.split()
                    key = parts[0][2:-1].lower()
                    if key in result:
                        result[key] = int(parts[1])
            except Exception, e:
                print "WARNING: ", e
        finally:
            if status is not None:
                status.close()
        return result

    memory_usage = classmethod(memory_usage)



