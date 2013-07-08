############################################################
#
#    Copyright (c) 2005, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#


# scripts that starts up a number of Tactic and monitors them
import sys, os
import tacticenv
from pyasm.web import TacticMonitor

# set it so that the temp directories are cleaned up
os.environ['TACTIC_CLEANUP'] = "true"

if __name__ == '__main__':
    args = sys.argv[1:]
    num_processes = None
    if len(args) == 1:
        num_processes = int(args[0])

    monitor = TacticMonitor(num_processes)
    
    #monitor.set_check_interval(0)
    monitor.execute()


