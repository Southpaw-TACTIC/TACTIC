############################################################
#
#    Copyright (c) 2011, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

__all__ = ['RunTransactionCmd', 'TransactionFilesCmd', 'TransactionQueueManager', 'TransactionQueueCmd', 'TransactionQueueServersTrigger']


import tacticenv

from pyasm.common import Environment, Xml, TacticException, Config, Container
from pyasm.biz import Project
from pyasm.command import Command, Trigger
from pyasm.search import SearchType, Search, SObject, DbContainer

from scheduler import Scheduler

import os, codecs, sys, shutil
from dateutil import parser


class TransactionQueueAppendCmd(Trigger):

    def execute(my):
        input = my.get_input()


        search_type = input.get('search_type')
        if search_type != 'sthpw/transaction_log':
            print "ERROR: this trigger can only be executed for transaction_logs"
            return

        
        project = Project.get()

        # Block admin project from syncing
        # NOTE: maybe need an option to enable this?
        if project.get_code() == 'admin':
            return


        log = input.get('sobject')
        transaction_code = log.get_value("code")

        # if this is a remote transaction, then do not create a job for it
        local_prefix = Config.get_value("install", "server")


        search = Search("sthpw/sync_server")
        search.add_filter("state", "online")
        servers = search.get_sobjects()
        #print "servers: ", len(servers)




        # These are usually determined by the server entry
        #sync_mode = input.get('mode')
        #if not sync_mode or sync_mode == 'default':
        #    sync_mode = 'xmlrpc'
        ## This will transaction into a "file" folder
        #sync_mode = "file"

        #file_mode = 'delayed'
        #file_mode = 'upload'


        # get some user info
        env = Environment.get()
        #user = env.get_user_name()
        #ticket = env.get_ticket()

        project_code = Project.get_project_code()

        from pyasm.security import AccessManager
        access_manager = AccessManager()


        for server in servers:

            # check security
            #if not my.check_security(server):
            #    print "Transaction denied due to security restrictions"
            #    continue

            server_code = server.get_code()

            # don't publish a transaction back to the original server
            if log.get_value("server_code") == server_code:
                continue

            # check project security
            rules = server.get_value("access_rules");
            if not rules:
                rules = "<rules/>"
            access_manager.add_xml_rules(rules)

            # filter based on project code
            namespace = log.get_value("namespace")
            key1 = { 'code': namespace }
            key2 = { 'code': '*' }
            keys = [key1, key2]
            if not access_manager.check_access("project", keys, "allow", default="deny"):
                continue


            # filter based on transaction key
            """
            keywords = log.get_value("kewords", no_exception=True)
            key1 = { 'keywords': keywords }
            key2 = { 'keywords': '*' }
            keys = [key1, key2]
            if not access_manager.check_access("transaction", keys, "allow", default="deny"):
                continue
            """


            # filter out any specific rules from transaction itself
            from tactic.ui.sync import SyncFilter
            sync_filter = SyncFilter(rules=rules, transaction=log)
            sync_filter.execute()

            filtered_xml = sync_filter.get_filtered_xml()
            message = sync_filter.get_message()


            # create a new job entry
            job = SearchType.create("sthpw/sync_job")
            job.set_value("state", "pending")
            job.set_value("server_code", server_code)
            job.set_value("transaction_code", transaction_code)
            job.set_user()

            host = server.get_value("host")


            job.set_value("command", "tactic.command.TransactionQueueCmd")
            kwargs = {
                'server': server.get_value("code"),
                'transaction_code': transaction_code,
                'project_code': project_code,
                #'file_mode': file_mode,
                #'sync_mode': sync_mode
            }
            job.set_json_value("data", kwargs)
            job.commit()


    def check_security(my, server):

        # security for this server
        current_project_code = Project.get_project_code()

        # admin project sync is not support?
        if current_project_code == 'admin':
            return False

        project_code = server.get_value("project_code", no_exception=True)
        if project_code:
            if project_code != current_project_code:
                return False

        return True


# create a task from the job
from queue import JobTask
class TransactionQueueManager(JobTask):

    def __init__(my, **kwargs):
        super(TransactionQueueManager, my).__init__(**kwargs)

        trigger = TransactionQueueServersTrigger()
        trigger.execute()
        my.servers = Container.get("TransactionQueueServers")

        # add a static trigger
        event = "change|sthpw/sync_server"
        trigger = SearchType.create("sthpw/trigger")
        trigger.set_value("event", event)
        trigger.set_value("class_name", "tactic.command.TransactionQueueServersTrigger")
        trigger.set_value("mode", "same process,same transaction")
        Trigger.append_static_trigger(trigger, startup=True)




    def set_check_interval(my, interval):
        my.check_interval = interval

    def get_process_key(my):
        import platform;
        host = platform.uname()[1]
        pid = os.getpid()
        return "%s:%s" % (host, pid)


    def get_job_search_type(my):
        return "sthpw/sync_job"


    def get_next_job(my):
        from queue import Queue
        import random
        import time
        interval = 0.05
        time.sleep(interval)
        job_search_type = my.get_job_search_type()
        servers_tried = []

        job = None
        while 1:
            my.servers = Container.get("TransactionQueueServers")
            if my.servers == None:
                trigger = TransactionQueueServersTrigger()
                trigger.execute()
                my.servers = Container.get("TransactionQueueServers")


            # use a random load balancer.  This algorithm is pretty
            # inefficient, but will only be an issue if there are lots
            # of servers
            num_servers = len(my.servers)
            if num_servers == 0:
                break


            server_index = random.randint(0, len(my.servers)-1)
            if server_index in servers_tried:
                continue

            server_code = my.servers[server_index].get_code()
            #print "server_code: ", server_code
            job = Queue.get_next_job(job_search_type=job_search_type, server_code=server_code)
            if job:
                break

            servers_tried.append(server_index)
            if len(servers_tried) == len(my.servers):
                break
        return job



    def start():
        
        scheduler = Scheduler.get()
        scheduler.start_thread()
        task = TransactionQueueManager(
            #check_interval=0.1,
            max_jobs_completed=20
        )
        task.cleanup_db_jobs()
        scheduler.add_single_task(task, mode='threaded', delay=1)
        # important to close connection after adding tasks
        DbContainer.close_all()

    start = staticmethod(start)



class TransactionQueueServersTrigger(Trigger):
    def execute(my):
        #print "Searching for sync shares ...."
        search = Search("sthpw/sync_server")
        search.add_filter("state", "online")
        servers = search.get_sobjects()
        #print "... found [%s] online remote share/s" % len(servers)

        Container.put("TransactionQueueServers", servers)



 




class TransactionQueueCmd(Command):
    '''get the last transaction in a queue and run periodically'''

    def execute(my):


        transaction_code = my.kwargs.get("transaction_code")
        job = my.kwargs.get("job")
        job_code = ''
        if job:
            job_code = job.get_code()

        print "Executing sync job [%s] ... "% job_code
        if not transaction_code:
            raise TacticException("WARNING: No transaction_code provided")

        server_code = my.kwargs.get("server")
        if not server_code:
            raise TacticException("WARNING: No server defined")

        server = Search.get_by_code("sthpw/sync_server", server_code)
        if not server:
            raise TacticException("ERROR: No server with code [%s] defined" % server_code)
        host = server.get_value("host")


        # file mode is usually determined by the server
        file_mode = my.kwargs.get("file_mode")
        if not file_mode:
            file_mode = server.get_value("file_mode", no_exception=True)
        if not file_mode:
            file_mode = 'upload'



        # sync mode is usually determined by the server
        sync_mode = my.kwargs.get("sync_mode")
        if not sync_mode:
            sync_mode = server.get_value("sync_mode", no_exception=True)
        if not sync_mode or sync_mode == 'default':
            # defautl is xmlrpc
            sync_mode = "xmlrpc"


        project_code = my.kwargs.get("project_code")
        #project_code = 'admin'
        if not project_code:
            raise TacticException("WARNING: Project code is not supplied")



        # get info for remote server definition
        ticket = server.get_value("ticket")
        if not ticket:
            raise TacticException("ERROR: No authorization ticket specified for server [%s]" % server_code)

        user = None
        password = None

        # grab data passed into it
        search = Search("sthpw/transaction_log")
        search.add_filter("code", transaction_code)
        log = search.get_sobject()
        if not log:
            print "WARNING: No transaction_log [%s] exists" % transaction_code
            return


        # provide an opportunity to filter out the transaction log
        # If a server is a complete copy, then no filter is necessary
        message, transaction_xml = my.filter_transaction( log, server )
        if not transaction_xml.get_nodes("transaction/*"):
            print "No actions in transaction passed security ... skipping sync to [%s]" % server.get_code()
            job = my.kwargs.get("job")
            job.set_value("error_log", message)
            job.commit()
            return


        import zlib, binascii
        #transaction_data = Common.process_unicode_string(transaction_xml)
        transaction_data = transaction_xml.to_string()
        if isinstance(transaction_data, unicode):
            transaction_data = transaction_data.encode('utf-8')
        length_before = len(transaction_data)
        compressed = zlib.compress(transaction_data)
        ztransaction_data = binascii.hexlify(compressed)
        ztransaction_data = "zlib:%s" % ztransaction_data
        length_after = len(ztransaction_data)
        print "transaction log recompress: ", "%s%%" % int(float(length_after)/float(length_before)*100), "[%s] to [%s]" % (length_before, length_after)
        # reset the transaction log sobject with the new xml.  This
        # should be harmless because it is never commited
        log.set_value("transaction", ztransaction_data)



        # NOTE: not really a command.  Just a set of actions
        cmd = TransactionFilesCmd(transaction_xml=transaction_xml)
        paths = cmd.execute()


        from pyasm.search import TableDataDumper

        # drop the transaction into a folder
        if sync_mode == 'file':
            base_dir = server.get_value("base_dir", no_exception=True)
            if not base_dir:
                base_dir = Config.get_value("checkin", "win32_dropbox_dir")

            if not base_dir:
                raise Exception("Must define a base_dir for sync_mode=file")

            ticket = server.get_value("ticket")

            my.handle_file_mode(base_dir, transaction_code, paths, log, transaction_xml, ticket)
            return



        # xmlrpc mode

        from tactic_client_lib import TacticServerStub
        remote_server = TacticServerStub(
            protocol='xmlrpc',
            server=host,
            project=project_code,
            user=user,
            password=password,
            ticket=ticket
        )


        # if the mode is undo, then execute an undo
        if sync_mode == 'undo':
            remote_server.undo(transaction_id=log.get_code(), is_sync=True)
        else:            

            # upload all of the files
            try:
                if file_mode == 'upload':
                    for path in paths:
                        if os.path.isdir(path):
                            print "upload dir: ", path
                            remote_server.upload_directory(path)
                        else:
                            print "upload file: ", path
                            remote_server.upload_file(path)


                #print "ping: ", remote_server.ping()
                remote_server.execute_transaction(log.get_data(), file_mode=file_mode)
            except Exception, e:
                print "Error sending remote command [%s]" % str(e)

                job = my.kwargs.get("job")
                job.set_value("error_log", str(e))
                #job.set_value("state", "error")
                job.commit()

                # print the stacktrace
                import traceback
                tb = sys.exc_info()[2]
                stacktrace = traceback.format_tb(tb)
                stacktrace_str = "".join(stacktrace)
                print "-"*50
                print stacktrace_str
                print "Error: ", str(e)
                print "-"*50

                raise

        job = my.kwargs.get("job")
        job.set_value("error_log", "")
        job.commit()



    def handle_file_mode(my, base_dir, transaction_code, paths, log, transaction_xml, ticket):
        # drop the transaction into a folder

        timestamp = log.get_value("timestamp")
        timestamp = parser.parse(timestamp)
        timestamp = timestamp.strftime("%Y%m%d_%H%M%S")

        asset_dir = Environment.get_asset_dir()

        # create the transactions dir if it does not exist
        if not os.path.exists("%s/transactions" % base_dir):
            os.makedirs("%s/transactions" % base_dir)

        base_dir = "%s/transactions/%s" % (base_dir, transaction_code)

        is_encrypted = True
        if is_encrypted == True:
            # put the transaction in a temp folder
            tmp_dir = Environment.get_tmp_dir(include_ticket=True)
            tmp_dir = "%s/%s-%s" % (tmp_dir, transaction_code, timestamp)

        else:
            tmp_dir = "%s/%s" % (base_dir, timestamp)

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)


        from pyasm.common import EncryptUtil
        encrypt = EncryptUtil(ticket)

        # create a simple manifest file
        f = open("%s/manifest.xml" % tmp_dir, 'wb')
        f.write('''<manifest code='transaction_log' version='1'>\n''')
        f.write('''  <sobject search_type="sthpw/transaction_log"/>\n''')
        f.write('''</manifest>\n''')
        f.close()


        tpath = "%s/sthpw_transaction_log.spt" % tmp_dir

        from pyasm.search import TableDataDumper
        dumper = TableDataDumper()
        dumper.set_delimiter("#-- Start Entry --#", "#-- End Entry --#")
        dumper.set_include_id(False)
        dumper.set_sobjects([log])
        dumper.dump_tactic_inserts(tpath, mode='sobject')


        tpath = "%s/_transaction.xml" % tmp_dir
        #f = open(tpath, 'wb')
        f = codecs.getwriter('utf8')(open(tpath, 'wb'))
        f.write(transaction_xml.to_string())
        f.close()


        # copy the checked in files
        for path in paths:
            rel_path = path.replace(asset_dir, "")
            rel_path = rel_path.lstrip("/")
            to_path = "%s/%s" % (tmp_dir, rel_path)
            to_dir = os.path.dirname(to_path)
            if not os.path.exists(to_dir):
                os.makedirs(to_dir)

            shutil.copy(path, to_dir)


        # zip up and encrypt the transaction
        if is_encrypted:
            zip_path = "%s.zip" % (tmp_dir)
            from pyasm.common import ZipUtil
            zip = ZipUtil()
            zip.zip_dir("%s" % (tmp_dir), zip_path)

            encrypt.encrypt_file(zip_path)


            shutil.move("%s.enc" % zip_path, "%s-%s.zip.enc" % (base_dir, timestamp))
            rmdir = os.path.dirname(tmp_dir)
            shutil.rmtree(rmdir)
            #os.unlink("%s.zip" % tmp_dir)


        job = my.kwargs.get("job")
        job.set_value("error_log", "")
        job.commit()


        return





    def filter_transaction(my, log, server):

        transaction_xml = log.get_xml_value("transaction")

        rules = server.get_value("access_rules")
        if not rules:
            rules = "<rules/>"

        #rules = '''
        #<rules>
        #<rule group='project' code='*' access='allow'/>
        #<rule group='search_type' code='sthpw/note' access='allow'/>
        #<rule group='search_type' code='new_project/brochures' access='allow'/>
        #</rules>
        #'''

        from tactic.ui.sync import SyncFilter
        sync_filter = SyncFilter(rules=rules, transaction=log)
        sync_filter.execute()

        filtered_xml = sync_filter.get_filtered_xml()
        message = sync_filter.get_message()
        return message, filtered_xml



class RunTransactionCmd(Command):

    def is_undoable():
        return False
    is_undoable = staticmethod(is_undoable)

    def execute(my):

        import types

        transaction_xml = my.kwargs.get("transaction_xml")
        file_mode = my.kwargs.get("file_mode")
        if not file_mode:
            file_mode = 'delayed'

        # if the first argument is a dictionary, then the whole
        # transaction sobject was passed through
        # NOTE: this is now the default
        if type(transaction_xml) == types.DictType:
            transaction_dict = transaction_xml
            transaction_xml = transaction_dict.get("transaction")
            timestamp = transaction_dict.get("timestamp")
            login = transaction_dict.get("login")

            # recreate the transaction
            transaction = SearchType.create("sthpw/transaction_log")
            for name, value in transaction_dict.items():
                if name.startswith("__"):
                    continue
                if name == 'id':
                    continue
                if value == None:
                    continue
                transaction.set_value(name, value)

        elif isinstance(transaction_xml, SObject):
            transaction = transaction_xml

        else:
            # Create a fake transaction.
            # This is only used for test purposes
            transaction = SearchType.create("sthpw/transaction_log")
            if transaction_xml:
                transaction.set_value("transaction", transaction_xml)
            else:
                print "WARNING: transaction xml is empty"
            transaction.set_value("login", "admin")

            # commit the new transaction.  This is the only case where
            # a transaction will not have a code, so it has to be committed.
            # The other case do not need to be committed because they will
            # already have codes and the transaction is committed in 
            # RedoCmd
            # 
            try:
                transaction.commit()
            except Exception, e:
                print "Failed to commit transaction [%s]: It may already exist. Skipping." % transaction.get_code()
                print str(e)
                return

        transaction_code = transaction.get_value("code")

        # see if this transaction already exists
        search = Search("sthpw/transaction_log")
        search.add_filter("code", transaction_code)
        if search.get_count():
            print "WARNING: transaction [%s] already exists" % transaction_code
            return



        security = Environment.get_security()
        ticket = security.get_ticket_key()

        # run the transaction in the project of the transaction
        project_code = transaction.get_value("namespace")
        Project.set_project(project_code)

        # NOTE: this is needed for operations, but does not
        # need to be committed
        transaction.set_value("ticket", ticket)

        # files mode is delayed then ignore file operations
        if file_mode == 'delayed':
            ignore = ['file']
        else:
            ignore = []
        #ignore = []


        # this will switch to use rel_path in transaction to get the files
        base_dir = my.kwargs.get("base_dir")

        transaction_log = transaction

        # Run the transaction
        from pyasm.command import RedoCmd
        cmd = RedoCmd(ignore=ignore, base_dir=base_dir, transaction_log=transaction)
        #Command.execute_cmd(cmd)
        cmd.execute()

        # Add remote sync registration
        transaction_log.trigger_remote_sync()




class TransactionFilesCmd(Command):

    def execute(my):

        mode = my.kwargs.get('mode')
        if not mode:
            mode = 'lib'


        transaction_xml = my.kwargs.get("transaction_xml")
        assert(transaction_xml)

        from pyasm.common import Xml, Environment

        if isinstance(transaction_xml, basestring):
            xml = Xml()
            xml.read_string(transaction_xml)
        else:
            xml = transaction_xml


        base_dir = Environment.get_asset_dir()
        paths = []


        # get all of the file nodes
        nodes = xml.get_nodes("transaction/file")
        for node in nodes:

            if xml.get_attribute(node, "type") == 'create':
                src = xml.get_attribute(node, "src")

                if mode == 'relative':
                    path = src
                else:
                    if src.startswith(base_dir):
                        path = src
                    else:
                        path = "%s/%s" % (base_dir, src)
                paths.append(path)

        return paths





# TEST TEST TEST TEST

__all__.append("TransactionImportCmd")
class TransactionImportCmd(Command):
    '''Test class to create a plugin for transactions'''

    def execute(my):
        import os
        path = my.kwargs.get("path")
        path = path.replace("\\", "/")
        basename = os.path.basename(path)

        upload_dir = Environment.get_upload_dir()

        path = "%s/%s" % (upload_dir, basename)

        f = open(path, 'r')

        transactions = []
        xml = [] 

        for line in f:
            if line == '\n':
                transactions.append(xml)
                xml = []
                continue

            xml.append(line.strip())

        transactions.append(xml)

        for transaction in transactions:
            value = "\n".join(transaction)


            # we have the transaction

            # recreate the log
            transacton_log = SearchType.create("sthpw/transaction_log")
            transaction_log.set_value("transaction", transaction)

            break



__all__.append("TransactionLogCompareCmd")
class TransactionLogCompareCmd(Command):

    def execute(my):

        mode = my.kwargs.get("mode")
        if not mode:
            mode = 'scan'



        search_key = my.kwargs.get("search_key")
        if not search_key:
            server_code = my.kwargs.get("server_code")
            server_sobj = Search.get_by_code("sthpw/sync_server", server_code)
        else:
            server_sobj = Search.get_by_search_key(search_key)

        if not server_sobj:
            return


        server_code = server_sobj.get_code()
        start_expr = my.kwargs.get("start_expr")


        # if search keys have been manually given
        search_keys = my.kwargs.get("search_keys")

        from tactic.ui.sync import SyncUtils
        if search_keys:
            sync_utils = SyncUtils(server_code=server_code, search_keys=search_keys)
        else:
            sync_utils = SyncUtils(server_code=server_code, start_expr=start_expr)
        remote_server = sync_utils.get_remote_server()

        if mode == 'test':
            my.info = {
                'ret_val': remote_server.ping()
            }
            return

        if mode == 'scan':
            info = sync_utils.get_transaction_info()
            print info

        #if mode == 'sync':
        if mode == 'pull':
            # get the missing remote transactions
            info = sync_utils.get_transaction_info()
            missing_transactions = info.get("remote_transactions")

            #my.download_transaction_files(missing_transactions)

            print "executing missing transactions locally: ", len(missing_transactions)

            # execute missing transactions on the local machine
            for transaction in missing_transactions:

                # FIXME: should check if the transaciton already exists
                code = transaction.get_value("code")

                # need to convert to a dictionary
                transaction_dict = transaction.get_data()

                cmd = RunTransactionCmd(transaction_xml=transaction_dict)
                cmd.execute()

        if mode == 'push':
            # get the missing remote transactions
            info = sync_utils.get_transaction_info()
            missing_transactions = info.get("local_transactions")

            # execute missing transactions on the local machine
            for transaction in missing_transactions:

                # do them one at a time (slow)
                print "running: ", transaction.get_code()

                # need to convert to a dictionary
                transaction_dict = transaction.get_data()

                remote_server.execute_transaction(transaction_dict)






    def download_transaction_files(my, transactions):
        '''This uses a simple httpd download mechanism to get the files.
        '''

        remote_host = sync_utils.get_remote_host()

        download_mode = 'http'

        # Try a mode where files are zipped
        if download_mode == 'zip':
            remote_server.download_zip(paths)



        # go through each transaction and look at the files
        for transaction in transactions:
            transaction_xml = transaction.get("transaction")
            cmd = TransactionFilesCmd(transaction_xml=transaction_xml, mode='relative')
            paths = cmd.execute()


            # download to the temp dir
            to_dir = Environment.get_tmp_dir()
            ticket = Environment.get_ticket()
            to_dir = "%s/%s" % (to_dir, ticket)

            # or we could download directly to that asset directory
            base_dir = Environment.get_asset_dir()

            # do the slow method
            for path in paths:
                url = "%s/assets/%s" % (remote_host, path)

                print "downloading: ", url
                remote_server.download(url, to_dir)

                # FIXME: the problem with this is that it is not undoable
                #dirname = os.path.dirname(path)
                #to_dir = "%s/%s" % (base_dir, dirname)
                #print "to_dir: ", to_dir


                remote_server.download(url, to_dir)






__all__.extend( ['TransactionPluginCreateCmd', 'TransactionPluginInstallCmd'])

from pyasm.common import ZipUtil
from plugin import PluginCreator, PluginInstaller


class TransactionPluginCreateCmd(Command):
    '''Test class to create a plugin for transactions'''

    def execute(my):
        project_code = my.kwargs.get("project_code")
        transaction_code = my.kwargs.get("transaction_code")
        login = my.kwargs.get("login")

        session = my.kwargs.get("session")
        start_time = session.get("start_time")
        end_time = session.get("end_time")

        search_keys = session.get("search_keys")
        if search_keys != None:
            if search_keys == '':
                raise TacticException("No search keys passed in")
            search_keys = search_keys.split("|")
            if not search_keys:
                raise TacticException("No search keys passed in")

            transactions = Search.get_by_search_keys(search_keys)
            codes = [x.get_code() for x in transactions]
            assert len(search_keys) == len(codes)
            expr = '''@SOBJECT(sthpw/transaction_log['code','in','%s']['@ORDER_BY','code asc'])''' % ("|".join(codes))
        else:
            expr = '''@SOBJECT(sthpw/transaction_log['login','%s']['namespace','%s']['timestamp','&gt;','%s']['timestamp','&lt;','%s']['@ORDER_BY','code asc'])''' % (login, project_code, start_time, end_time)

        manifest_xml = '''
<manifest code='transaction_log' version='1'>
<sobject expression="%s" search_type="sthpw/transaction_log"/>
</manifest>
        ''' % (expr)


        plugin = SearchType.create("sthpw/plugin")
        plugin.set_value("code", "transaction_log")
        plugin.set_value("version", "1.0")

        creator = PluginCreator(manifest=manifest_xml, plugin=plugin)
        creator.execute()

        plugin_path = creator.get_plugin_path()

        plugin_dir = creator.get_plugin_dir()

        # find all the logs (again!!!)
        # FIXME: should get from plugin
        expr = expr.replace("&gt;", ">")
        expr = expr.replace("&lt;", "<")
        logs = Search.eval(expr)

        asset_dir = Environment.get_asset_dir()

        for log in logs:
            transaction_xml = log.get_xml_value("transaction").to_string()
            cmd = TransactionFilesCmd(transaction_xml=transaction_xml)
            paths = cmd.execute()
            for path in paths:
                rel_path = path.replace(asset_dir, "")
                rel_path = rel_path.lstrip("/")
                new_path = "%s/assets/%s" % (plugin_dir, rel_path)
                dirname = os.path.dirname(new_path)

                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                print "adding: [%s]" % new_path
                shutil.copy(path, new_path)



class TransactionPluginInstallCmd(Command):
    '''Test class to create a plugin for transactions'''

    def execute(my):

        import os
        path = my.kwargs.get("path")
        path = path.replace("\\", "/")
        basename = os.path.basename(path)

        upload_dir = Environment.get_upload_dir()

        path = "%s/%s" % (upload_dir, basename)

        paths = ZipUtil.extract(path)


        # TODO: why do we need to read the manifest here?
        # ... should be automatic
        manifest_path = "%s/transaction_log/manifest.xml" % upload_dir
        if not os.path.exists(manifest_path):
            raise TacticException("Cannot find manifest file [%s]" % manifest_path)
        f = codecs.open(manifest_path, 'r', 'utf-8')
        manifest_xml = f.read()
        f.close()
        creator = PluginInstaller(base_dir=upload_dir, manifest=manifest_xml)
        creator.execute()


        # run the transactions
        logs = creator.get_jobs()
        for log in logs:
            transaction_xml = log.get_value("transaction")
            cmd = RunTransactionCmd(transaction_xml=transaction_xml)
            cmd.execute()

            # This is needed here, because normaly, RunTransactionCmd
            # is run by a sync, so it blocks further syncs.  When
            # a transaction session is installed, we need to propogate
            # this to the other machines
            cmd = TransactionQueueAppendCmd()
            input = {
                'search_type': 'sthpw/transaction_log',
                'sobject': log
            }
            cmd.input = input
            cmd.execute()






# TEST
if __name__ == '__main__':

    from pyasm.security import Batch
    Batch()
    #cmd = TransactionPluginCreateCmd()
    #Command.execute_cmd(cmd)

    #cmd = TransactionPluginInstallCmd()
    #Command.execute_cmd(cmd)


    cmd = TransactionLogCompareCmd()
    Command.execute_cmd(cmd)



