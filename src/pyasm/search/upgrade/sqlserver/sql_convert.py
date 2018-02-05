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


__all__ = ['convert_sqlserver_upgrade']

import tacticenv
from pyasm.common import Environment

import os


def convert_sqlserver_upgrade(namespace):
    converter = SQLServerConverter()
    return converter.convert_upgrade(namespace)



# This will convert the upgrade script to one which is compatible with
# SQLSever 
class BaseSQLConverter(object):
    def __init__(self, vendor):
        self.vendor = vendor
        self.namespace = None


    def convert_upgrade(self, namespace):

        self.namespace = namespace

        upgrade_dir = Environment.get_upgrade_dir() 
        tmp_dir = Environment.get_tmp_dir()

        src_path ="%s/project/%s_upgrade.py" % (upgrade_dir, namespace)
        dst_path = "%s/upgrade/%s/%s_upgrade.py" % (tmp_dir, self.vendor, namespace)

        self.convert_file(src_path, dst_path)

        return dst_path


    def convert_bootstrap(self):
        upgrade_dir = Environment.get_upgrade_dir() 

        file_names = [
                "bootstrap_schema.sql",
                "sthpw_schema.sql",
                "config_schema.sql"
        ]
        for file_name in file_names:
            src_file = "%s/postgresql/%s" % (upgrade_dir, file_name)
            dst_file = "%s/%s/%s" % (upgrade_dir, self.vendor.lower(), file_name)
            print "Converting .."
            print "  from: ", src_file
            print "  to:   ", dst_file
            self.convert_file(src_file, dst_file)




    def convert_file(self, src_path, dst_path):

        upgrade_dir = Environment.get_upgrade_dir() 
        tmp_dir = Environment.get_tmp_dir()

        dir = os.path.dirname(dst_path)
        if dir and not os.path.exists(dir):
            os.makedirs(dir)

        f = open(src_path, 'r')
        f2 = open(dst_path, 'w')

        # prepend lines
        lines = self.get_prepend_lines()
        for line in lines:
            f2.write(line)

        for line in f.xreadlines():
            line = self.handle_line(line)
            if line == None:
                continue
            f2.write(line)

        f.close()
        f2.close()

        return dst_path


    def get_prepend_lines(self):
        if self.namespace:
            return []
        else:
            return ["SET QUOTED_IDENTIFIER ON;\n"];



class SQLServerConverter(BaseSQLConverter):

    def __init__(self):
        self.vendor = 'SQLServer'
        self.namespace = None


    def handle_line(self, line):
        # FIXME: this could be genealized with self.vendor
        if line.startswith("class "):
            line = "class %s%sUpgrade(BaseUpgrade):\n" % (self.vendor, self.namespace.capitalize())

        elif line.startswith("__all__ "):
            line = "__all__ = ['%s%sUpgrade']\n" % (self.vendor, self.namespace.capitalize())


        #if line.find("timestamp") != -1 and line.find("now()") == -1:
        #    line = line.replace("timestamp", "timestamp NULL DEFAULT NULL")

        line = line.replace("SET sql_mode='ANSI_QUOTES';", "SET QUOTED_IDENTIFIER ON;")
        line = line.replace(" text"                      , " nvarchar(max)")
        line = line.replace(" ntext"                     , " nvarchar(max)")
        line = line.replace(" varchar("                  , " nvarchar(")
        line = line.replace(" character varying("        , " nvarchar(")
        line = line.replace(" timestamp"                 , " datetime2(6)")
        line = line.replace("boolean"                    , "BIT")
        line = line.replace(" rule "                     , " rule ")
        line = line.replace(" DEFAULT now()"             , " DEFAULT (getdate())")
        line = line.replace(" default now()"             , " DEFAULT (getdate())")
        line = line.replace(" without time zone"         , "")
        line = line.replace(" with time zone"            , "")
        line = line.replace("id serial"                  , "id integer IDENTITY")
        line = line.replace("create unique index "       , "CREATE UNIQUE INDEX ")
        line = line.replace(" TYPE"                      , "")
        line = line.replace("(id)"                       , "")
        line = line.replace(" add column"                , " add")
        line = line.replace(" ADD COLUMN"                , " ADD")
        line = line.replace(" TABLE file "              , " TABLE \"file\" ")
        line = line.replace(" status nvarchar(max)"      , " status nvarchar(256)")
        # string concatenation
        line = line.replace("||"                         , "+")
        # note: SQLServer uses " alter column" to change datatypes

        return line


if __name__ == '__main__':

    converter = SQLServerConverter()
    converter.convert_bootstrap()


