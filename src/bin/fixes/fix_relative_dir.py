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


class FixRelativeDirCmd(Command):

    def execute(self):
        search = Search("sthpw/file")
        search.add_limit(1000)
        search.add_where("relative_dir is NULL")
        search.add_order_by("code")
        files = search.get_sobjects()

        for file in files:

            snapshot_code = file.get_value("snapshot_code")

            snapshot = Snapshot.get_by_code(snapshot_code)
            if not snapshot:
                if WARNING: print "WARNING: Snapshot [%s] not found for file [%s]" % (snapshot_code, file.get_code() )
                continue

            try:
                file_name = file.get_value("file_name")
                if WARNING:
                    lib_dir = snapshot.get_lib_dir()
                    path = "%s/%s" % (lib_dir, file_name)

                    if not os.path.exists(path):
                        print "WARNING: path [%s] does not exist" % path

                file_type = snapshot.get_type_by_file_name(file_name)

                relative_dir = snapshot.get_relative_dir(file_type=file_type)

                cur_relative_dir = file.get_value("relative_dir")
                if cur_relative_dir and cur_relative_dir != relative_dir:
                    if WARNING: print "WARNING: current [%s] and build relative dir [%s] are not equal" % (cur_relative_dir, relative_dir)

                    #answer = raw_input("Fix (y/n): ")
                    #if answer == "n":
                    #    continue
                    #continue


                if cur_relative_dir != relative_dir:
                    file.set_value("relative_dir", relative_dir)
                    file.commit()



            except SObjectNotFoundException, e:
                # Remove some dangling unittest
                if snapshot_code.endswith("UNI"):
                    file.delete()
                    snapshot.delete()
                else:
                    if WARNING:
                        print "WARNING: Error getting directory for snapshot [%s] for file [%s]" % (snapshot_code, file.get_code() )
                        print "\t", e.__str__()

                continue

            except TacticException, e:
                print "WARNING: Problem found on file [%s]" % file.get_code()
                print "\t", e.__str__()
                continue


            except Exception, e:
                print "ERROR: Error found on file [%s]" % file.get_code()
                print "\t", e.__str__()
                if e.__str__() == 'list index out of range':
                    continue
                elif e.__str__() == "'NoneType' object has no attribute 'get_value'":
                    continue
                else:
                    raise


if __name__ == '__main__':
    Batch()
    Project.set_project("admin")

    start = time.time()
    cmd = FixRelativeDirCmd()
    Command.execute_cmd(cmd)

    print float(int( (time.time() - start) * 1000)) / 1000, "seconds"
    


