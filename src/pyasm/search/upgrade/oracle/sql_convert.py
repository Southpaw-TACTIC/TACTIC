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


__all__ = ['convert_oracle_upgrade']

import tacticenv
from pyasm.common import Environment
from pyasm.search.upgrade import BaseSQLConverter

import os


def convert_oracle_upgrade(namespace):
    converter = SqlServerConverter()
    return converter.convert_upgrade(namespace)



class OracleConverter(BaseSQLConverter):

    def __init__(my):
        my.vendor = 'Oracle'
        my.namespace = None



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

        if line.find(" text") != -1:
            line = line.replace(" text", " VARCHAR(MAX)")

        elif line.find(" serial") != -1:
            line = line.replace(" serial", " INT IDENTITY")

        return line


if __name__ == '__main__':

    converter = OracleConverter()
    converter.convert_bootstrap()


