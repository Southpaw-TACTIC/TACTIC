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

def main():
    print "Running Job Queue ..."
    from pyasm.security import Batch
    Batch()

    JobTask.start(
            check_interval=0.1,
            max_jobs_completed=50
    )
    count = 0
    while 1:
        time.sleep(1)



if __name__ == '__main__':

    main()

