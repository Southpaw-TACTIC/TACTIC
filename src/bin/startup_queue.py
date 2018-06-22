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

from pyasm.common import Common, Environment
from tactic.command import JobTask

import time
import sys
import os

def main(options, site=None):
    #print "Starting Job Queue ..."
    from pyasm.security import Batch
    Batch(site=site)

    idx = 0
    if 'index' in options:
        idx = options['index']
        options.pop('index')
    write_pid(idx)

    log_dir = "%s/log" % Environment.get_tmp_dir()
    pid_path = "%s/startup_queue.%s" % (log_dir, idx)


    JobTask.start(
            check_interval=0.1,
            max_jobs_completed=50,
            pid_path=pid_path,
    )

    try:
        while 1:
            try:
                time.sleep(1)
            except (KeyboardInterrupt, SystemExit), e:
                #print "Exiting ..."
                raise

    finally:

        if os.path.exists(pid_path):
            os.unlink(pid_path)



def write_pid(idx):
    log_dir = "%s/log" % Environment.get_tmp_dir()
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    try:
        file = open("%s/startup_queue.%s" % (log_dir, idx), "w")
        pid = os.getpid()
        file.write(str(pid))
        file.close()
    except IOError, e:
        if e.errno == 13:
            print
            print "Permission error opening the file [%s/startup_queue.%s]." % (log_dir, idx)
            print
            if os.name == 'nt':
                print "You may need to run this shell as the Administrator."
            else:
                print "The file should be owned by the same user that runs this startup_queue.py process."

            sys.exit(2)

    if os.name != 'nt' and os.getuid() == 0:
        print 
        print "You should not run this as root. Run it as the Web server process's user. e.g. tactic or apache"
        print
        sys.exit(0)


if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-q", "--queue", dest="queue", help="List of queues for this process", default=None)
    parser.add_option("-i", "--index", dest="index", help="index of this job queue", default=0)
    parser.add_option("-s", "--site", dest="site", help="Site to grab queue from")
    
 
    (options, args) = parser.parse_args()
    if not options:
        options = {}
    else:
        options = vars(options)

    if len(args) == 1:
        site = args[0]
    else:
        site = options['site']

    main(options, site=site)



