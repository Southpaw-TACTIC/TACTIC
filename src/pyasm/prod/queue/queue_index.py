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

from pyasm.security import Batch
from pyasm.search import Search
from pyasm.web import WebContainer
from pyasm.widget import TableWdg

import cherrypy

class QueueIndex:
    @cherrypy.expose()
    def index(self):
        Batch()
        # clear the buffer
        #WebContainer.clear_buffer()
        #search = Search("sthpw/queue")
        #table = TableWdg("sthpw/queue")
        #table.set_search(search)
        #return table.get_buffer_display()

	return "Tactic Queue Slave"




