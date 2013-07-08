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


# DEPRECATED: This is replace by sql_convert.py




__all__ = ['convert_sqlite_upgrade']

import tacticenv
from pyasm.common import Environment

import os


# This will convert the upgrade script to one which is compatible with
# sqlite


def convert_sqlite_upgrade(namespace):

    upgrade_dir = Environment.get_upgrade_dir() 
    tmp_dir = Environment.get_tmp_dir()

    src_path ="%s/project/%s_upgrade.py" % (upgrade_dir, namespace)
    path = "%s/upgrade/sqlite/%s_upgrade.py" % (tmp_dir, namespace)
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

    f = open(src_path, 'r')
    f2 = open(path, 'w')


    for line in f.xreadlines():
        if line.find("serial PRIMARY KEY") != -1:
            line = line.replace("serial PRIMARY KEY", "integer PRIMARY KEY AUTOINCREMENT")
        elif line.find("PRIMARY KEY") != -1:
            if line.find("ALTER TABLE") != -1:
                pass
            else:
                pass


        elif line.find("now()") != -1:
            line = line.replace("now()", "CURRENT_TIMESTAMP")

        elif line.startswith("class "):
            line = "class Sqlite%sUpgrade(BaseUpgrade):\n" % namespace.capitalize()

        elif line.startswith("__all__ "):
            line = "__all__ = ['Sqlite%sUpgrade']\n" % namespace.capitalize()


        f2.write(line)
        #print line.rstrip()

    f.close()
    f2.close()

    return path


if __name__ == '__main__':
    convert_sqlite_upgrade()

