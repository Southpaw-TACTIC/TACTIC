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

# This fixes any duplicate file codes that may have occured due to file code
# crossover bug

import tacticenv

import os, time

from pyasm.common import Xml
from pyasm.security import Batch
from pyasm.search import Search, DbContainer
from pyasm.command import Command
from pyasm.biz import Project, Snapshot
from pyasm.biz.snapshot import SObjectNotFoundException

BATCH = 50


class FixDuplicateFileCodeCmd(Command):

    def execute(my):
        database = "sthpw" 

        sql = DbContainer.get(database)
        value_array = sql.do_query("select code, cc from (select code, count(code) as cc from file group by code order by cc desc) as X where cc > 1;")
        #value_array = sql.do_query("select code, cc from (select code, count(code) as cc from file group by code order by cc desc) as X;")

        print "found [%s] pairs" % len(value_array)

        for count, value_list in enumerate(value_array):
            if count >= BATCH:
                break

            # get the file object
            file_code = value_list[0]
            search = Search("sthpw/file")
            search.add_filter("code", file_code)
            files = search.get_sobjects()

            #if len(files) == 1:
            #    continue

            for file in files:
                project_code = file.get_value("project_code")
                if not project_code:
                    print "WARNING: file [%s] has no project_code" % file_code
                    continue

                project = Project.get_by_code(project_code)
                initials = project.get_initials()

                id = file.get_id()
                new_file_code = "%s%s" % (id, initials)
                if file_code == new_file_code:
                    continue

                print "-"*20
                print "switching: ", file_code, "to", new_file_code


                snapshot_code = file.get_value("snapshot_code")
                snapshot = Snapshot.get_by_code(snapshot_code)
                assert snapshot

                snapshot_xml = snapshot.get_xml_value("snapshot")
                print snapshot_xml.to_string()
                node = snapshot_xml.get_node("snapshot/file[@file_code='%s']" % file_code)
                Xml.set_attribute(node, "file_code", new_file_code)
                print snapshot_xml.to_string()

                assert node


                # set the file_code
                file.set_value("code", new_file_code)
                file.commit()

                # set the snapshot
                snapshot.set_value("snapshot", snapshot_xml.to_string() )
                snapshot.commit()




if __name__ == '__main__':
    Batch()
    Project.set_project("admin")

    start = time.time()
    cmd = FixDuplicateFileCodeCmd()
    Command.execute_cmd(cmd)



