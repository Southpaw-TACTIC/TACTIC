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


# DEPRECATED: now in tactic.ui.command.queue.py


__all__ = ['Queue']


from pyasm.common import Base, Container, Environment
from pyasm.security import Batch
from pyasm.command import Command
from pyasm.search import *
from pyasm.biz import Project
import pickle, time, thread


# dormant time between checking requests, in seconds
SLEEP_TIME = 5


class Queue(SObject):

    SEARCH_TYPE = "sthpw/queue"

    def get_command(self):
        return self.command

    def get_search_columns():
        return ["description", 'login', 'state']
    get_search_columns = staticmethod(get_search_columns)


    def get_defaults(self):
        user_name = Environment.get_user_name()
        return { "login": user_name }


    def execute(self):
        self.command = None
        try:
            # reload the module
            #class_name = queue.get_value("command")
            #exec("reload(%s)" % class_name)

            self.command = pickle.loads( self.get_value("serialized") )
        except Exception, e:
            print "Error: ", e.__str__()
            DbContainer.remove("sthpw")
        else:
            # execute the command
            print "executing: ", self.get_id(), self.command
            try:
                # refresh the environment and execute
                Command.execute_cmd(self.command)
            except Exception, e:
                ExceptionLog.log(e)
                print "Error: ", e.__str__()
                self.set_value("state", "error")

                description = self.get_value("description")
                self.set_value("description", "%s : %s" % \
                    (description, e.__str__()) )
                self.commit()
            else:
                print "setting to done"
                self.set_value("state", "done")
                self.commit()



    def get_next_job(queue_type=None):

        sql = DbContainer.get("sthpw")

        # get the entire queue
        search = Search("sthpw/queue")
        if queue_type:
            search.add_filter("queue", queue_type)
        search.add_filter("state", "pending")
        search.add_order_by("timestamp")
        search.add_limit("10")
        queues = search.get_sobjects()
        queue_id = 0

        for queue in queues:

            queue_id = queue.get_id()

            # attempt to lock this queue
            # have to do this manually
            update = "UPDATE queue SET state = 'locked' where id = '%s' and state = 'pending'" % queue_id

            sql.do_update(update)
            row_count = sql.get_row_count()

            if row_count == 1:
                break
            else:
                queue_id = 0

        if queue_id:
            queue = Search.get_by_id("sthpw/queue", queue_id)
            return queue
        else:
            return None

    get_next_job = staticmethod(get_next_job)



    def get_job(queue_type=None, job_search_type="sthpw/queue",server_code=None):
        '''This will get the next job if no other job is running.  It
        assumes that only on job can be running at once.
        '''

        sql = DbContainer.get("sthpw")

        search_type_obj = SearchType.get(job_search_type)
        table = search_type_obj.get_table()

        # get the entire queue
        search = Search(job_search_type)
        if queue_type:
            search.add_filter("queue", queue_type)
        if server_code:
            search.add_filter("server_code", server_code)
        search.add_filters("state", ["pending","locked","error"])
        search.add_order_by("timestamp")
        search.add_limit("10")
        queues = search.get_sobjects()
        queue_id = 0

        if not queues:
            return

        # if the first status is locked, then exit
        first_queue = queues[0]
        first_status = first_queue.get_value("state")
        if first_status in ['locked']:
            return
        if first_status in ['error']:
            #print "Found error on next job, cannot proceed ..."
            return


        # Iterate through the jobs
        for queue in queues:

            queue_id = queue.get_id()

            # attempt to lock this queue
            # have to do this manually
            update = "UPDATE %s SET state = 'locked' where id = '%s' and state = 'pending'" % (table, queue_id)

            sql.do_update(update)
            row_count = sql.get_row_count()

            if row_count == 1:
                break
            else:
                queue_id = 0

        if queue_id:
            queue = Search.get_by_id(job_search_type, queue_id)
            return queue
        else:
            return None

    get_job = staticmethod(get_job)




    def start(self):
        print "starting thread: ", thread.get_ident()
        thread.start_new_thread(Queue._start, ("Queue", 1))


    def _start(name, i):

        Batch()

        # loop continuously
        while 1:

            queue = Queue.get_next_job()

            if queue:
                queue.execute()

            else:
                print "Queue: No jobs available"

                # go to sleep for a while
                DbContainer.remove("sthpw")
                time.sleep(SLEEP_TIME)

    _start = staticmethod(_start)




    def create(sobject, queue_type, priority, description, command=None):

        queue = SObjectFactory.create("sthpw/queue")
        queue.set_value("project_code", Project.get_project_name())
        queue.set_sobject_value(sobject)
        queue.set_value("queue", queue_type)
        queue.set_value("state", "pending")

        queue.set_value("login", Environment.get_user_name())
        if command:
            pickled = pickle.dumps(command)
            queue.set_value("command", command.__class__.__name__)
            queue.set_value("serialized", pickled)

        queue.set_value("priority", priority)
        queue.set_value("description", description)

        queue.set_user()
        queue.commit()

        return queue

    create = staticmethod(create)


