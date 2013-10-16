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

# Manages transactions across multiple databases and commands.
# Also handles nested transactions

__all__ = ["TransactionException", "Transaction", "FileUndo", "TableUndo", "TableDropUndo", "AlterTableUndo"]

import os, time, codecs

from pyasm.common import *


class TransactionException(Exception):
    pass


class Transaction(Base):

    KEY = "Transaction:transaction"

    def __init__(my):
        my.counter = 0
        my._reset()
        my.command_class = ""
        my.description = ""
        my.title = ''
        my.record_flag = True


    def _reset(my):
        my.counter = 0
        my.transaction_objs = []
        my.databases = {}
        my.xml = Xml()
        my.xml.create_doc("transaction")
        my.transaction_log = None
        my.change_timestamps = {}

    def set_record(my, record_flag):
        my.record_flag = record_flag

    def get_xml(my):
        return my.xml


    def get_change_timestamp(my, search_type, search_code, is_insert=False):

        key = "%s|%s" % (search_type, search_code)

        log = my.change_timestamps.get(key)
        if log != None:
            return log

        from search import Search, SearchType
        # if this is an insert, then no entry will exist
        if not is_insert:
            search = Search("sthpw/change_timestamp")
            search.add_filter("search_type", search_type)
            search.add_filter("search_code", search_code)
            log = search.get_sobject()
        else:
            log = None

        if not log:
            log = SearchType.create("sthpw/change_timestamp")
            log.set_value("search_type", search_type)
            log.set_value("search_code", search_code)
            changed_on = {}
            changed_by = {}
            log.set_value("changed_on", changed_on)
            log.set_value("changed_by", changed_by)

        my.change_timestamps[key] = log

        return log


    def get_change_timestamps(my):
        return my.change_timestamps





    def set_transaction(my, transaction_log):
        #my.xml = transaction_log.get_xml_value("transaction")

        # We now start with a fresh transaction and then only append
        # on commit.
        my.xml = Xml()
        my.xml.read_string("<transaction/>")
        my.transaction_log = transaction_log


    def set_description(my, description):
        my.description = description

    def add_description(my, description):
        if my.description:
            my.description += "\n%s" % description
        else:
            my.description += "%s" % description


    def set_title(my, title):
        my.title = title

    def set_command_class(my, command_class):
        my.command_class = command_class


    def is_in_transaction(my):
        if my.counter == 0:
            return False
        else:
            return True


    def start(my):
        if my.counter == 0:
            my._reset()

        my.counter += 1
        #if my.counter > 1:
        #    raise Exception("counter > 1")


    def commit_all(my):
        my.counter = 1
        my.commit()
        



    def commit(my):
        my.counter -= 1
        if my.counter < 0:
            print("Transaction counter below zero")
            raise TransactionException("Transaction counter below zero")

        # check if this is a nested transaction
        if my.counter > 0:
            return

        assert my.counter == 0

        # commit all of the transaction items
        from sql import SqlException
        for transaction_obj in my.transaction_objs:
            try:
                transaction_obj.commit()
            except SqlException:
                print("ERROR: FAILED TO COMMIT", transaction_obj.get_database_name())

        # check the number of nodes in the transaction.  If there are
        # no nodes, then nothing happened don't put this into the log
        nodes = my.xml.get_nodes("transaction/*")
        if len(nodes) == 0:
            my._reset()
            return



        # after committing all of the transaction items, commit this
        # transaction to the transaction log
        if my.record_flag:
            my.commit_log()


        # reset the transaction
        my._reset()


    def abort(my):
        return my.rollback()


    def rollback(my):

        if my.counter <= 0:
            raise TransactionException("Transaction start/rollback mismatch")

        # go through each transaction items and rollback
        for transaction in my.transaction_objs:
            transaction.rollback()

        # use the current ticket
        security = Environment.get_security()
        if security:
            ticket = security.get_ticket_key()
        else:
            ticket = ""

        # Undo file system calls
        # TODO: should put this into a transaction object and register it
        # Do it manually here for now
        xml = my.xml
        nodes = xml.get_nodes("transaction/file")
        nodes.reverse()
        for node in nodes:
            FileUndo.undo(node, ticket)
         
        # reset transaction and the counter
        my._reset()
    
        # close connections, not sure if this is needed
        #from pyasm.search import DbContainer
        #DbContainer.close_session_sql()


    def register(my, transaction_obj):
        '''registers the transaction object.  Note a command can be a
        transaction object.'''

        # if we are not in transaction, don't bother
        if my.counter == 0:
            return

        # for a command, this start functions doesn't really do anything
        transaction_obj.start()
        my.transaction_objs.append(transaction_obj)



    def register_database(my, database):
        '''makes sure that the database is only in the transaction once'''

        # if we are not in transaction, don't bother
        if my.counter == 0:
            return

        db_name = database.get_database_name()

        # if the database is listed, then ignore it
        if my.databases.has_key(db_name):
            return

        # start a transaction in the database
        database.start()
        my.databases[db_name] = database

        # add it to the transactions
        my.transaction_objs.append(database)

    def get_databases(my):
        return my.databases

    def get_database(my, db_name):
        return my.databases.get(db_name)


    # logging functions for transactionss
    # Any action that occurs to the system should get recorded here
    def get_transaction_log(my):
        return my.xml


    def get_file_log(my):
        '''get only the file logs'''
        xml = my.get_transaction_log()
        file_nodes = xml.get_nodes("transaction/file")

        # create a new document
        file_xml = Xml()
        file_xml.create_doc("transaction")
        file_root = file_xml.get_root_node()

        for file_node in file_nodes:
            file_xml.append_child(rile_root, file_node)

        return file_xml





    def create_log_node(my,node_name):
        root = my.xml.get_root_node()
        node = my.xml.create_element(node_name)
        my.xml.append_child(root, node)
        return node


    def commit_log(my):

        if not my.description:
            my.description = "No description available"

        # if there is a command class, check that is undoable, otherwise
        # it is by default undoable
        if my.command_class:
            module, class_name = Common.breakup_class_path(my.command_class)

            try:
                exec("import %s" % module)
                is_undoable = eval( "%s.is_undoable()" % my.command_class )
                if not is_undoable:
                    return
            except AttributeError:
                # by default a command is undoable
                pass


        xml_string = my.xml.to_string()

        xml_lib = Xml.get_xml_library()

        string_append = True
        if string_append and my.transaction_log:
            # append the value instead
            old_value = my.transaction_log.get_value("transaction")
            if old_value == '<transaction/>':
                old_lines = []
            else:
                old_lines = old_value.split("\n")

            if old_lines:
                if xml_lib == 'lxml':
                    old_lines = old_lines[2:-1]
                else:
                    old_lines = old_lines[2:-1]


            xml_lines = xml_string.split("\n")
            if xml_lines:
                if xml_lib == 'lxml':
                    xml_lines = xml_lines[1:-1]
                else:
                    xml_lines = xml_lines[2:-2]


            new_lines = []
            new_lines.append('''<?xml version='1.0' encoding='UTF-8'?>\n<transaction>''')
            new_lines.extend(old_lines)
            new_lines.append("<!-- new transaction -->")
            new_lines.extend(xml_lines)

            # depending on the version of lxml, this may or may not end with
            # </transaction> already ... this protects against that case
            if new_lines[-1] != "</transaction>":
                new_lines.append('''</transaction>''')
 
            new_value = '\n'.join(new_lines)

            my.transaction_log.set_value("transaction", new_value )
            my.transaction_log.set_value("description", my.description)
            my.transaction_log.commit()

        elif my.transaction_log:
            my.transaction_log.set_value("transaction", xml_string )
            my.transaction_log.set_value("description", my.description)
            my.transaction_log.commit()
        else:
            from transaction_log import TransactionLog
            my.transaction_log = TransactionLog.create( \
                my.command_class, xml_string, my.description, my.title )


        # update the change_timestamp logs
        my.update_change_timestamps(my.transaction_log)

        # add remote sync registration
        my.transaction_log.trigger_remote_sync()

        return my.transaction_log


    def update_change_timestamps(my, transaction_log):

        # commit all of the changes logs
	# NOTE: this does not get executed on undo/redo
        timestamp = transaction_log.get_value("timestamp")
        code = transaction_log.get_value("code")

        from pyasm.biz import Project
        from pyasm.search import Search
        project_code = Project.get_project_code()

        for key, change_timestamp in my.change_timestamps.items():
            new_changed_on = change_timestamp.get_json_value("changed_on", {})

            search_type = change_timestamp.get_value("search_type")
            search_code = change_timestamp.get_value("search_code")
            search = Search("sthpw/change_timestamp")
            search.add_filter("search_type", search_type)
            search.add_filter("search_code", search_code)
            ct = search.get_sobject()
            if ct:
                changed_on = ct.get_json_value("changed_on", {})
                change_timestamp = ct
            else:
                changed_on = change_timestamp.get_json_value("changed_on", {})

            for column, value in new_changed_on.items():
                if value == "CHANGED":
                    changed_on[column] = timestamp

            change_timestamp.set_json_value("changed_on", changed_on)
            change_timestamp.set_value("transaction_code", code)
            change_timestamp.set_value("project_code", project_code)

            # it is possible that this commit will fail under heavy load
            # because per chance, the same search_type/search_type combo
            # was created in another transaction
            from pyasm.search import SqlException, DbContainer
            try:
                change_timestamp.commit(triggers=False, log_transaction=False)
            except SqlException, e:
                print "WARNING: ", str(e)
                if change_timestamp.is_insert:
                    action = "insert"
                else:
                    action = "update"
                print "Could not change_timestamp for %s: %s - %s" % (action, search_type, search_code)
                DbContainer.commit_thread_sql()





    def commit_file_log(my):
        xml_string = my.get_file_log().to_string()
        from transaction_log import TransactionLog
        transaction_log = TransactionLog.create( \
            my.command_class, xml_string, my.description, my.title )
        return transaction_log



    # static function to get transaction singleton

    def get(create=False, force=False):
        '''start a transaction or create a new one
        
        @params
        create - option to create a transaction if none exists
        force - force create a new transaction
        '''

        # get the top transaction
        transaction = None
        if not force:
            transactions = Container.get_seq(Transaction.KEY)
            if transactions:
                transaction = transactions[-1]

        if force:
            # force start a new transaction
            transaction = Transaction()
            transaction.start()
            Container.append_seq(Transaction.KEY,transaction)
        elif create:
            # only create a transaction if it does not exist
            if transaction:
                # just start the transaction
                transaction.start()
            else:
                # start a new transaction
                transaction = Transaction()
                transaction.start()
                Container.append_seq(Transaction.KEY,transaction)

        return transaction
    get = staticmethod(get)


    def clear_stack(cls):
        '''removes all transactions on the stack'''
        transactions = Container.get_seq(Transaction.KEY)
        if transactions:
            for i in range(0, len(transactions)):
                transaction = transactions.pop()
                assert not transaction.is_in_transaction()
                del(transactions)

    clear_stack = classmethod(clear_stack)



    def remove_from_stack(cls):
        '''removes the last transaction on the stack'''
        transactions = Container.get_seq(Transaction.KEY)
        if transactions:
            transaction = transactions[-1]
            for sql in transaction.get_databases():
                sql.close()
            del(transactions[-1])

    remove_from_stack = classmethod(remove_from_stack)


    def resume_by_id(cls, transaction_log_id):
        from transaction_log import TransactionLog
        transaction_log = TransactionLog.get_by_id(transaction_log_id)
        if not transaction_log:
            raise TransactionException("Transaction [%s] does not exist" % transaction_log_id)
        return cls.resume(transaction_log)
    resume_by_id = classmethod(resume_by_id)


    def resume(cls, transaction_log):
        '''continue a previous transaction.  Note that calling this will
        override any transaction currently in progress'''
        assert transaction_log

        # verify that the current user is the same as the one for the
        # transaction
        if Environment.get_user_name() != transaction_log.get_value("login"):
            raise TransactionException("Transaction id [%s] with user [%s] does does not belong to [%s]" % (transaction_log.get_id(), transaction_log.get_value("login"), Environment.get_user_name() ) )

        # start a new transaction
        transaction = Transaction.get(create=True)

        # transfer information from the log to the transaction
        description = transaction_log.get_value("description")
        title = transaction_log.get_value("title")
        transaction.set_description(description)
        transaction.set_title(title)
        command_cls = transaction_log.get_value("command")
        transaction.set_command_class(command_cls)
        transaction.set_transaction(transaction_log)

        
        return transaction
    resume = classmethod(resume)

        





import shutil

class FileUndo:
    '''encapsulates common file manipulations that can be undone'''

    def mkdir(src):
        if os.path.exists(src):
            return

        os.makedirs(src)
        FileUndo._add_to_transaction_log("mkdir", src, "")
 
    mkdir = staticmethod(mkdir)


    def rmdir(src):
        if os.path.exists(src):
            try:
                os.rmdir(src)
            except Exception, e:
                print "WARNING: could not remove [%s]" % src
        FileUndo._add_to_transaction_log("rmdir", src, "")
 
    rmdir = staticmethod(rmdir)



    def remove(src):
        # remove doesn't actually remove.  It just moves it to a cache
        # file in case it has to be undone
        tmp_dir = "%s/cache" % Environment.get_tmp_dir()
        filename = os.path.basename(src)
        tmp_file = "%s/%s" % (tmp_dir, filename)

        if os.path.exists(src):
            System().makedirs(tmp_dir)
            if os.path.exists(tmp_file):
                # just write over
                if os.path.isdir(tmp_file):
                    shutil.rmtree(tmp_file)
                else:
                    os.unlink(tmp_file)
            shutil.move(src, tmp_file)

        # all file links need to be relative
        asset_dir = Environment.get_asset_dir()
        # for relative_path to work (which uses file names, we must convince
        # it that asset_dir is a dir
        if not asset_dir.endswith("/"):
            asset_dir = "%s/" % asset_dir


        rel_src = Common.relative_path(asset_dir, src)
        #rel_dst = Common.relative_path(asset_dir, tmp_file)
        FileUndo._add_to_transaction_log("remove", rel_src, tmp_file)

    remove = staticmethod(remove)


    def create(orig, src=None, io_action=True, extra={}):
        '''makes the src file look like it was just created (from orig)
        The difference with this and 'move' is that on undo, 'move' will
        move the file back to the src and this will move it to a cache
        directory'''
        if io_action:
            if src:
                # take into account the situation where this is a link
                if os.path.islink(src):
                    os.unlink(src)

                if io_action == 'copy':
                    shutil.copy(orig,src)
                else:
                    shutil.move(orig,src)
            else:
                src=orig

        extra['orig'] = orig

        FileUndo._add_to_transaction_log("create", src, "", extra=extra)
    create = staticmethod(create)
       


    def copy(src,dst):
        # only work with absolute paths
        src = os.path.abspath(src)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copyfile(src, dst)
        FileUndo._add_to_transaction_log("copy", src, dst)
    copy = staticmethod(copy)



    def move(src,dst):
        src = os.path.abspath(src)
        shutil.move(src,dst)
        FileUndo._add_to_transaction_log("move", src, dst)
    move = staticmethod(move)

    def symlink(src,dst,mode='symlink'):
        '''make a symbolic link'''
        assert mode in ['symlink','copy']

        asset_dir = Environment.get_asset_dir()
        # for relative_path to work (which uses file names, we must convince
        # it that asset_dir is a dir
        if not asset_dir.endswith("/"):
            asset_dir = "%s/" % asset_dir

        extra = {}

        def handle_link(dst, extra):
            '''read the symlink and find the prev'''
            prev = os.readlink(dst)
            wd = os.getcwd()
            dst_dir = os.path.dirname(dst)
            os.chdir(dst_dir)
            # while it seems like you can join any 2 paths, it is based on working directory
            prev = os.path.join(dst_dir, os.path.abspath(prev))
            extra['prev'] = prev
            os.unlink(dst)
            # reset working directory
            os.chdir(wd)

        dirname = os.path.dirname(dst)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        extra['mode'] = mode

        # OS which don't support symlinks are treated differently, however
        # the transaction will write the same info regardless of OS.
        link_name = os.path.basename(dst)
        link_dir = os.path.dirname(dst)
        link_path = "%s/.%s.link" % (link_dir, link_name)
        extra['link'] = Common.relative_path(asset_dir, link_path)

        if os.name == "nt" or mode == 'copy':
            # check the link file

            if os.path.exists(link_path):
                link_file = open(link_path, "rb")
                prev = link_file.readline()
                link_file.close()
                extra['prev'] = Common.relative_path(asset_dir, prev)
                os.unlink(link_path)

            import codecs
            link_file = codecs.open(link_path, "w", "utf-8")
            link_file.write(src)
            link_file.close()

            # this islink condition seems redundant for nt but in linux copy mode, it is valid
            if os.path.islink(dst):
                handle_link(dst, extra)
            elif os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.unlink(dst)

            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copyfile(src, dst)
        else:

            # if it already exists, read where it was pointing to
            if os.path.islink(dst):
                handle_link(dst, extra)
            elif os.path.exists(dst): 
                # raise an error if it is a preexisting file
                # Note: it is possible that this file
                # was a symlink using copy mode and this is why it was a
                # file.  This is a fringe case.
                raise TacticException("The symlink destination already existed as a regular file [%s]"%dst)

            # create the link
            rel = Common.relative_path(dst, src)
            try:
                os.symlink(rel,dst)
            except Exception:
                print "Error: could not symlink [%s] to [%s]" % (rel, dst)
                raise 

        # all file links need to be relative
        rel_src = Common.relative_path(asset_dir, src)
        rel_dst = Common.relative_path(asset_dir, dst)

        FileUndo._add_to_transaction_log("symlink", rel_src, rel_dst, extra)

    symlink = staticmethod(symlink)


    def _add_to_transaction_log(type, src, dst, extra={}):

        # remove the base from the beginning
        base_dir = Environment.get_asset_dir()
        if not base_dir.endswith("/"):
            base_dir = "%s/" % base_dir

        if src and src.startswith("/"):
            src = src.replace(base_dir, "")
        if dst and dst.startswith("/"):
            dst = dst.replace(base_dir, "")

  
        transaction = Transaction.get()
        if not transaction:
            return

        file_node = transaction.create_log_node("file")
        Xml.set_attribute(file_node,"type",type)
        Xml.set_attribute(file_node,"src",src)
        Xml.set_attribute(file_node,"dst",dst)
        
        for name,value in extra.items():
            Xml.set_attribute(file_node,name,value)

    _add_to_transaction_log = staticmethod(_add_to_transaction_log)
      



    def undo(node, ticket=""):

        #if not ticket:
        #    ticket = "NO_TICKET"

        type = Xml.get_attribute(node,"type")
        src = Xml.get_attribute(node,"src")
        dst = Xml.get_attribute(node,"dst")

        base_dir = Environment.get_asset_dir()
        if src and not src.startswith("/"):
            src = "%s/%s" % (base_dir, src)
        if dst and not dst.startswith("/"):
            dst = "%s/%s" % (base_dir, dst)


        try:
            if type == "move":
                # move the file back
                dirname = os.path.dirname(src)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                shutil.move(dst,src)
            elif type == "copy":
                # remove the dst tree of file
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.unlink(dst)
                else:
                    Environment.add_warning("Cannot delete", "Cannote remove nonexistent file/dir [%s]" % dst)
            elif type == "remove":
                # move tmp file back
                shutil.move(dst,src)
            elif type == "mkdir":
                # remove directory
                try:
                    os.rmdir(src)
                except OSError, e:
                    if 'Directory not empty' in e.__str__():
                        # can consider removing the contents first and then rmdir
                        raise TransactionException(e)

            elif type == "rmdir":
                # add the directory back
                if not os.path.exists(src):
                    os.makedirs(src)

            elif type == "create":
                # move to a temp directory
                tmp_dir = Environment.get_tmp_dir()
                tmp_dir = "%s/cache/%s" % (tmp_dir, ticket)
                try:
                    if not os.path.exists(tmp_dir):
                        System().makedirs(tmp_dir)

                    if os.path.isdir(src):
                        basename = os.path.basename(src)
                        cache_dir = "%s/%s" % (tmp_dir,basename)
                        if os.path.exists(cache_dir):
                            shutil.rmtree(cache_dir)
                        shutil.move(src, "%s/%s" % (tmp_dir,basename) )
                    else:
                        shutil.move(src, "%s" % tmp_dir )

                except Exception, e:
                    # if there are any errors in moving to cache, then
                    # just delete the files
                    if os.path.exists(src):
                        if os.path.isdir(src):
                            shutil.rmtree(src)
                        else:
                            os.unlink(src)
                        print "Error: ", e
                        print "Error moving [%s] to cache directory in [%s] failed. Removed repository files" % (src, tmp_dir)

                # attempt to remove directories
                last_dir = None
                dirname = src
                while 1:
                    try:
                        dirname = os.path.dirname(dirname)
                        if dirname == last_dir:
                            break
                        os.rmdir(dirname)
                        last_dir = dirname
                    except:
                        break


            elif type == "symlink":
                # this is not implemented in windows because windows
                # does not support symbolic links, we are copying instead
                # if mode is copy or os is nt
                mode = Xml.get_attribute(node,"mode")
                if os.name == "nt" or mode == 'copy':
                    prev = Xml.get_attribute(node,"prev")
                    link_path = Xml.get_attribute(node,"link")
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            shutil.rmtree(dst)
                        else:
                            os.unlink(dst)
                    if not prev:
                        
                        if link_path and os.path.exists(link_path):
                            if os.path.isdir(link_path):
                                shutil.rmtree(link_path)
                            else:
                                os.unlink(link_path)
                    else:
                        if os.path.isdir(prev):
                            shutil.copytree(prev, dst)
                        else:
                            shutil.copy(prev,dst)
                        import codecs
                        link_file = codecs.open(link_path, "w", "utf-8")
                        link_file.write(prev)
                        link_file.close()
                else:
                    # restablish the previous link
                    if os.path.islink(dst):
                        os.unlink(dst)
                    prev = Xml.get_attribute(node,"prev")
                    if prev:
                        
                        # create the link
                        rel = Common.relative_path(dst, prev)
                        os.symlink(rel, dst)

        except IOError, e:
            print( e.__str__())
            print("Failed to undo %s %s" % (type, src))
        except OSError, e:
            raise TransactionException("Failed to undo due to OS Error during %s. %s" % (type, e.__str__()))
        except Exception, e:
            print "Error: %s" %e
            raise

    undo = staticmethod(undo)



    def redo(node, ticket="", base_dir=''):
        '''interpret transaction log and perform the actions in it'''

        #if not ticket:
        #    ticket = "NO_TICKET"

        type = Xml.get_attribute(node,"type")
        src = Xml.get_attribute(node,"src")
        dst = Xml.get_attribute(node,"dst")

        asset_dir = Environment.get_asset_dir()
        if src and not src.startswith("/"):
            src = "%s/%s" % (asset_dir, src)
        if dst and not dst.startswith("/"):
            dst = "%s/%s" % (asset_dir, dst)


        if type == "move":
            # move the file
            shutil.move(src,dst)
        elif type == "copy":
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copyfile(src, dst)
        elif type == "remove":
            shutil.move(src,dst)
        elif type == "mkdir":
            # recreate directory
            if not os.path.exists(src):
                os.mkdir(src)
        elif type == "create":

            security = Environment.get_security()
            ticket = security.get_ticket_key()

            tmp_dir = Environment.get_tmp_dir()

            # first check the upload, then the cache
            filename = os.path.basename(src)

            # find the location of the file

            # if this is from reruning a transaction from another server
            # then the file will be in the transaction folder???
            # when to use rel_path?
            if base_dir:
                rel_path = Xml.get_attribute(node,"rel_path")
                orig = "%s/%s" % (base_dir, rel_path)
                src = "%s/%s" % (asset_dir, rel_path)
                src_dir = os.path.dirname(src)
            else:
                # if the transaction was undo, then the file will be in the
                # cache folder
                orig = "%s/cache/%s/%s" % (tmp_dir, ticket, filename)
                if not os.path.exists(orig):
                    orig = "%s/upload/%s/%s" % (tmp_dir, ticket, filename)

                src_dir = os.path.dirname(src)


            if not os.path.exists(orig):
                print "WARNING: cannot find file [%s]" % orig

            if not os.path.exists(src_dir):
                os.makedirs(src_dir)

            if base_dir:
                shutil.copy(orig, src)
            else:
                shutil.move(orig, src)

            #dirname = os.path.dirname(src)
            #if not os.path.exists(dirname):
            #    os.makedirs(dirname)
            #shutil.move("%s/%s" % (tmp_dir,filename), src)
        elif type == "symlink":
            mode = Xml.get_attribute(node,"mode")
            if os.name == "nt" or mode == 'copy':
                link_path = Xml.get_attribute(node,"link")
                dirname = os.path.dirname(link_path)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                link_file = open(link_path, 'w')
                link_file.write(src)
                link_file.close()
                # link_file doesn't mean much for dir??
                dstdirname = os.path.dirname(dst)
                if not os.path.exists(dstdirname):
                    os.makedirs(dstdirname)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copyfile(src, dst)
            else:
                if os.path.exists(dst):
                    os.unlink(dst)

                # create the link
                rel = Common.relative_path(dst, src)
                try:
                    os.symlink(rel,dst)
                except Exception:
                    print "Error: could not symlink [%s] to [%s]" % (rel, dst)
                    raise 



    redo = staticmethod(redo)




class TableUndo(Base):

    def log(search_type, database, table):
        # build the sobject xml action description
        transaction = Transaction.get()
        if not transaction:
            print "WARNING: no transaction found"
            return

        sobject_node = transaction.create_log_node("table")
        Xml.set_attribute(sobject_node,"search_type", search_type)
        Xml.set_attribute(sobject_node,"table",table)
        Xml.set_attribute(sobject_node,"database",database)
        Xml.set_attribute(sobject_node,"action", "create")

        from search import SearchType, Sql, DbContainer
        search_type = SearchType.build_search_type(search_type, project_code=database)

        column_info = SearchType.get_column_info(search_type)
        xml = transaction.get_xml()

        #print "column_info: ", column_info
        #column_info:  {u'code': {'data_type': 'varchar', 'nullable': True}, u'description': {'data_type': 'text', 'nullable': True}, u'timestamp': {'data_type': 'timestamp', 'nullable': True}, u's_status': {'data_type': 'varchar', 'nullable': True}, u'keywords': {'data_type': 'text', 'nullable': True}, u'login': {'data_type': 'varchar', 'nullable': True}, u'id': {'data_type': 'integer', 'nullable': False}, u'name': {'data_type': 'varchar', 'nullable': True}}
        for column, data in column_info.items():
            column_node = xml.create_element("column")
            xml.append_child(sobject_node, column_node)
            xml.set_attribute(column_node,"name",column)

            # make some assumptions about id
            if column == 'id':
                data_type = 'serial'
                xml.set_attribute(column_node,"primary_key","true")
            elif column == 'code':
                data_type = data.get("data_type")
                xml.set_attribute(column_node,"unique","true")
            else:
                data_type = data.get("data_type")
            xml.set_attribute(column_node,"data_type",data_type)


            if data.get('nullable'):
                nullable = "true"
            else:
                nullable = "false"
            xml.set_attribute(column_node,"nullable",nullable)




        # have to call nextval() since currval may fail if the sequence hasn't been initialized

        # this is not necessary in sqlite as it uses an autoincrement instead
        # of sequence
        from pyasm.biz import Project
        db_resource = Project.get_db_resource_by_search_type(search_type)
        sql = DbContainer.get(db_resource)
        impl = sql.get_database_impl()
        if impl.has_sequences():
            seq_max = SearchType.sequence_nextval(search_type)

            if seq_max - 1 > 0:
                Xml.set_attribute(sobject_node,"seq_max", seq_max)
                SearchType.sequence_setval(search_type, seq_max-1)

    log = staticmethod(log)


    def undo(node):

        from sql import SqlException

        try:
            search_type = Xml.get_attribute(node,"search_type")
            database = Xml.get_attribute(node,"database")
            table = Xml.get_attribute(node,"table")

            if database == "" or table == "" or not search_type:
                raise TransactionException()


            from pyasm.biz import Project
            from search import DbContainer
            db_resource = Project.get_db_resource_by_search_type(search_type)
            sql = DbContainer.get(db_resource)

            host = sql.get_host()
            user = sql.get_user()

            tmp_dir = Environment.get_tmp_dir()
            schema_path = "%s/cache/create_%s_%s.sql" % \
                (tmp_dir, database, table)

            if os.path.exists(schema_path):
                os.unlink(schema_path)

            # dump the table to a file and store it in cache
            from sql_dumper import TableSchemaDumper
            dumper = TableSchemaDumper(search_type)
            try:
                dumper.dump_to_tactic(path=schema_path)
            except SqlException, e:
                print "SqlException: ", e
        
            # dump the table data to a file and store it in cache
            from sql_dumper import TableDataDumper
            dumper = TableDataDumper()
            dumper.set_info(table)
            try:
                dumper.execute()
            except SqlException, e:
                print "SqlException: ", e

            #cmd = "pg_dump -h %s -U %s -t %s %s > %s" % \
            #    (host, user, table, database, schema_path)
            #os.system(cmd)

            sql.do_update('DROP TABLE "%s"' % table)

        except SqlException, e:
            # This means that the table did not exist, DROP TABLE failed.
            # if there is an sql exception, Note it, but continue.  The
            # undo must complete.
            # TODO: should put this in an error log
            print "SqlException: ", e

        except TransactionException, e:
            print "Failed to undo '%s' '%s'" % (database, table)

    undo = staticmethod(undo)



    def redo(node):
        try:
            search_type = Xml.get_attribute(node,"search_type")
            database = Xml.get_attribute(node,"database")
            table_name = Xml.get_attribute(node,"table")
            seq_max = Xml.get_attribute(node,"seq_max")
            
            if database == "" or table_name == "" or not search_type:
                raise TransactionException("Missing database or table in transaction_log")

            # re-enter table
            from sql import DbContainer
            from search import SearchType
            from pyasm.biz import Project
            project = Project.get_by_code(database)
            db_resource = project.get_project_db_resource()
            sql = DbContainer.get(db_resource)

            tmp_dir = Environment.get_tmp_dir()
            schema_path = "%s/cache/create_%s_%s.sql" % \
                (tmp_dir, database, table_name)

            from pyasm.search import CreateTable
            create = CreateTable()
            create.set_table(table_name)

            children = Xml.get_children(node)
            for column_node in children:
                name = Xml.get_attribute(column_node, "name")
                data_type = Xml.get_attribute(column_node, "data_type")
                nullable = Xml.get_attribute(column_node, "nullable")

                # FIXME: make some assumptions.  Not completely correct
                # but will work with most of TACTIC.  Should really
                # introspect databases for this info
                if name == 'id':
                    create.add(name, "serial", primary_key=True )
                else:
                    create.add(name, data_type )

            create.commit(sql)

            # set sequence to the max
            st_obj = SearchType.get(search_type)
            if seq_max:
                st_obj.sequence_setval(seq_max)
            """
            try:
                 f = codecs.open(schema_path, 'r', 'utf-8')
                 table = None
                 lines = f.readlines()
                 statement_str ="".join(lines)
                 from pyasm.search import SearchType, Insert, CreateTable
                 exec(statement_str)
                 # this table comes from exec()
                 table.commit(sql)

                 st_obj = SearchType.get(search_type)
                 if seq_max:
                     SearchType.sequence_setval(search_type, seq_max)


            except IOError, e:
                 print "ERROR: ", str(e)
                 raise TacticException('Cannot locate the file [%s] for restoring the table.' %schema_path) 
            """


            #except SqlException, e:
            #     print "Database ERROR:", str(e)
        
        except TransactionException, e:
            print("Failed to redo '%s' '%s'" % (database, table_name))
            print "Error: ", e

    redo = staticmethod(redo)




class TableDropUndo(Base):

    def log(search_type, database, table):
        # build the sobject xml action description
        transaction = Transaction.get()
        sobject_node = transaction.create_log_node("table")
        Xml.set_attribute(sobject_node,"table",table)
        Xml.set_attribute(sobject_node,"database",database)
        Xml.set_attribute(sobject_node,"search_type", search_type)
        Xml.set_attribute(sobject_node,"action", "drop")

        from search import SearchType
        #st_obj = SearchType.get(search_type)
        #seq_max = st_obj.sequence_nextval()

        seq_max = SearchType.sequence_nextval(search_type)
        if seq_max - 1 > 0:
            Xml.set_attribute(sobject_node,"seq_max", seq_max)
            

    log = staticmethod(log)



    def undo(node):
        try:
            search_type = Xml.get_attribute(node,"search_type")
            database = Xml.get_attribute(node,"database")
            table_name = Xml.get_attribute(node,"table")
            seq_max = Xml.get_attribute(node,"seq_max")

            if database == "" or table_name == "" or not search_type:
                raise TransactionException('Missing search_type, table or database in transaction log')

            # re-enter table
            from sql import DbContainer

            from pyasm.biz import Project
            project = Project.get_by_code(database)
            # FIXME: for now, make database == project
            db_resource = project.get_project_db_resource()
            sql = DbContainer.get(db_resource)

            tmp_dir = Environment.get_tmp_dir()
            schema_path = "%s/cache/drop_%s_%s.sql" % \
                (tmp_dir, database, table_name)

            try:
                 f = codecs.open(schema_path, 'r', 'utf-8')
                 table = None
                 lines = f.readlines()
                 statement_str ="".join(lines)
                 from pyasm.search import SearchType, Insert, DropTable, CreateTable
                 exec(statement_str)
                 # this table comes from exec()
                 table.commit(sql)

                 st_obj = SearchType.get(search_type)
                 if seq_max:
                     SearchType.sequence_setval(search_type, seq_max)
            except IOError, e:
                 print "ERROR: ", str(e)
                 raise TacticException('Cannot locate the file [%s] for restoring the table.' %schema_path) 
            except SqlException, e:
                 print "Database ERROR:", str(e)

         
            # need to keep it around
            """
            if os.path.exists(schema_path):
                os.unlink(schema_path)
            """
        except TransactionException:
            print("Failed to undo '%s' '%s'" % (database, table_name))

    undo = staticmethod(undo)


    def redo(node):
        from sql import SqlException

        try:
            search_type = Xml.get_attribute(node,"search_type")
            database = Xml.get_attribute(node,"database")
            table = Xml.get_attribute(node,"table")

            if database == "" or table == "" or not search_type:
                raise TransactionException('Missing  search_type, table or database in transaction log')



            from sql import DbContainer
            from pyasm.biz import Project
            # remove table
            project = Project.get_by_code(database)
            # FIXME: for now, make database == project
            db_resource = project.get_project_db_resource()
            sql = DbContainer.get(db_resource)

            tmp_dir = Environment.get_tmp_dir()
            schema_path = "%s/cache/drop_%s_%s.sql" % \
                (tmp_dir, database, table)

            if os.path.exists(schema_path):
                os.unlink(schema_path)

            # dump the table to a file and store it in cache
            from sql_dumper import TableSchemaDumper
            dumper = TableSchemaDumper(search_type)
            try:
                dumper.dump_to_tactic(path=schema_path)
            except SqlException, e:
                print "SqlException: ", e
           

            sql.do_update('DROP TABLE "%s"' % table)

        except SqlException, e:
            # This means that the table did not exist, DROP TABLE failed.
            # if there is an sql exception, Note it, but continue.  The
            # undo must complete.
            # TODO: should put this in an error log
            print "SqlException: ", e

        except TransactionException, e:
            print "Failed to redo '%s' '%s'" % (database, table)
    redo = staticmethod(redo)




class AlterTableUndo(Base):

    def log_add(db_resource,table,column,type):
        database = db_resource.get_database()

        # build the sobject xml action description
        transaction = Transaction.get()
        sobject_node = transaction.create_log_node("alter")

        Xml.set_attribute(sobject_node,"action", 'add')

        if isinstance(db_resource, basestring):
            database = db_resource
            Xml.set_attribute(sobject_node,"database",database)
        else:
            # TODO: we need to store more info here?
            databsae = db_resource.get_database()
            Xml.set_attribute(sobject_node,"database",database)


        Xml.set_attribute(sobject_node,"table",table)
        Xml.set_attribute(sobject_node,"column",column)
        Xml.set_attribute(sobject_node,"type",type)
    log_add = staticmethod(log_add)

    def log_modify(database, table, column, type, not_null=False):
        transaction = Transaction.get()
        sobject_node = transaction.create_log_node("alter")

        Xml.set_attribute(sobject_node,"action", 'modify')
        Xml.set_attribute(sobject_node,"database",database)
        Xml.set_attribute(sobject_node,"table",table)
        Xml.set_attribute(sobject_node,"column",column)
        Xml.set_attribute(sobject_node,"to_type",type)
        Xml.set_attribute(sobject_node,"to_not_null", not_null)
        from sql import DbContainer
        from pyasm.biz import Project
        project = Project.get_by_code(database)
        # FIXME: for now, make database == project
        db_resource = project.get_project_db_resource()
        sql = DbContainer.get(db_resource)
        col_dict = sql.get_column_types(table)
        col_type = col_dict.get(column)

        null_dict = sql.get_column_nullables(table)
        from_not_null = not null_dict.get(column)

        Xml.set_attribute(sobject_node,"from_type", col_type)
        Xml.set_attribute(sobject_node,"from_not_null", from_not_null)
    log_modify = staticmethod(log_modify)

    def log_drop(database,table,column):
        # build the sobject xml action description
        transaction = Transaction.get()
        sobject_node = transaction.create_log_node("alter")

        Xml.set_attribute(sobject_node,"action","drop")
        Xml.set_attribute(sobject_node,"database",database)
        Xml.set_attribute(sobject_node,"table",table)
        Xml.set_attribute(sobject_node,"column",column)

       
        from sql import DbContainer
        from pyasm.biz import Project
        project = Project.get_by_code(database)
        # FIXME: for now, make database == project
        db_resource = project.get_project_db_resource()
        sql = DbContainer.get(db_resource)
        #sql = DbContainer.get(database)
        col_dict = sql.get_column_types(table)
        col_type = col_dict.get(column)
        if not col_type:
            from sql import SqlException
            raise SqlException('Column Type is unknown. log_drop() needs to be called before a column is dropped.')
        Xml.set_attribute(sobject_node,"type", col_type)

    log_drop = staticmethod(log_drop)





    def undo(node):
        action = Xml.get_attribute(node,"action")
        if action == 'add':
            AlterTableUndo._drop_column(node)
        elif action == 'drop':
            AlterTableUndo._add_column(node)
        elif action == 'modify':
            AlterTableUndo._modify_column(node, mode='undo')
    undo = staticmethod(undo)
        

    def redo(node):
        action = Xml.get_attribute(node,"action")
        if action == 'add':
            AlterTableUndo._add_column(node)
        elif action == 'drop':
            AlterTableUndo._drop_column(node)
        elif action == 'modify':
            AlterTableUndo._modify_column(node, mode='redo')
    redo = staticmethod(redo)
        


    def _add_column(node):
        statement = None
        try:
            database = Xml.get_attribute(node,"database")
            table = Xml.get_attribute(node,"table")
            column = Xml.get_attribute(node,"column")
            type = Xml.get_attribute(node,"type")

            if database == "" or table == "":
                raise TransactionException()

            # add column
            from sql import DbContainer
            from pyasm.biz import Project
            project = Project.get_by_code(database)
            db_resource = project.get_project_db_resource()
            sql = DbContainer.get(db_resource)
            # this may not return the type exacty like before like varchar is in place of
            # varchar(256) due to the column type returned from the sql impl
            statement = 'ALTER TABLE "%s" ADD COLUMN "%s" %s' % (table,column,type)
            sql.do_update(statement)


        except TransactionException:
            print("Failed to add column '%s.%s'" % (table, column))
        except Exception, e:
            print "Error: [%s]" % e.__str__()
            if statement:
                print("Failed to execute: %s in [%s]" % (statement, database))
            raise

    _add_column = staticmethod(_add_column)




    def _drop_column(node):
        statement = None
        try:
            database = Xml.get_attribute(node,"database")
            table = Xml.get_attribute(node,"table")
            column = Xml.get_attribute(node,"column")

            if database == "" or table == "" or type == "":
                raise TransactionException()

            # drop column
            from sql import DbContainer
            from pyasm.biz import Project
            project = Project.get_by_code(database)
            # FIXME: for now, make database == project
            db_resource = project.get_project_db_resource()
            sql = DbContainer.get(db_resource)

            statement = 'ALTER TABLE "%s" DROP COLUMN "%s"' % (table,column)
            sql.do_update(statement)

        except TransactionException:
            print("Failed to drop column '%s.%s'" % (table, column))
        except Exception, e:
            print(e.__str__())
            if statement:
                print("Failed to execute: %s" % statement)
            else:
                raise


    _drop_column = staticmethod(_drop_column)

    def _modify_column(node, mode=None):
        try:
            database = Xml.get_attribute(node,"database")
            table = Xml.get_attribute(node,"table")
            column = Xml.get_attribute(node,"column")
            from_not_null = Xml.get_attribute(node,"from_not_null")
            to_not_null = Xml.get_attribute(node,"to_not_null")
            if mode=='undo':
                type = Xml.get_attribute(node,"from_type")
                not_null = from_not_null
            else:
                type = Xml.get_attribute(node,"to_type")
                not_null = to_not_null

            if database == "" or table == "":
                raise TransactionException()

            from search import DbContainer
            sql = DbContainer.get(database)
            # if not null constraint did not change, do not touch it
            if from_not_null == to_not_null:
                is_not_null = None
            else:
                is_not_null = not_null=='True'
            sql.modify_column(table, column, type, is_not_null)


        except TransactionException:
            print("Failed to modify column '%s.%s'" % (table, column))
        except Exception, e:
            print(e.__str__())
            print("Failed to execute sql.modify_column()")

    _modify_column = staticmethod(_modify_column)


