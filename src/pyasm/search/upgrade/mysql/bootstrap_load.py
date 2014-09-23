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


import tacticenv

from pyasm.common import Environment, Xml, Config
from pyasm.search import DatabaseImpl

from tactic.command import PluginCreator, PluginInstaller

import os


class FakeSecurity(object):
    def check_access(my, *args):
        return True
    def get_user_name(my):
        return "admin"
    def get_login(my):
        return my
    def alter_search(my, search):
        pass
    def get_ticket(my):
        from pyasm.search import SearchType
        ticket = SearchType.create("sthpw/ticket")
        return ticket
    def get_ticket_key(my):
        return ""


def import_bootstrap():
    print "Importing bootstrap ..."
    vendor = "MySQL"

    impl = DatabaseImpl.get(vendor)
    impl.create_database("sthpw")


    upgrade_dir = Environment.get_upgrade_dir()

    for category in ['bootstrap', 'sthpw', 'config']:
        f = open("%s/%s/%s_schema.sql" % (upgrade_dir, vendor.lower(), category) )
        data = f.read()
        f.close()

        data = data.split(";")

        cmds = []
        for cmd in data:
            cmd = cmd.strip()
            if cmd == '':
                continue
            cmds.append(cmd)

        from pyasm.search import DbContainer
        sql = DbContainer.get("sthpw")
        for cmd in cmds:
            sql.do_update(cmd)


# NOTE: this requires plugins and is likely not necessary for initial load
# of schema
def import_schema(plugin_code):
    from pyasm.search import Transaction
    transaction = Transaction.get(create=True)

    install_dir = Environment.get_install_dir()
    base_dir = Environment.get_plugin_dir()
    template_dir = "%s/%s" % (base_dir, plugin_code)
    manifest_path = "%s/manifest.xml" % (template_dir)
    print "Reading manifest: ", manifest_path

    xml = Xml()
    xml.read_file(manifest_path)

    # create a new project
    installer = PluginInstaller(base_dir=base_dir, manifest=xml.to_string() )
    installer.execute()


def upgrade():
    print "Running upgrade on 'sthpw' database"

    install_dir = Environment.get_install_dir()
    from pyasm.common import Config  
    python = Config.get_value("services", "python")
    if not python:
        python = "python"

    cmd = "%s \"%s/src/bin/upgrade_db.py\" -f -y -p sthpw" % (python, install_dir)
    print cmd

    os.system(cmd)




if __name__ == '__main__':

    Environment.set_security(FakeSecurity())
    import_bootstrap()
    #import_schema("sthpw_schema")
    #import_schema("config_schema")

    from pyasm.security import Batch
    Batch()

    # upgrade the database using the upgrade script
    upgrade()



