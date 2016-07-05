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

    def __init__(my):
        my.monitor = TacticMonitor()

   

    def init(my):
        my.monitor.mode = "init"
        my.monitor.execute()

    def run(my):
        my.monitor.mode = "monitor"
        my.monitor.execute()
    
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
    #startup.stop() 
    log_dir = "%s/log" % Environment.get_tmp_dir()
    files = os.listdir(log_dir)
    ports = []
    watch_folders = []
    write_stop_monitor()
    
    import time
    time.sleep(5)

    for filename in files:
        base, ext = os.path.splitext(filename)
        if base == 'pid':
            ports.append(ext[1:])
        elif base == 'watch_folder':
            watch_folders.append(ext[1:])
    
    for port in ports:
        try:
            file_name = "%s/pid.%s" % (log_dir,port)
            file = open(file_name, "r")
            pid = file.readline().strip()
            os.system('taskkill /F /PID %s'%pid)
            file.close()
        except IOError, e:
            print "Error opening file [%s]" %file_name
            continue

    # kill watch folder processes
    for watch_folder in watch_folders:
        try:
            filename = "%s/watch_folder.%s" % (log_dir, watch_folder)
            f = open(filename, "r")
            pid = f.readline()
            f.close()
            os.system('taskkill /F /PID %s' % pid)
        except IOError, e:
            print "Error handling processes for watch folder [%s]." % watch_folder

 
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
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE) 
        service.run()
        # monitor() needs to run after... 
     
    def SvcStop(self): 
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) 
        stop()
        win32event.SetEvent(self.stop_event) 



if __name__ == '__main__': 
    win32serviceutil.HandleCommandLine(TacticService) 



