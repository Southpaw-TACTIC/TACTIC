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

import cherrypy

from queue import Queue
from queue_index import QueueIndex


# create a web service


if __name__ == '__main__':

    # start the queue in a separate thread
    queue = Queue()
    queue.start()

    # start a cherrypy web service
    cherrypy.root = QueueIndex()
    cherrypy.config.update( {
        'global': { 'server.socketPort': 8082, 'server.environment': 'production' }
    } )
    cherrypy.server.start()




