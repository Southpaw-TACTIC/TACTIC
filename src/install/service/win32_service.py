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

__all__ = ['TacticService']


import os, sys
 
import win32serviceutil 
import win32service 
import win32event 

import tacticenv

from pyasm.common import Environment
from pyasm.web import TacticMonitor


class WinService(object):

    def __init__(self):
        self.monitor = TacticMonitor()

   

    def init(self):
        self.monitor.mode = "init"
        self.monitor.execute()

    def run(self):
        self.monitor.mode = "monitor"
        self.monitor.execute()
    
def write_stop_monitor():
    '''write a stop.monitor file to notify TacticMonitor to exit'''
    log_dir = "%s/log" % Environment.get_tmp_dir()
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
   
    file = open("%s/stop.monitor" % log_dir, "w")
    pid = os.getpid()
    file.write(str(pid))
    file.close()

def stop():
   
    write_stop_monitor()
    
    import time
    time.sleep(3)
    # let monitor.py handle killing of start_up and watch_folder
 
class TacticService(win32serviceutil.ServiceFramework): 
    '''NT Service.'''
     
    _svc_name_ = "TacticService" 
    _svc_display_name_ = "Tactic Application Server" 
 
    def __init__(self, args): 
        win32serviceutil.ServiceFramework.__init__(self, args) 
        # create an event that SvcDoRun can wait on and SvcStop 
        # can set. 
        self.stop_event = win32event.CreateEvent(None, 0, 0, None) 


    def SvcDoRun(self): 

        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        service = WinService()
        service.init()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        service.run()
        # run() needs to run after SERVICE_RUNNING... 
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE) 
     
    def SvcStop(self): 
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) 
        stop()
        win32event.SetEvent(self.stop_event) 



if __name__ == '__main__': 
    win32serviceutil.HandleCommandLine(TacticService) 



