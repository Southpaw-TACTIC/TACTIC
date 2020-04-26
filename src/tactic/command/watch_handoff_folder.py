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


__all__ = ['WatchServerFolderTask', 'WatchFolderTask']

import tacticenv

import time, hashlib, os, shutil

from pyasm.common import Environment, Xml, EncryptUtil, ZipUtil, Config
from pyasm.security import Batch
from pyasm.biz import Project
from pyasm.search import DbContainer
from pyasm.search import Search, Transaction, SearchType, DbContainer
from pyasm.command import Command

from scheduler import SchedulerTask, Scheduler



class WatchServerFolderTask(SchedulerTask):

    #def __init__(self):
    #    super(WatchServerFolderTask, self).__init__()



    def execute(self):
        Batch()

        # get all of the file servers
        search = Search("sthpw/sync_server")
        search.add_filter("state", "online")
        search.add_filter("sync_mode", "file")
        self.servers = search.get_sobjects()

        self.tasks = []
        for server in self.servers:
            base_dir = server.get_value("base_dir")
            if not base_dir:
                continue

            transaction_dir = "%s/transactions" % base_dir

            ticket = server.get_value("ticket")
            task = WatchFolderTask(base_dir=transaction_dir, ticket=ticket)
            self.tasks.append(task)


        # close all the database connections
        DbContainer.close_all()


        count = 0
        while 1:
            #start = time.time()

            for task in self.tasks:
                try:
                    task.execute()
                except Exception as e:
                    print "WARNING: error executing task:"
                    print "Reported Error: ", str(e)


            #print time.time() - start
            # catch a breather?
            time.sleep(2)
            count += 1


    def start(cls):
        
        task = WatchServerFolderTask()

        scheduler = Scheduler.get()
        scheduler.add_single_task(task, 3)
        #scheduler.add_interval_task(task, 1)

        scheduler.start_thread()
        # important to close connection after adding tasks
        DbContainer.close_all()

        return scheduler

    start = classmethod(start)
       




class WatchFolderTask(SchedulerTask):

    def __init__(self, **kwargs):
        self.last_md5 = None
        self.last_dir_set = None

        self.base_dir = kwargs.get("base_dir")

        self.ticket = kwargs.get("ticket")

        super(WatchFolderTask, self).__init__()

        # find out all of the jobs in the queue that are not in the
        # database
        #self.init()

        self.iterations = 0


    def init(self):

        base_dir = self.base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        dirs = os.listdir(base_dir)

        # skip local transactions
        server_code = Config.get_value("install", "server")
        dir_set = set(dirs)
        for dirname in dirs:
            if dirname.startswith("%sTRANSACTION" % server_code):
                dir_set.remove(dirname)
        dirs = list(dir_set)



        tmp_set = set(dirs)
        dirs_set = set()
        dirs_dict = {}

        for dir in tmp_set:
            if dir.startswith("."):
                continue
            if dir.find("TRANSACTION") == -1:
                continue
            if dir.find("-") != -1:
                parts = dir.split("-")
                code = parts[0]
            else:
                code = dir.replace(".zip", "")
                code = code.replace(".enc", "")
            dirs_set.add(code) 
            dirs_dict[code] = dir

        search = Search("sthpw/transaction_log")
        search.add_filters("code", list(dirs_set))
        search.add_column("code")
        transactions = search.get_sobjects()
        codes = [x.get_code() for x in transactions]
        codes_set = set(codes)

        diff = dirs_set.difference(codes_set)
        diff = list(diff)
        diff.sort()

        total = len(diff)-1
        for count, transaction_code in enumerate(diff):

            dirname = dirs_dict.get(transaction_code)

            # FIXME: there is a memory growth problem.  Batch clears it
            if total > 1:
                print "Processing file [%s] (%s of %s): " % (dirname, count+1,total+1)
            if count % 10 == 0:
                Batch()

            path = "%s/%s" % (base_dir, dirname)
            if dirname:
                if dirname.endswith(".zip"):
                    path = "%s.zip" % path
                    dirname = "%s.zip" % dirname

                elif dirname.endswith("%s.zip.enc" % path):
                    path = "%s.zip.enc" % path
                    dirname = "%s.zip.enc" % dirname
            else:
                dirname = transaction_code



            try:
                if not self.verify_dir(path):
                    continue

                # see if this is encrypted
                if dirname.endswith(".zip") or dirname.endswith(".enc"):
                    if not self.ticket:
                        raise Exception("Could not decrypt encrypted transaction due to missing ticket for [%s]" % path)
                    base_dir = os.path.dirname(path)
                    self.handle_encrypted(base_dir, transaction_code, dirname)
                else:
                    print "Running transaction: [%s]" % transaction_code
                    self.handle_transaction(base_dir, transaction_code, transaction_code)
            except Exception as e:
                print "... ERROR: could not process transaction [%s]" % transaction_code
                print str(e)
                print

            interval = 0.1
            time.sleep(interval)


    def execute(self):

        base_dir = self.base_dir
        if not base_dir:
            print "WARNING: No base dir defined."
            return

        # every 10 iterations, compare to the database and rerun
        #if self.iterations % 10 == 0: 
        if self.iterations == 0:
            self.init()
        else:
            self.handle_base_dir(base_dir)
        self.iterations += 1


    def handle_base_dir(self, base_dir):

        #md5 = self.get_folder_md5(base_dir)
        #print md5
        #if self.last_md5 != None and md5 != self.last_md5:
        #    print "There is a change"
        #self.last_md5 = md5

        diff = self.get_new_dirs(base_dir)
        if not diff:
            return

        # FIXME: there is a memory growth issue.  Batch cleans it up.
        Batch()

        for dirname in diff:

            transaction_code = dirname

            # see if this is encrypted
            if dirname.endswith(".enc") or dirname.endswith(".zip"):
                self.handle_encrypted(base_dir, transaction_code, dirname)

            else:
                self.handle_transaction(base_dir, transaction_code, dirname)



    def handle_encrypted(self, base_dir, transaction_code, encrypted):

        key = self.ticket

        from_path = "%s/%s" % (base_dir, encrypted)
        tmp_dir = Environment.get_tmp_dir(include_ticket=True)
        if encrypted.endswith(".enc"):
            to_path = "%s/%s" % (tmp_dir, encrypted)
            to_path = to_path.replace(".enc", "")

            encrypt_util = EncryptUtil(key)
            encrypt_util.decrypt_file(from_path, to_path)


            zip_util = ZipUtil()
            to_dir = os.path.dirname(to_path)
            zip_util.extract(to_path)


        else:
            to_path = from_path
            to_dir = tmp_dir
            zip_util = ZipUtil()
            zip_util.extract(to_path, to_dir)



        dirname = encrypted.replace(".enc", "")
        dirname = dirname.replace(".zip", "")

        print "Running transaction: [%s]" % transaction_code
        self.handle_transaction(to_dir, transaction_code, dirname)



    def handle_transaction(self, base_dir, transaction_code, dirname):

        import time

        start = time.time()


        # check to see if the transaction exists already
        log = Search.get_by_code("sthpw/transaction_log", transaction_code)
        if log:
            print "Transaction [%s] already exists. Skipping ..." % log.get_code()
            return



        transaction_path = "%s/%s/sthpw_transaction_log.spt" % (base_dir, dirname)
        if not os.path.exists(transaction_path):
            # this file has not arrived yet, so ignore
            return


        manifest_path = "%s/%s/manifest.xml" % (base_dir, dirname)
        f = open(manifest_path)
        manifest_xml = f.read()
        f.close()

        transaction_path = "%s/%s/sthpw_transaction_log.spt" % (base_dir, dirname)

        search = Search("sthpw/sync_log")
        search.add_filter("transaction_code", transaction_code)
        sync_log = search.get_sobject()
        #if sync_log:
        #    print "Already processed [%s]" % transaction_code
        #    return

        try:

            from tactic.command import PluginInstaller
            from run_transaction_cmd import RunTransactionCmd


            # import the transaction data
            installer = PluginInstaller(manifest=manifest_xml)

            jobs = installer.import_data(transaction_path, commit=False)
            transaction_log = jobs[0]

            file_base_dir = "%s/%s" % (base_dir, dirname)

            # run the transaction in its own command
            from run_transaction_cmd import RunTransactionCmd
            run_transaction = RunTransactionCmd(transaction_xml=transaction_log, base_dir=file_base_dir)
            Command.execute_cmd(run_transaction)

            status = "complete"

        # May need special handing
        #except MissingItemException as e:
        #    print "WARNING: Could not run transaction [%s]" % transaction_code
        #    print "Error reported: ", str(e)
        #    search = SearchType.create("sthpw/sync_error")



        except Exception as e:
            print "WARNING: Could not run transaction [%s]" % transaction_code
            print "Error reported: ", str(e)
            status = "error"
            error = str(e)
        else:
            error = ""


        # start a sync log
        if status != 'complete':
            if not sync_log:
                sync_log = SearchType.create("sthpw/sync_log")
                sync_log.set_value("transaction_code", transaction_code )
                sync_log.set_user()
                sync_log.set_project()

            sync_log.set_value("status", status)

            if error:
                sync_log.set_value("error", error)

            sync_log.commit()


        # if the status is complete, the delete this entry
        elif sync_log:
            sync_log.delete()






    def get_folder_md5(self, base):
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
                except Exception as e:
                    print e
        md5 = m.hexdigest()
        return md5



    def get_new_dirs(self, base):

        dirs = os.listdir(base)
        dir_set = set(dirs)

        # go through all the dirs and remove any that are from this server
        server_code = Config.get_value("install", "server")
        for dirname in dirs:
            if dirname.startswith("%sTRANSACTION" % server_code):
                dir_set.remove(dirname)
        dirs = list(dir_set)


        if self.last_dir_set != None:
            diff = dir_set.difference(self.last_dir_set)


            for dirname in diff.copy():

                # verify the all the files have arrived
                if not self.verify_dir("%s/%s" % (base, dirname)):
                    diff.remove(dirname)
                    dir_set.remove(dirname)

            if diff:
                print "... found new files: ", diff

            removed_diff = self.last_dir_set.difference(dir_set)


        else:
            diff = set()
            removed_diff = set()

        # use the original list to make sure that dirs aren't handled more
        # once
        self.last_dir_set = set(dirs)

        #print "time: ", time.time() - start
        if removed_diff:
            print "removed files: ", removed_diff

        diff = list(diff)
        diff.sort()

        return diff


    def verify_dir(self, base):

        # ignore transactions that a derived from this server
        server_code = Config.get_value("install", "server")
        if base.startswith("%sTRANSACTION" % server_code):
            return False


        if base.find("TRANSACTION") == -1:
            return False


        if not os.path.isdir(base):
            if base.endswith(".zip.enc"):
                return True
            elif base.endswith(".zip"):
                return True
            else:
                return False


        asset_dir = Environment.get_asset_dir()

        transaction_path = "%s/_transaction.xml" % base
        if not os.path.exists(transaction_path):
            return False

        xml = Xml()
        xml.read_file(transaction_path)

        nodes = xml.get_nodes("transaction/file")

        # verify that all the files are present
        for node in nodes:

            code = xml.get_attribute(node, "code")

            file_sobj = Search.get_by_code("sthpw/file", code)

            src = xml.get_attribute(node, "src")
            rel_path = xml.get_attribute(node, "rel_path")

            src_path = "%s/%s" % (base, rel_path)
            if not os.path.exists(src_path):
                print "[%s] has not arrived" % src_path
                return False


            st_size = xml.get_attribute(node, "size")
            if st_size:
                st_size = int(st_size)
            else:
                st_size = -1
            md5 = xml.get_attribute(node, "md5")

            if st_size != -1:
                # check that the size is the same
                if st_size != os.path.getsize(src_path):
                    print "[%s] size does not match" % src_path
                    return False


        # all the tests have passed
        return True



    def start(cls):
        # This is not normally run

        task = WatchFolderTask()

        #scheduler = Scheduler.get()
        #scheduler.add_interval_task(task, 1)
        #scheduler.start_thread()

        while 1:
            start = time.time()
            task.execute()
            #print time.time() - start
            # catch a breather?
            time.sleep(1)


    start = classmethod(start)



__all__.append("DumpTransactionCodesCmd")
class DumpTransactionCodesCmd(Command):

    def execute(self):
        project = Project.get()

        search = Search("sthpw/transaction_log")
        search.add_filter("namespace", project.get_code() )
        search.add_column("code")

        transactions = search.get_sobjects()
        codes = SObject.get_values(transactions, "code")
        codes = set(codes)

        # dump out the transactions for this project
        f = open("/tmp/transactions_codes", 'wb')
        f.write(str(codes))
        f.close()

       




if __name__ == '__main__':
    Batch()
    DbContainer.close_all()

    WatchServerFolderTask.start()

    while 1:
        try:
            time.sleep(15)
        except (KeyboardInterrupt, SystemExit), e:
            scheduler.stop()
            break


