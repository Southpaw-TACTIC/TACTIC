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
from __future__ import print_function


import os, sys

# set up environment
os.environ['TACTIC_APP_SERVER'] = "cherrypy"
os.environ['TACTIC_MODE'] = "development"
os.environ['TACTIC_CLEANUP'] = "true"

import tacticenv
# This will also set some paths
from pyasm.common import Environment, Config

"""
tactic_install_dir = tacticenv.get_install_dir()
tactic_site_dir = tacticenv.get_site_dir()


sys.path.insert(0, "%s/src" % tactic_install_dir)
sys.path.insert(0, "%s/tactic_sites" % tactic_install_dir)
sys.path.insert(0, tactic_site_dir)
"""



def startup(port, server=""):

    from tactic.startup import FirstRunInit
    cmd = FirstRunInit()
    cmd.execute()

    log_dir = "%s/log" % Environment.get_tmp_dir()
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

   
    try:
        file = open("%s/pid.%s" % (log_dir,port), "w")
        pid = os.getpid()
        file.write(str(pid))
        file.close()
    except IOError as e:
        if e.errno == 13:
            print(" ")
            print("Permission error opening the file [%s/pid.%s]." % (log_dir,port))
            print(" ")
            if os.name=='nt':
                print("You may need to run this shell as the Administrator.")
            else:
                print("The file should be owned by the same user that runs this startup_dev.py process.")
            sys.exit(2)



    if os.name != 'nt' and os.getuid() == 0:
        print(" ") 
        print("You should not run this as root. Run it as the Web server process's user. e.g. apache")
        print(" ") 
        sys.exit(0)

    import cherrypy
    try:
        cherrypy_major_version = int(cherrypy.__version__.split('.')[0])
    except:
        cherrypy_major_version = 3

    if cherrypy_major_version >= 3:
        from pyasm.web.cherrypy30_startup import CherryPyStartup
        startup = CherryPyStartup(port)

        startup.set_config('global', 'server.socket_port', port)
        startup.set_config('global', 'server.socket_queue_size', 100)
        startup.set_config('global', 'server.thread_pool', 50)


        startup.set_config('global', 'log.screen', False)

        startup.set_config('global', 'request.show_tracebacks', True)
        startup.set_config('global', 'server.log_unhandled_tracebacks', True)

        startup.set_config('global', 'engine.autoreload_on', True)


        """ 
        access_log = cherrypy.log.access_log
        for handler in tuple(access_log.handlers):
            access_log.removeHandler(handler)
        cherrypy.log.error_log.propagate = False
        cherrypy.log.access_log.propagate = False
        """





    else:
        from pyasm.web.cherrypy_startup import CherryPyStartup
        startup = CherryPyStartup(port)
        startup.set_config('global', 'server.environment', 'development')
        startup.set_config('global', 'server.socket_port', port)
        
        startup.set_config('global', 'server.log_to_screen', True)
        startup.set_config('global', 'server.socket_queue_size', 100)
        startup.set_config('global', 'server.thread_pool', 100)
        #startup.set_config('global', 'server.socket_host', server)

        startup.set_config('global', 'server.log_tracebacks', True)
        startup.set_config('global', 'server.log_unhandled_tracebacks', True)

    hostname = None
    server_default = '127.0.0.1'
    
    if not server:
        hostname = Config.get_value("install", "hostname") 
        if hostname == 'localhost':
            # swap it to IP to suppress CherryPy Warning
            hostname = server_default
        if hostname:
            # special host name for IIS which can't load balance across many
            # ports with the same service
            hostname = hostname.replace("{port}", str(port))
            server = hostname
        else:
            server = server_default
       
    startup.set_config('global', 'server.socket_host', server)



    startup.execute()


if __name__ == '__main__':
    from optparse import OptionParser


    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port", help="Port to run TACTIC server on", default=8081)
    parser.add_option("-s", "--server", dest="server", help="Host name TACTIC server will run under")
    parser.add_option("-o", "--data_dir", dest="data_dir", help="Override location of TACTIC_DATA_DIR")
    parser.add_option("-d", "--python_path", dest="python_path", help="Host name TACTIC server will run under", default="")

    (options, args) = parser.parse_args()

    # add the optional path to the python path
    if options.python_path:
        paths = options.python_path.split("|")
        paths.reverse()
        for path in paths:
            sys.path.insert(0, path)

    if len(args) == 1:
        port = int(args[0])
    else:
        port = int(options.port)

    data_dir = options.data_dir
    if data_dir:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        os.environ["TACTIC_DATA_DIR"] = data_dir

    startup(port, options.server)

