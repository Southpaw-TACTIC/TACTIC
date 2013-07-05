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

import sys, os, getpass

try:
    import tacticenv
except ImportError:
    pass

from tactic_client_lib import TacticServerStub


def main(args):

    server = TacticServerStub(setup=False)
    server.get_info_from_user(force=True)
    return

    """
    old_server_name = server.server_name
    old_project_code = server.project_code
    default_login = getpass.getuser()

    print
    server_name = raw_input("Enter name of TACTIC server (%s): " % old_server_name)
    if not server_name:
        server_name = old_server_name

    print
    login = raw_input("Enter user name (%s): " % default_login)
    if not login:
        login = default_login

    print
    password = getpass.getpass("Enter password: ")

    print
    project_code = raw_input("Project (%s): " % old_project_code)
    if not project_code:
        project_code = old_project_code

    server.set_server(server_name)


    # commit info to a file
    if os.name == "nt":
        dir = "C:/sthpw/etc"
    else:
        dir = "/tmp/sthpw/etc"
    if not os.path.exists(dir):
        os.makedirs(dir)

    filename = "%s.tacticrc" % login
    path = "%s/%s" % (dir,filename)

    # do the actual work
    ticket = server.get_ticket(login, password)
    print "Got ticket [%s] for [%s]" % (ticket, login)

    file = open(path, 'w')
    file.write("login=%s\n" % login)
    file.write("server=%s\n" % server_name)
    file.write("ticket=%s\n" % ticket)
    if project_code:
        file.write("project=%s\n" % project_code)

    file.close()
    print
    print "Saved to [%s]" % path
    """



if __name__ == '__main__':
    
    executable = sys.argv[0]
    args = sys.argv[1:]
    main(args)

