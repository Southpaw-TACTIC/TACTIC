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

__all__ = ["UndoCmd", "RedoCmd"]


from pyasm.common import *
from pyasm.biz import Project
from pyasm.search import *
from pyasm.security import Sudo

from .command import *

class UndoCmd(Command):

    def __init__(self, ignore_files=False, is_sync=True, transaction_log=None):
        super(UndoCmd,self).__init__()
        self.transaction_log = transaction_log
        self.ignore_files = ignore_files
        self.is_sync = is_sync


    def get_title(self):
        return "Undo"

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)



    def check(self):
        return True

    def set_transaction_log(self, transaction_log):
        '''manually set the translation log'''
        self.transaction_log = transaction_log

    def set_transaction_id(self, transaction_id):
        '''manually set the translation id'''
        sudo = Sudo()
        try:
            self.transaction_log = Search.get_by_id("sthpw/transaction_log", transaction_id)
        finally:
            sudo.exit()

        if not self.transaction_log:
            raise CommandException("Transaction with id [%s] does not exist" % transaction_id)


    def set_transaction_code(self, transaction_code):
        '''manually set the translation code'''
        self.transaction_log = Search.get_by_code("sthpw/transaction_log", transaction_code)
        if not self.transaction_log:
            raise CommandException("Transaction with code [%s] does not exist" % transaction_code)




    def execute(self):
        if not self.transaction_log:
            search = Search("sthpw/transaction_log")
            search.add_filter("type", "undo")

            # get the current project.  If the project is admin, then undo
            # works differently
            project = Project.get_global_project_code()
            assert project
            search.add_filter("namespace", project)

            user = Environment.get_user_name()
            assert user
            search.add_filter("login", user)

            search.add_order_by("timestamp desc")

            search.add_limit(1)
            self.transaction_log = search.get_sobject()

        if not self.transaction_log:
            print("WARNING: No transaction log found for undo")
            return CommandExitException()

        self.transaction_log.undo(ignore_files=self.ignore_files)

        self.transaction_log.set_value("type", "redo")
        self.transaction_log.commit()

        # undo triggers a special sync
        # if this is a sync undo, then do not propgate remote undos
        if not self.is_sync:
            self.transaction_log.trigger_remote_undo()




class RedoCmd(Command):

    def __init__(self,**kwargs):
        super(RedoCmd,self).__init__()
        self.kwargs = kwargs
        self.transaction_log = self.kwargs.get("transaction_log")
        self.ignore = self.kwargs.get("ignore")
        if not self.ignore:
            self.ignore = []

    def get_title(self):
        return "Redo"

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)


    def check(self):
        #from pyasm.web import WebContainer
        #web = WebContainer.get_web()
        #if web.get_form_value("Redo") != "":
        return True

    def set_transaction_log(self, transaction_log):
        '''manually set the translation log to undo'''
        self.transaction_log = transaction_log


    def get_transaction_log(self):
        '''get the transaction log'''
        return self.transaction_log



    def set_transaction_id(self, transaction_id):
        '''manually set the translation id'''
        self.transaction_log = Search.get_by_id("sthpw/transaction_log", transaction_id)
        if not self.transaction_log:
            raise CommandException("Transaction with id [%s] does not exist" % transaction_id)


    def set_transaction_code(self, transaction_code):
        '''manually set the translation code'''
        self.transaction_log = Search.get_by_code("sthpw/transaction_log", transaction_code)
        if not self.transaction_log:
            raise CommandException("Transaction with code [%s] does not exist" % transaction_code)




    def execute(self):
        import time
        start = time.time()

        security = Environment.get_security()
        ticket = security.get_ticket_key()

        if not self.transaction_log:
            search = Search("sthpw/transaction_log")
            search.add_filter("type", "redo")

            # get the current project
            project = Project.get_global_project_code()
            search.add_filter("namespace", project)

            user = Environment.get_user_name()
            search.add_filter("login", user)

            search.add_order_by("timestamp")
            search.add_limit(1)

            self.transaction_log = search.get_sobject()

        if not self.transaction_log:
            return CommandExitException()

        base_dir = self.kwargs.get("base_dir")

        self.transaction_log.redo(ignore=self.ignore, base_dir=base_dir)
        self.transaction_log.set_value("type", "undo")
        self.transaction_log.commit()

        # get the transaction and set it to not record this transaction
        transaction = Transaction.get()
        transaction.set_record(False)

        # update the change timestamps
        transaction.update_change_timestamps(self.transaction_log)

        print("RedoCmd: ", time.time() - start)
        print




