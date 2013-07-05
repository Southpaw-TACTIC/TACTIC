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

# Repurposed from http://docs.cherrypy.org/cherrypy22-as-windows-service

'''
The most basic (working) CherryPy 2.2 Windows service possible.
Requires Mark Hammond's pywin32 package.
'''
 
import cherrypy 
import win32serviceutil 
import win32service 
import win32event 

from queue import Queue
from queue_index import QueueIndex


 
class TacticQueueService(win32serviceutil.ServiceFramework): 
    """NT Service."""
     
    _svc_name_ = "TacticQueueService" 
    _svc_display_name_ = "Tactic Queue Service" 
 
    def __init__(self, args): 
        win32serviceutil.ServiceFramework.__init__(self, args) 
        # create an event that SvcDoRun can wait on and SvcStop 
        # can set. 
        self.stop_event = win32event.CreateEvent(None, 0, 0, None) 
 
    def SvcDoRun(self): 

        # start the queue in a separate thread
        queue = Queue()
        queue.start()

        cherrypy.tree.mount(QueueIndex(), '/')
        
        # in practice, you will want to specify a value for
        # server.log_file below or in your config file.  If you
        # use a config file, be sure to use an absolute path to
        # it, as you can't be assured what path your service 
        # will run in. 
        cherrypy.config.update({ 
            'global':{ 
                'autoreload.on': False, 
                'server.log_to_screen': False, 
            } 
        }) 
        # set init_only=True so that start() does not block 
        cherrypy.server.start(init_only=True) 
        # now, block until our event is set... 
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE) 
     
    def SvcStop(self): 
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) 
        cherrypy.server.stop() 
        win32event.SetEvent(self.stop_event) 



if __name__ == '__main__': 
    win32serviceutil.HandleCommandLine(MyService) 



