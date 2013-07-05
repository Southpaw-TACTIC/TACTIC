#!/usr/bin/env python
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

# Load balancer: for API calls, redirects are stored by ticket
# This script must match the TACTIC servers that are actually running.

import sys, os, time

# Comment out these to override
SERVER_NAME = "localhost"
NUM_SERVERS = 1
START_PORT = 8081


import tacticenv
from pyasm.common import Config

def main():

    cleanup_chunk = 100     # cleanup every 100 requests
    cleanup_intervaL = 60   # cleanup any transaction that is over 60 seconds

    # look in config file
    server_name = Config.get_value("server", "server_name")
    if not server_name:
        server_name = SERVER_NAME

    num_servers = Config.get_value("server", "num_servers")
    if not num_servers:
        num_servers = NUM_SERVERS
    else:
        num_servers = int(num_servers)

    start_port = Config.get_value("server", "start_port")
    if not start_port:
        start_port = START_PORT
    else:
        start_port = int(start_port)


    servers = []
    for i in range(0, num_servers):
        server = "%s:%s" % (server_name, start_port + i)
        servers.append(server)

    ticket_redirects = {}
    ticket_timestamps = {}

    count = 0
    cleanup_count = 0

    while 1:

        data = sys.stdin.readline().strip()

        #f = open("/tmp/sthpw/load_balance.log", 'a')
        #f.write("-------------------\n")
        #f.write("data: "+data+"\n")
        #f.write("count: "+str(count)+"\n")


        # branch logic for api
        if data.startswith("default/Api/"):
            # get ticket
            parts = data.split("/")
            ticket = parts[-1]
            if ticket:
                ticket_redirect = ticket_redirects.get(ticket)

                if ticket_redirect:
                    server = ticket_redirect
                else:
                    # use a round robin
                    server = servers[count]
                    count = (count+1) % num_servers

                    ticket_redirects[ticket] = server
                    ticket_timestamps[ticket] = time.time()

            else:
                # use round robin delegation
                server = servers[count]
                count = (count+1) % num_servers

            url = "http://%s/tactic/default/Api/" % server

            # clean up
            #print ticket_redirects.values()
            '''
            cleanup_count = (cleanup_count+1) % cleanup_chunk
            if cleanup_count == cleanup_chunk-1:
                now = time.time()
                for ticket, start in ticket_timestamps.items():
                    #print ticket, now - start
                    if now - start > cleanup_interval:
                        del(ticket_redirects[ticket])
                        del(ticket_timestamps[ticket])
            '''
                    


        else:
            # use round robin delegation
            server = servers[count]
            count = (count+1) % num_servers
            data = data.lstrip("/")
            url = "http://%s/tactic/%s" % (server, data)

        #f.write(url + "\n")
        #f.close()

        sys.stdout.write( url + "\n" )
        sys.stdout.flush()




        #data = sys.stdin.readline().strip()
        #count = (count+1) % num_servers
        #sys.stdout.write( servers[count] + "\n" )
        #sys.stdout.flush()



if __name__ == '__main__':
    main()
