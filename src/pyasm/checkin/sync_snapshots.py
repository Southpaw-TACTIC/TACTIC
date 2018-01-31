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
import tacticenv

__all__ = ["BaseRepo", "TacticRepo"]

import os, sys, md5, re

from pyasm.command import Command
from pyasm.search import Search
from pyasm.security import Batch

class SnapshotSync(Command):

    def execute(self):

        # get all of the snapshots taht are not in sync
        messages = []

        search = Search("sthpw/snapshot")
        search.add_filter('is_synced', False)
        search.add_order_by('timestamp')
        snapshots = search.get_sobjects()
        for snapshot in snapshots:
            missing = False
            for path in snapshot.get_all_lib_paths():
                if not os.path.exists(path):
                    missing = True
                    msg = "Snapshot [%s] - Path [%s] not found" % (snapshot.get_code(), path)
                    messages.append(msg)
                    
            if not missing:
                snapshot.set_value("is_synced", True)
                snapshot.set_latest(commit=False)
                snapshot.commit()


        print messages

if __name__ == '__main__':
    Batch(project_code='admin')
    sync = SnapshotSync()
    Command.execute_cmd(sync)




