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

import time
import tacticenv
from tactic_client_lib import TacticServerStub

#from pyasm.security import Batch




def execute():
    #try:
    #    server = TacticServerStub(project='admin')
    #except:
    #    # TODO: this should be automatic
    #    server = TacticServerStub(project='admin', setup=False)
    #    server.get_info_from_user()
    #    server = TacticServerStub(project='admin')
    server = TacticServerStub(project='admin')

    iterations = 100

    print "Testing [%s] requests ..." % iterations
    print

    total_time = 0
    count = 0

    ports = {}
    threads = {}
    databases = {}
    for i in range(0, iterations):
        start = time.time()
        x = server.get_connection_info()
        diff = time.time() - start
        try:
            ports[x['port']] += 1
        except:
            ports[x['port']] = 1
        try:
            threads[x['thread']] += 1
        except:
            threads[x['thread']] = 1

        num_databases = x['num_database_connections']
        databases[x['port']] = num_databases
 

        total_time += diff
        count += 1
        #print "time: ", time.time() - start

    average_time = total_time / count
    print "average time: ", average_time
    print

    print "ports: %s found" % len(ports.keys())
    for key in ports.keys():
        print "\t%s: %s requests" % (key, ports[key])

    print
    print "threads: %s found" % len(threads.keys())
    for key in threads.keys():
        print "\tid=%s: %s requests" % (key, threads[key])

    # FIXME: not completely correct yet
    #print
    #print "databases: %s found" % len(databases.keys())
    #for key in databases.keys():
    #    print "\tport=%s: %s databases" % (key, databases[key])


    print

def main():
    execute()
    return
    import os
    import profile, pstats
    if os.name == 'nt':
        path = "C:/sthpw/profile"
    else:
        path = "/home/apache/tacticTemp/profile"
    profile.run( "execute()", path)
    p = pstats.Stats(path)
    p.sort_stats('cumulative').print_stats(30)
    print "*"*30
    p.sort_stats('time').print_stats(30)




if __name__ == '__main__':
    #Batch(project_code="admin")
    main()
