###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

# interactive utility to change database information


__all__ = ['Install']


import os, shutil, sys

import tacticenv
from pyasm.common import Config


class InstallException(Exception):
    pass

class ChangeDbPassword:

    def execute(my):

        my.print_header()

        # install the necessary files to python directory
        my.ask_questions()


    def print_header(my):
        print
        print
        print "*"*20
        print "TACTIC Database Configuration"
        print "*"*20
        print



    def ask_questions(my):

        # set vendor
        default_vendor = Config.get_value("database", "vendor")
        print
        print "Please enter the database vendor (PostgreSQL or Oracle):"
        print
        while 1:
            if not default_vendor:
                default_vendor = "PostgreSQL"
            vendor = raw_input("(%s) -> " % default_vendor)
            if not vendor:
                vendor = default_vendor
            print

            if vendor in ['PostgreSQL', 'Oracle']:
                break
            else:
                print "ERROR: Vendor must one of 'PostgreSQL' or 'Oracle'"
                print


        # set server
        default_server = Config.get_value("database", "server")
        if not default_server:
            default_server = "localhost"
        print
        print "Please enter database server hostname or IP address:"
        print
        server = raw_input("(%s) -> " % default_server)
        if not server:
            server = default_server
        print



        # set the user
        default_user = Config.get_value("database", "user")
        if not default_user:
            default_user = "__EMPTY__"
        print
        print "Please enter user name accessing the database:"
        if vendor == "Oracle":
            print "    (To access Oracle using schema names, type '__EMPTY__')"
        print
        user = raw_input("(%s) -> " % default_user)
        if not user:
            user = default_user
        print



        # set password
        from pyasm.search import DbPasswordUtil
        current_password = DbPasswordUtil.get_password()
        password = 0
        password2 = 1
        print
        print "Please enter database password:"
        print "  (ENTER to keep password, '__EMPTY__' for empty password)"

        import getpass
        while password != password2:
            print
            password = getpass.getpass("Enter Password -> ")

            if password:
                password2 = getpass.getpass("Confirm Password -> ")
            else:
                password = current_password
                password2 = password
                break

            print

            if password == password2:
                break
            else:
                print "ERROR: Passwords do not match"


        # Summary:
        print
        print "Vendor:   [%s]" % vendor
        print "Server:   [%s]" % server
        print "User:     [%s]" % user
        print

        ok = raw_input("Save to config (N/y) -> ")
        if ok.lower() != "y":
            print "Aborted"
            return


        # save the info
        from pyasm.search import DbPasswordUtil
        DbPasswordUtil.set_password(password)

        Config.set_value("database", "vendor", vendor)
        Config.set_value("database", "server", server)

        if user == "__EMPTY__":
            user = ""
        Config.set_value("database", "user", user)
        Config.save_config()
        path = Config.get_config_path()

        print
        print "Saved new database information to [%s].  Please restart TACTIC for the changes to take effect" % path
        print

        '''
        test = raw_input("Test Connection (N/y) -> ")
        if test.lower() != "y":
            return

        print
        print "Testing ..."
        from pyasm.search import DbContainer, DatabaseException
        try:
            sql = DbContainer.get("sthpw")
        except DatabaseException:
            print
            print "ERROR: Could not connect"
        else:
            print "Connection successful"
        '''








if __name__ == '__main__':
    cmd = ChangeDbPassword()
    cmd.execute()
    



