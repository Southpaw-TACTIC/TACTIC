############################################################
#
#    Copyright (c) 2010, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#


__all__ = ['NamingMigratorCmd']

import tacticenv

from pyasm.common import Xml, Config
from pyasm.search import Search, FileUndo
from pyasm.security import Batch
from pyasm.biz import Snapshot, Project
from pyasm.command import Command


import os, shutil


class NamingMigratorCmd(Command):

    def execute(my):
        search_type = my.kwargs.get("search_type")
        assert search_type

        sobjects = Search.eval("@SOBJECT(%s)" % search_type)
        print "@SOBJECT(%s)" % search_type
        if not sobjects:
            print "No sobjects to process"
            return
        print "sobjects: ", len(sobjects)
        snapshots = Search.eval("@SOBJECT(sthpw/snapshot)", sobjects)

        limit = 100


        base_dir = Config.get_value("checkin", "asset_base_dir")
        #base_dir = "/home/apache/assets/"

        num_found = 0
        errors = []
        for i, snapshot in enumerate(snapshots):
            if i > limit:
                break
            print "Processing: %s of %s" % (i, len(snapshots) )

            file_types = snapshot.get_all_file_types()
            for file_type in file_types:
                files = snapshot.get_files_by_type(file_type)

                if len(files) > 1:
                    ffsadfsd

                file = files[0]

                file_name = file.get_value("file_name")
                checkin_dir = file.get_value("checkin_dir")

                old_path = "%s/%s" % ( checkin_dir, file_name )

                try:
                    path = snapshot.get_preallocated_path(file_type, file_name)
                except Exception, e:
                    error = "Snapshot [%s] has an error getting preallocated path: [%s]" % (snapshot.get_code(), e.message )
                    errors.append(error)
                    continue


                if old_path == path:
                    continue

                num_found += 1

                print "old: ", old_path
                print "new: ", path


                if not os.path.exists(old_path):
                    print '... old does not exist'
                    

                print "-"*20


                new_dir = os.path.dirname(path)
                new_filename = os.path.basename(path)
                new_relative_dir = new_dir.replace(base_dir, '')

                xml = snapshot.get_xml_value("snapshot")
                node = xml.get_node("snapshot/file[@type='%s']" % file_type)
                Xml.set_attribute(node, "name", new_filename)



                # update all of the file
                file.set_value("file_name", new_filename)
                file.set_value("checkin_dir", new_dir)
                file.set_value("relative_dir", new_relative_dir)
                snapshot.set_value("snapshot", xml.to_string() )

                FileUndo.move(old_path, path)
                file.commit()
                snapshot.commit()

        if errors:
            print "Errors:"
            for error in errors:
                print error
            print "-"*20
        print "Found %s of %s snapshots which have paths different from naming" % (num_found, len(snapshots) )




if __name__ == '__main__':

    Batch(project_code='pg')
    cmd = NamingMigratorCmd(search_type='pg/photos')
    Command.execute_cmd(cmd)
