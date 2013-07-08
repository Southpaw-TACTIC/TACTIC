import sys
import os
import getopt
import traceback

import httplib
import urllib

# -------------------------------------------------------------------------------------------------------
#
#                        TACTIC Client API version bootstrap example script
#                        __________________________________________________
#
#
# == Summary ==
#
#        This script is an example of how to manage client API access to multiple versions of TACTIC, or
#    to manage client API access through upgrades and rollbacks of versions of a single TACTIC server.
#
#    What is required for this approach to work, and for this script to run successfully, are 2 things:
#
#    (1) that in each TACTIC install the VERSION file, at the very top of a TACTIC install, is copied
#        as a file named VERSION.txt into the src/context folder
#
#    (2) that every time a specific version of TACTIC is installed on the TACTIC server, a copy of
#        that version's src/client folder is pushed out to client workstations before a specific server
#        version install is switched to for the live TACTIC server
#
#        NOTE: this script assumes that these client-side copies of the client API package are located
#              and named in the following manner ...
#
#
#                C:\sthpw\client_api\tactic-2.6.0.rc01\client
#
#                C:\sthpw\client_api\tactic-2.6.0.rc02\client
#
#                C:\sthpw\client_api\tactic-2.6.0.v01\client
#
#
#              ... it is up to each studio to determine the location of, and the mechanism to push out
#              new versions of, the client API packages that need to be made available to client-side
#              running scripts.
#
#
# == The Concept ==
#
#        The overall concept here is to provide a way for pipeline scripts that need access to TACTIC
#    (and that will be running on client workstations) to be able to seamlessly load the appropriate
#    client API version that precisely matches the TACTIC version of the server that the script will be
#    accessing through the TACTIC client API.
#
#    To accomplish this, we establish a "bootstrap" function, see bootstrap_get_tactic_server_stub()
#    below, that is actually completely independent of TACTIC server version. This bootstrap function
#    is able to make an HTTP request to a specific TACTIC server (without using the TACTIC client API
#    which is TACTIC version dependent), in order to obtain the version of that TACTIC server. Once
#    the version is known, the bootstrap function dynamically appends the "client" folder of the matching
#    client API version that is accessible by the client workstation. The script then does the import
#    of the appropriate module class and then instantiates a tactic server stub instance against the
#    correct client API version and returns that server stub instance to the calling program.
#
#    So, this bootstrap function would need to become part of the standard studio python libraries
#    that would always be available to pipeline python scripts. All scripts in the pipeline that
#    needed to access TACTIC would then be designed to always use this bootstrap function to obtain
#    a connection to the given TACTIC server it would be running against.
#
# -------------------------------------------------------------------------------------------------------


def bootstrap_get_tactic_server_stub( tactic_server_str, project_code, login, password ):

    conn = httplib.HTTPConnection(tactic_server_str)
    conn.request("GET", "/context/VERSION.txt")

    response = conn.getresponse()
    # print response.status, response.reason

    data = response.read()
    tactic_version = data.strip()

    conn.close()

    print
    print "> Found TACTIC version '%s' running on server %s ..." % (tactic_version, tactic_server_str)
    print

    client_lib_install_path = "C:/sthpw/client_api/tactic-%s/client" % tactic_version

    print "  ... attempting to import 'TacticServerStub' from 'tactic_client_lib' located in:"
    print
    print "         %s" % client_lib_install_path
    print

    try:
        sys.path.append( client_lib_install_path )
        from tactic_client_lib import TacticServerStub
        if not login or not password:
            print
            print "> Warning: login/password not provided, assuming the use of .tacticrc ticket ..."
            print
            tactic_server = TacticServerStub(server=tactic_server_str, project=project_code)
        else:
            tactic_server = TacticServerStub(
                                server=tactic_server_str,
                                project=project_code,
                                user=login,
                                password=password
                            )
    except:
        print "  ERROR: unable to access TACTIC client API for server version '%s'" % (tactic_version)
        if not login or not password:
            print "           (likely there is no .tacticrc ticket that exists)"

        print
        print "Exception found:"
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        print
        tactic_server = None

    return tactic_server


def usage():

    script_name = os.path.basename(sys.argv[0])
    print
    print "  Usage: %s [options] <tactic_server_str> <project_code>" % (script_name)
    print
    print "         ____ OPTIONS ____"
    print
    print "         -h, --help ... print this usage message"
    print
    print "         -i, --interactive ... interactive user prompts to enter login & password"
    print
    print "         -l <login>, --login <login> ... user login"
    print "         -p <password>, --password <password> ... user password"
    print
    print "         NOTE: use only one of ... -i OR (-l <login> and -p <password>)"
    print "               if none of those options are used it is assumed to use an"
    print "               existing .tacticrc ticket"
    print
    print "    e.g. python %s -l dsmith -p mypassword 192.168.188.134 sample3d" % (script_name)
    print


if __name__ == '__main__':

    login = None
    password = None

    use_ticket = False
    prompt_user = False

    short_opts = "hil:p:"
    long_opts = [ "help", "interactive", "login=", "password=" ]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
    except getopt.error:
        usage()
        sys.exit(1)

    if len(args) != 2:
        usage()
        sys.exit(1)

    tactic_server_str = args[0]
    project_code = args[1]

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-i", "--interactive"):
            prompt_user = True
        elif opt in ("-l", "--login"):
            login = arg
        elif opt in ("-p", "--password"):
            password = arg

    if prompt_user:

        login = raw_input("  Enter TACTIC login (just ENTER for current user): ")
        if not login:
            if sys.platform == 'win32':
                login = os.environ.get('USERNAME')
            else:
                login = os.environ.get('USER')

        password = raw_input("  Enter TACTIC password for user '%s': " % login)
        if not password:
            print
            print "*** password required to run script ... no password entered ... aborting."
            print
            sys.exit(1)

    else:
        if not (login and password) and not (not login and not password):
            usage()
            sys.exit(1)

    tactic_server = bootstrap_get_tactic_server_stub(tactic_server_str, project_code, login, password)

    if tactic_server:
        print
        print "ping: [%s]" % tactic_server.ping()
        print
    else:
        print
        print "*** NO connection to TACTIC server obtained ... unable to ping server ***"
        print


