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

import sys
import hashlib


def get_md5(path):
    '''get md5 checksum'''
    try:
        f = open(path, 'rb')
        # this chunk size affects the speed a little but not significant enough
        # in most cases
        CHUNK = 1024*1024
        #m = md5.new()
        m = hashlib.md5()
        while 1:
            chunk = f.read(CHUNK)
            if not chunk:
                break
            m.update(chunk)
        md5_checksum = m.hexdigest()
        f.close()
        return md5_checksum
    except IOError, e:
        # do not print to stdout, write to stderr later if desired
        sys.stderr.write("WARNING: error getting md5 on [%s]: " % path)
        return None

if __name__ == '__main__':
    executable = sys.argv[0]
    args = sys.argv[1:]
    if len(args) == 1:
        md5_val = get_md5(args[0])
        if md5_val:
            sys.stdout.write(md5_val)
    sys.exit(0)

