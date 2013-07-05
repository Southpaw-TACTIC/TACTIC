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


__all__ = ['convert_mysql_upgrade']

import tacticenv
from pyasm.common import Environment
from pyasm.search.upgrade import BaseSQLConverter

import os


def convert_mysql_upgrade(namespace):
    converter = MySQLConverter()
    return converter.convert_upgrade(namespace)



class MySQLConverter(BaseSQLConverter):

    def __init__(my):
        my.vendor = 'MySQL'
        my.namespace = None


    def get_prepend_lines(my):
        if my.namespace:
            return []
        else:
            return ["SET sql_mode='ANSI_QUOTES';\n"];



    def handle_line(my, line):
        #if line.find("now()") != -1:
        #    line = line.replace("now()", "CURRENT_TIMESTAMP")

        # FIXME: this could be genealized with my.vendor
        if line.startswith("class "):
            line = "class %s%sUpgrade(BaseUpgrade):\n" % (my.vendor, my.namespace.capitalize())

        elif line.startswith("__all__ "):
            line = "__all__ = ['%s%sUpgrade']\n" % (my.vendor, my.namespace.capitalize())

        line = line.replace("without time zone", "")
        line = line.replace("with time zone", "")

        if line.find("timestamp") != -1 and line.find("now()") == -1 and \
                line.find("timestamp_idx") == -1:
            line = line.replace("timestamp", "timestamp NULL DEFAULT NULL")


        return line


if __name__ == '__main__':

    converter = MySQLConverter()
    converter.convert_bootstrap()


