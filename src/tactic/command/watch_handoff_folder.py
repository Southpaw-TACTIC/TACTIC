############################################################
#
#    Copyright (c) 2012, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

import tacticenv

import time, hashlib, os, shutil

from pyasm.common import Environment, Xml
from pyasm.search import Search

from scheduler import SchedulerTask, Scheduler

class WatchHandoffFolderTask(SchedulerTask):

    def __init__(my):
        my.last_md5 = None
        my.last_dir_set = None
        my.handoff_dir = Environment.get().get_server_handoff_dir(include_ticket=False)
        my.handoff_dir = "/home/apache/Dropbox/assets/handoff"
        print "handoff: ", my.handoff_dir

        super(WatchHandoffFolderTask, my).__init__()

    def execute(my):

        #md5 = my.get_folder_md5(my.handoff_dir)
        #print md5
        #if my.last_md5 != None and md5 != my.last_md5:
        #    print "There is a change"
        #my.last_md5 = md5

        diff = my.get_new_dirs(my.handoff_dir)
        if not diff:
            return

        for dirname in diff:


            transaction_path = "%s/%s/.transaction.xml" % (my.handoff_dir, dirname)
            if not os.path.exists(transaction_path):
                # this file has not arrived yet, so ignore
                pass

            # find the corresponding checkins for this path
            ticket = dirname
            f = open(transaction_path)
            xml_string = f.read()
            f.close()


            xml = Xml()
            xml.read_string(xml_string)


            snapshot_node = xml.get_node("transaction/snapshot")
            code = xml.get_attribute(snapshot_node, "code")

            # made the sync
            nodes = xml.get_nodes("transaction/file")
            search = Search("sthpw/snapshot")
            search.add_filter("code", code)
            snapshot = search.get_sobject()

            snapshot.set_value("is_sync", True)
            #snapshot.commit()


            nodes = xml.get_nodes("transaction/file")
            for node in nodes:
                src = xml.get_attribute(node, "src")
                src = "%s/%s/%s" % (my.handoff_dir, ticket, src)

                #dst = xml.get_attribute(node, "dst")
                #if not dst.startswith("/") and dst[2] != ":":
                #    asset_dir = Environment.get_asset_dir()
                #    dst = "%s/%s" % (asset_dir, dst)

                # get the dst path from file_sobj
                file_code = xml.get_attribute(node, "code")
                file_sobj = Search.get_by_code("sthpw/file", file_code)
                dst = file_sobj.get_lib_path()

                print "src: ", src
                print "dst: ", dst
                #shutil.copy(src, dst)






    def get_folder_md5(my, base):
        m = hashlib.md5()
        for root, dirs, files in os.walk(base):
            #print root
            #if dirs:
            #    print dirs
            for filename in files:
                path = "%s/%s" % (root, filename)
                try:
                    stat = os.stat(path)
                    m.update(path)
                    m.update(str(stat))
                except Exception, e:
                    print e
        md5 = m.hexdigest()
        return md5



    def get_new_dirs(my, base):
        dirs = os.listdir(base)

        # really just looking for a new directory in the handoff directory
        dir_set = set()
        for dirname in dirs:
            dir_set.add(dirname)

        if my.last_dir_set != None:
            diff = dir_set.difference(my.last_dir_set)

            for dirname in diff.copy():
                # verify the all has arrived
                if not my.verify_dir("%s/%s" % (base, dirname)):
                    print "removing: ", dirname
                    diff.remove(dirname)
                    dir_set.remove(dirname)


        else:
            diff = set()

        my.last_dir_set = dir_set 

        return diff


    def verify_dir(my, base):

        transaction_path = "%s/.transaction.xml" % base
        if not os.path.exists(transaction_path):
            print "Transaction path has not arrived"
            return False

        xml = Xml()
        xml.read_file(transaction_path)

        nodes = xml.get_nodes("transaction/file")

        # verify that all the files are present
        for node in nodes:

            code = xml.get_attribute(node, "code")

            file_sobj = Search.get_by_code("sthpw/file", code)

            src = xml.get_attribute(node, "src")
            src_path = "%s/%s" % (base, src)
            if not os.path.exists(src_path):
                print "[%s] has not arrived" % src
                return False


            st_size = xml.get_attribute(node, "size")
            if st_size:
                st_size = int(st_size)
            else:
                st_size = -1
            print "st_size: ", st_size
            md5 = xml.get_attribute(node, "md5")
            print "md5: ", md5

            # check that the size is the same
            if st_size != os.path.getsize(src_path):
                print "[%s] size does not match" % src_path
                return False

        # all the tests have passed
        return True



if __name__ == '__main__':
    from pyasm.security import Batch
    Batch()

    scheduler = Scheduler.get()

    task = WatchHandoffFolderTask()
    scheduler.add_interval_task(task, 1)

    scheduler.start_thread()

    import time
    while 1:
        try:
            time.sleep(15)
        except (KeyboardInterrupt, SystemExit), e:
            scheduler.stop()
            break


