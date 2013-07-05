###########################################################
#
# Copyright (c) 2011, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['BaseSQLConverter']

import tacticenv
from pyasm.common import Environment

import os


# This will convert the upgrade script to one which is compatible with
# sqlite
class BaseSQLConverter(object):
    def __init__(my, vendor):
        my.vendor = vendor
        my.namespace = None


    def convert_upgrade(my, namespace):

        my.namespace = namespace

        upgrade_dir = Environment.get_upgrade_dir() 
        tmp_dir = Environment.get_tmp_dir()

        src_path ="%s/project/%s_upgrade.py" % (upgrade_dir, namespace)
        dst_path = "%s/upgrade/%s/%s_upgrade.py" % (tmp_dir, my.vendor, namespace)

        my.convert_file(src_path, dst_path)

        return dst_path


    def convert_bootstrap(my):
        upgrade_dir = Environment.get_upgrade_dir() 

        file_names = [
                "bootstrap_schema.sql",
                "sthpw_schema.sql",
                "config_schema.sql"
        ]
        for file_name in file_names:
            src_file = "%s/postgresql/%s" % (upgrade_dir, file_name)
            dst_file = "%s/%s/%s" % (upgrade_dir, my.vendor.lower(), file_name)
            print "Converting .."
            print "  from: ", src_file
            print "  to:   ", dst_file
            my.convert_file(src_file, dst_file)




    def convert_file(my, src_path, dst_path):

        upgrade_dir = Environment.get_upgrade_dir() 
        tmp_dir = Environment.get_tmp_dir()

        dir = os.path.dirname(dst_path)
        if dir and not os.path.exists(dir):
            os.makedirs(dir)

        f = open(src_path, 'r')
        f2 = open(dst_path, 'w')

        # prepend lines
        lines = my.get_prepend_lines()
        for line in lines:
            f2.write(line)

        for line in f.xreadlines():
            line = my.handle_line(line)
            if line == None:
                continue
            f2.write(line)

        f.close()
        f2.close()

        return dst_path


    def get_prepend_lines(my):
        return []



