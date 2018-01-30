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


__all__ = ['convert_sqlite_upgrade']

import tacticenv
from pyasm.common import Environment
from pyasm.search.upgrade import BaseSQLConverter

import os


def convert_sqlite_upgrade(namespace):
    converter = SqliteConverter()
    return converter.convert_upgrade(namespace)



class SqliteConverter(BaseSQLConverter):

    def __init__(self):
        self.vendor = 'Sqlite'
        self.namespace = None


    def get_prepend_lines(self):
        return []



    def handle_line(self, line):

        # FIXME: this could be genealized with self.vendor
        if line.startswith("class "):
            line = "class %s%sUpgrade(BaseUpgrade):\n" % (self.vendor, self.namespace.capitalize())

        elif line.startswith("__all__ "):
            line = "__all__ = ['%s%sUpgrade']\n" % (self.vendor, self.namespace.capitalize())

        if line.find("serial PRIMARY KEY") != -1:
            line = line.replace("serial PRIMARY KEY", "integer PRIMARY KEY AUTOINCREMENT")
        elif line.find("PRIMARY KEY") != -1:
            if line.find("ALTER TABLE") != -1:
                pass
            else:
                pass


        #elif line.find("boolean") != -1:
        #    line = line.replace("boolean", "integer")

        elif line.find("now()") != -1:
            line = line.replace("now()", "CURRENT_TIMESTAMP")

        return line


if __name__ == '__main__':

    converter = SqliteConverter()
    converter.convert_bootstrap()


