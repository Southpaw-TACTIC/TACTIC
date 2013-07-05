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

    def get_command(my):
        return my.command

    def get_search_columns():
        return ["description", 'login', 'state']
    get_search_columns = staticmethod(get_search_columns)


    def get_defaults(my):
        user_name = Environment.get_user_name()
        return { "login": user_name }


    def execute(my):
        my.command = None
        try:
            # reload the module
            #class_name = queue.get_value("command")
            #exec("reload(%s)" % class_name)

            my.command = pickle.loads( my.get_value("serialized") )
        except Exception, e:
            print "Error: ", e.__str__()
            DbContainer.remove("sthpw")
        else:
            # execute the command
            print "executing: ", my.get_id(), my.command
            try:
                # refresh the environment and execute
                Command.execute_cmd(my.command)
            except Exception, e:
                ExceptionLog.log(e)
                print "Error: ", e.__str__()
                my.set_value("state", "error")

                description = my.get_value("description")
                my.set_value("description", "%s : %s" % \
                    (description, e.__str__()) )
                my.commit()
            else:
                print "setting to done"
                my.set_value("state", "done")
                my.commit()



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





    def start(my):
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

        queue.set_value("login". Environment.get_user_name())
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


