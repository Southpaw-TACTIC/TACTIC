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

# This script goes through all the entries in the file table and fixes/sets the
# relative_dir column in the file table.  As of version 2.1.0.b02, TACTIC uses
# relative_dir to build the file path on all reads.  On checkins, it will
# still use the naming convention.

import tacticenv

import os, time

from pyasm.common import TacticException
from pyasm.security import Batch
from pyasm.search import Search
from pyasm.command import Command
from pyasm.biz import Project, Snapshot
from pyasm.biz.snapshot import SObjectNotFoundException

WARNING = False


class FixIsLatestSnapshotCmd(Command):

    def execute(self):
        count = 0
        change_count = 0
        from pyasm.search import Search, SearchException
        search = Search("sthpw/snapshot")
        search.add_order_by("search_type")
        search.add_order_by("search_id")
        search.add_order_by("context")
        search.add_order_by("version desc")
        snapshots = search.get_sobjects()
        print "found [%s] snapshots" % len(snapshots)

        current_search_type = None
        current_search_id = None
        current_context = None
        current_version = None
        for i, snapshot in enumerate(snapshots):
            search_type = snapshot.get_value("search_type")
            search_id = snapshot.get_value("search_id")
            context = snapshot.get_value("context")
            version = snapshot.get_value("version")

            #print i, search_type, search_id, context, version

            if not (search_type == current_search_type and \
                    search_id == current_search_id and \
                    context == current_context):
                count += 1
                if snapshot.get_value('is_latest') != True:
                    change_count += 1
                    try:
                        snapshot.set_latest()
                        print "\t... set to is latest! ", search_type, search_id, context, version
                    except Exception, e:
                        print "\t ... WARNING: could not set latest:: ", search_type, search_id, context, version
                        print "\t ... ", e

            current_search_type = search_type
            current_search_id = search_id
            current_context = context
            current_version = version   

        print "Total is_latest: ", count
        print "Total is_latest set: ", change_count
if __name__ == '__main__':
    Batch()
    Project.set_project("admin")

    start = time.time()
    cmd = FixIsLatestSnapshotCmd()
    Command.execute_cmd(cmd, call_trigger=False)

    print float(int( (time.time() - start) * 1000)) / 1000, "seconds"
    


