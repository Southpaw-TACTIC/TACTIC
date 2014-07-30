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

from pyasm.common import Common
from tactic.command import JobTask

import time

def main(options):
    #print "Starting Job Queue ..."
    from pyasm.security import Batch
    Batch()

    if not options.has_key("check_interval"):
        options['check_interval'] = 0.2
    if not options.has_key("max_jobs_completed"):
        options['max_jobs_completed'] = 50

    JobTask.start(
            **options
    )
    while 1:
        try:
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit), e:
            print "Exiting ..."
            raise



if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-q", "--queue", dest="queue", help="List of queues for this process", default=None)
 
    (options, args) = parser.parse_args()

    if not options:
        options = {}
    else:
        options = vars(options)

    main(options)



