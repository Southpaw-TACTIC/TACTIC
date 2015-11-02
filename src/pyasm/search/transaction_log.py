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

__all__ = ['TransactionLog']

from pyasm.common import *
from search import SObjectUndo, SObject, Search, SObjectFactory, SearchType, SearchException, SqlException
from transaction import FileUndo, TableUndo, TableDropUndo, AlterTableUndo
from sobject_log import SObjectLog

class TransactionLog(SObject):
    SEARCH_TYPE = "sthpw/transaction_log"


    def get_code_key(my):
        return "TRANSACTION"

    def undo(my, ignore_files=False):
        Container.put("is_undo", True)

        ticket = my.get_value("ticket", no_exception=True)

        try:

            xml = my.get_xml_value("transaction")

            nodes = xml.get_nodes("transaction/*")
            nodes.reverse()

            # if there is an error, report it but do what you can
            for node in nodes:
                node_name = xml.get_node_name(node)
                if node_name == "sobject":
                    SObjectUndo.undo(node)
                elif not ignore_files and node_name == "file":
                    FileUndo.undo(node, ticket)
                elif node_name == "table":
                    action = Xml.get_attribute(node,"action")
                    if action == 'drop':
                        TableDropUndo.undo(node)
                    else:
                        TableUndo.undo(node)
              
                elif node_name == "alter":
                    AlterTableUndo.undo(node)

        finally:
            Container.put("is_undo", False)
    
    def redo(my, ignore=[], base_dir=""):
        Container.put("is_undo", True)

        # get some values from transaction log
        timestamp = my.get_value("timestamp")


        ticket = my.get_value("ticket", no_exception=True)
        try:

            xml = my.get_xml_value("transaction")

            nodes = xml.get_nodes("transaction/*")
            for node in nodes:
                node_name = xml.get_node_name(node)
                if node_name == "sobject":
                    xml.set_attribute(node, "timestamp", timestamp)
                    SObjectUndo.redo(node)

                elif node_name == "file" and "file" not in ignore:
                    FileUndo.redo(node, ticket, base_dir=base_dir)
                elif node_name == "table":
                    action = Xml.get_attribute(node,"action")
                    if action == 'drop':
                        TableDropUndo.redo(node)
                    else:
                        TableUndo.redo(node)
                elif node_name == "alter":
                    AlterTableUndo.redo(node)
        finally:
            Container.put("is_undo", False)



    def trigger_remote_sync(my):
        # Trigger remote synchronization

        # This only gets set on a "start" call from client API.  The
        # remote sync job will only get registered is a "finish" is called
        if my.get_value("state") == "start":
            return

        from tactic.command.run_transaction_cmd import TransactionQueueAppendCmd
        cmd = TransactionQueueAppendCmd()
        input = {
            'search_type': 'sthpw/transaction_log',
            'sobject': my
        }
        cmd.input = input
        cmd.execute()


    def trigger_remote_undo(my):
        # Trigger remote synchronization

        if my.get_value("state") == "start":
            return

        from tactic.command.run_transaction_cmd import TransactionQueueAppendCmd
        cmd = TransactionQueueAppendCmd()
        input = {
            'search_type': 'sthpw/transaction_log',
            'sobject': my,
            'mode': 'undo'
        }
        cmd.input = input
        cmd.execute()




    # static functions
    def create(cls, command, transaction_data, description, title='', state=None, keywords=None):
        user_name = Environment.get_user_name()
        #namespace = Environment.get_env_object().get_context_name()
        from pyasm.biz import Project
        namespace = Project.get_global_project_code()

        # TODO: need to add a ticket column to the transaction_log table
        security = Environment.get_security()
        ticket = security.get_ticket_key()

        #transaction_data = transaction_data.replace("\\", "\\\\")

        length_before = len(transaction_data)
        cutoff = 10*1024
        if length_before > cutoff:
            import zlib, binascii
            transaction_data = Common.process_unicode_string(transaction_data)
            ztransaction_data = binascii.hexlify(zlib.compress(transaction_data))
            ztransaction_data = "zlib:%s" % ztransaction_data
            length_after = len(ztransaction_data)
            print "transaction log compress: ", "%s%%" % int(float(length_after)/float(length_before)*100), "[%s] to [%s]" % (length_before, length_after)
        else:
            ztransaction_data = transaction_data

        # a new entry deletes all redos for that user
        TransactionLog.delete_all_redo()


        log = SObjectFactory.create("sthpw/transaction_log")
        log.set_value("login", user_name)
        log.set_value("command", command)
        log.set_value("transaction", ztransaction_data)
        log.set_value("title", title)
        log.set_value("description", description)
        log.set_value("type", "undo")
        log.set_value("namespace", namespace)
        log.set_value("ticket", ticket)
        if state:
            log.set_value("state", state)

        if keywords:
            log.set_value("keywords", keywords)

        server = Config.get_value("install", "server")
        if server:
            log.set_value("server_code", server)

        log.commit(triggers=False)



        # FIXME:
        # only do an sobject log before the cutoff ... above this it gets
        # very slow.  Need a way of doing very fast inserts
        if length_before <= cutoff:
            cls.create_sobject_log(log, transaction_data)
        return log
    create = classmethod(create)


    def create_sobject_log(cls, log, transaction_data=None):

        if not transaction_data:
            transaction_data = log.get_value("transaction")

        # log a reference to each sobject affected
        already_logged = {}
        xml = Xml()
        xml.read_string(transaction_data)
        nodes = xml.get_nodes("transaction/*")


        # list of sobjects not logged
        not_logged = set([
            'sthpw/transaction_log',
            'sthpw/clipboard',
            'sthpw/sobject_log',
            'sthpw/file',
            'sthpw/message',
            'sthpw/message_log',
        ])

        find_parent = set([
            'sthpw/snapshot',
            'sthpw/note',
            'sthpw/task'
        ])


        for node in nodes:
            node_name = xml.get_node_name(node)
            if node_name == "sobject":
                search_type = Xml.get_attribute(node,"search_type")
                search_type_obj = SearchType.get(search_type)


                if search_type_obj.get_base_key() in not_logged:
                    continue


                search_id = Xml.get_attribute(node,"search_id")
                search_code = Xml.get_attribute(node,"search_code")

                if search_code:
                    search_key = "%s?code=%s" % (search_type, search_code)
                else:
                    search_key = "%s|%s" % (search_type, search_id)


                if already_logged.get(search_key):
                    continue
                already_logged[search_key] = True

                # delete items are not presently logged ...
                # TODO: maybe they should be
                action = Xml.get_attribute(node,"action")
                if action == "delete":
                    continue

                if search_code:
                    sobject = Search.get_by_code(search_type, search_code)
                else:
                    sobject = Search.get_by_id(search_type, search_id)


                if sobject:
                    SObjectLog.create(sobject, log, action)
                else:
                    # record has been deleted
                    if search_code:
                        print("Skipped SObject log creation for [%s?code=%s]" %(search_type, search_code))
                    else:
                        print("Skipped SObject log creation for [%s|%s]" %(search_type, search_id))

                if search_type_obj.get_base_key() in find_parent:
                    try:
                        if sobject:
                            sobject = sobject.get_parent()
                    except (SearchException, SqlException):
                        # don't worry if this parent can't be found.
                        pass
                    if sobject:
                        SObjectLog.create(sobject, log, "child_%s" % action)

    create_sobject_log = classmethod(create_sobject_log)



    def get_last(type=None):
        #namespace = SearchType.get_project()
        from pyasm.biz import Project
        namespace = Project.get_project_code()

        user_name = Environment.get_user_name()
        search = Search("sthpw/transaction_log")
        search.add_filter("login", user_name)
        search.add_filter("namespace", namespace)
        if type:
            search.add_filter("type", type)
        search.add_order_by("timestamp desc")
        sobject = search.get_sobject()
        return sobject
    get_last = staticmethod(get_last)

    def get_next_redo():
        from pyasm.biz import Project
        namespace = Project.get_project_code()

        user_name = Environment.get_user_name()
        search = Search("sthpw/transaction_log")
        search.add_filter("login", user_name)
        search.add_filter("namespace", namespace)
        
        search.add_filter("type", "redo")
        search.add_order_by("timestamp")
        sobject = search.get_sobject()
        return sobject
    get_next_redo = staticmethod(get_next_redo)



    def get(cls, user_name=None, namespace=None, time_interval=None):
        search = Search("sthpw/transaction_log")

        if user_name:
            search.add_filter("login", user_name)

        if namespace:
            search.add_filter("namespace", namespace)

        if time_interval and time_interval != 'NONE':
            from sql import Select
            search.add_where(Select.get_interval_where(time_interval))

        search.add_order_by("timestamp desc")
        search.set_limit(100)
        sobjects = search.do_search()
        return sobjects
    get = classmethod(get)


    def delete_all_redo():
        user_name = Environment.get_user_name()

        search = Search("sthpw/transaction_log")
        search.add_order_by("timestamp")
        search.add_filter("type", "redo")
        search.add_filter("login", user_name)
        transaction_logs = search.do_search()

        for transaction_log in transaction_logs:
            transaction_log.delete()

    delete_all_redo = staticmethod(delete_all_redo)









