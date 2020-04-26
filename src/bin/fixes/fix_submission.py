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

# This script puts all the submissions under a new directory related to the
# bin it belongs to

import os

import tacticenv

from pyasm.security import Batch
from pyasm.command import Command
from pyasm.search import Search, FileUndo
from pyasm.biz import Project, Snapshot
from pyasm.prod.biz import Submission


class MoveSubmissionCmd(Command):
    def get_title(self):
        return "Move Submission"

    def execute(self):

        search = Search(Submission)
        search.set_show_retired(True)
        submissions = search.get_sobjects()

        for submission in submissions:
            snapshot = Snapshot.get_latest_by_sobject(submission, "publish")
            paths = snapshot.get_all_lib_paths()

            bins = submission.get_bins()
            if not bins:
                 print "Bin for submissin [%s] does not exist" % submission.get_id()
                 continue
            bin = bins[0]
            code = bin.get_code()
            type = bin.get_value("type")
            label = bin.get_value("label")

            for path in paths:
                if not os.path.exists(path):
                    print "WARNING: path '%s' does not exist" % path
                    continue

                dirname = os.path.dirname(path)
                basename = os.path.basename(path)
                
                new_dirname = "%s/%s/%s/%s" % (dirname,type,label,code)
                if not os.path.exists(new_dirname):
                    os.makedirs(new_dirname)

                new_path = "%s/%s" % (new_dirname, basename)

                print new_path
                FileUndo.move(path, new_path)


                


if __name__ == '__main__':

    Batch(login_code="admin")
    Project.set_project("bar")

    cmd = MoveSubmissionCmd()
    Command.execute_cmd(cmd)

