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

from pyasm.common import Xml, Config, Environment
from pyasm.search import Search, FileUndo
from pyasm.security import Batch
from pyasm.biz import Snapshot, Project
from pyasm.command import Command


import os, shutil, sys


class NamingMigratorCmd(Command):

    def execute(my):

        mode = my.kwargs.get("mode")
        # modes are either naming based or file object based
        #mode = "naming"
        #mode = "file"
        assert mode in ['naming', 'file']

        search_type = my.kwargs.get("search_type")
        search_keys = my.kwargs.get("search_keys")
        assert search_type or search_keys

        if search_type:
            print "@SOBJECT(%s)" % search_type
            sobjects = Search.eval("@SOBJECT(%s)" % search_type)
        else:
            sobjects = Search.get_by_search_keys(search_keys)

        if not sobjects:
            print "No sobjects to process"
            return
        snapshots = Search.eval("@SOBJECT(sthpw/snapshot)", sobjects)

        # set an arbitrary limit for now
        limit = 1000

        base_dir = Environment.get_asset_dir()

        num_found = 0
        errors = []
        for i, snapshot in enumerate(snapshots):
            if i > limit:
                break
            print "Processing: %s of %s" % (i, len(snapshots) )

            file_types = snapshot.get_all_file_types()
            for file_type in file_types:
                files = snapshot.get_files_by_type(file_type)

                # FIXME: not sure why we have this limitation, although it is
                # a pretty rare occurance
                if len(files) > 1:
                    raise Exception("More than one file with type [%s] in snapshot [%s]" % (file_type, snapshot.get_code()) )

                file = files[0]
                file_name = file.get_value("file_name")


                # check-in dir is not subject to changes in asset_dir
                checkin_dir = file.get_value("checkin_dir")
                old_path = "%s/%s" % ( checkin_dir, file_name )


                try:

                    if mode == "naming":
                        # preallocated path is used to align a file to the
                        # current naming convention

                        # FIXME:
                        # there is a behavior in naming to add "_web" and
                        # "_icon" on the file name.  In this case, we don't
                        # want that, so ask for main
                        if file_type in ['icon', 'web']:
                            path = snapshot.get_preallocated_path('main', file_name)
                        else:
                            path = snapshot.get_preallocated_path(file_type, file_name)

                    elif mode == "file":
                        # relative_dir is used to align a file to the current
                        # place pointed to by the "file" object
                        relative_dir = file.get_value("relative_dir")
                        path = "%s/%s/%s" % ( base_dir, relative_dir, file_name )
                    else:
                        raise Exception("Invalid mode [%s]" % mode)

                except Exception, e:
                    error = "Snapshot [%s] has an error getting preallocated path: [%s]" % (snapshot.get_code(), e.message )
                    errors.append(error)
                    continue



                if old_path == path:
                    continue

                num_found += 1

                print "snapshot: ", snapshot.get_value("code")
                print "old: ", old_path
                print "new: ", path


                if not os.path.exists(old_path):
                    print '... old does not exist'
                    continue
                    

                print "-"*20


                new_dir = os.path.dirname(path)
                new_filename = os.path.basename(path)
                new_relative_dir = new_dir.replace(base_dir, '')
                new_relative_dir = new_relative_dir.strip("/")

                xml = snapshot.get_xml_value("snapshot")
                node = xml.get_node("snapshot/file[@type='%s']" % file_type)
                Xml.set_attribute(node, "name", new_filename)



                # update all of the file
                file.set_value("file_name", new_filename)
                file.set_value("checkin_dir", new_dir)
                file.set_value("relative_dir", new_relative_dir)
                snapshot.set_value("snapshot", xml.to_string() )

                dirname = os.path.dirname(path)
                if not os.path.exists(dirname):
                    FileUndo.mkdir(dirname)

                FileUndo.move(old_path, path)
                file.commit()
                snapshot.commit()


                # try to remove the old folder (if it's empty, it will be removed)
                dirname = os.path.dirname(old_path)
                while 1:
                    try:
                        os.rmdir(dirname)
                        dirname = os.path.dirname(dirname)
                    except:
                        break

        if errors:
            print "Errors:"
            for error in errors:
                print error
            print "-"*20
        print "Found %s of %s snapshots which have paths different from naming" % (num_found, len(snapshots) )




if __name__ == '__main__':

    args = sys.argv[1:]
    project_code = args[0]
    search_type = args[1]

    Batch(project_code=project_code)
    cmd = NamingMigratorCmd(search_type=search_type, mode="naming")
    Command.execute_cmd(cmd)


