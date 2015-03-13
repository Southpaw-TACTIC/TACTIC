###########################################################
#
# Copyright (c) 2014, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


import tacticenv

from tactic.command import TransactionQueueManager, WatchServerFolderTask

import time, sys, getopt

def main(site=None):
    from pyasm.security import Batch
    Batch(site=site)


    # start up the sync system ...
    print "Starting Transaction Sync Service ..."
    from tactic.command import TransactionQueueManager
    TransactionQueueManager.start()

    # start up the sync system ...
    print "Starting Watch Folder Service ..."
    from tactic.command import WatchServerFolderTask
    WatchServerFolderTask.start()


    while 1:
        try:
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit), e:
            print "Exiting ..."
            raise






if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:", ["site"])
    except getopt.error, msg:
        print msg
        sys.exit(2)
    # process options
    site = None
    for o, a in opts:
	if o in ("-s", "--site"):
            site = a
 
    main(site)

