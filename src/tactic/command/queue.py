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
__all__ = ['JobTask', 'Queue']

import tacticenv

from pyasm.security import Batch
from pyasm.common import Common, Config, Container, Environment, jsonloads, jsondumps, TacticException
from pyasm.biz import Project
from pyasm.search import Search, SearchType, DbContainer, Transaction
from pyasm.command import Command
from tactic.command import Scheduler, SchedulerTask

import os



class Queue:

    def get_next_job(job_search_type="sthpw/queue", queue_type=None, server_code=None):

        sql = DbContainer.get("sthpw")

        search_type_obj = SearchType.get(job_search_type)
        table = search_type_obj.get_table()

        # get the entire queue
        search = Search(job_search_type)
        if queue_type:
            search.add_filter("queue", queue_type)
        if server_code:
            search.add_filter("server_code", server_code)
        search.add_filter("state", "pending")

        search.add_order_by("priority")
        search.add_order_by("timestamp")


        chunk = 10
        search.add_limit(chunk)

        queues = search.get_sobjects()
        queue_id = 0

        for queue in queues:

            queue_id = queue.get_id()

            # attempt to lock this queue
            # have to do this manually
            update = """UPDATE "%s" SET state = 'locked' where id = '%s' and state = 'pending'""" % (table, queue_id)

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

    get_next_job = staticmethod(get_next_job)


    def add(command, kwargs, queue_type, priority, description, message_code=None):

        queue = SearchType.create("sthpw/queue")
        queue.set_value("project_code", Project.get_project_code())
        #queue.set_sobject_value(sobject)

        if not queue_type:
            queue_type = "default"
        queue.set_value("queue", queue_type)

        queue.set_value("state", "pending")

        queue.set_value("login", Environment.get_user_name())

        queue.set_value("command", command)
        data = jsondumps(kwargs)
        queue.set_value("data", data)

        if message_code:
            queue.set_value("message_code", message_code)


        if not priority:
            priority = 9999
        queue.set_value("priority", priority)

        if description:
            queue.set_value("description", description)

        queue.set_user()
        queue.commit()

        return queue

    add = staticmethod(add)






# create a task from the job
class JobTask(SchedulerTask):

    def __init__(self, **kwargs):

        #print("JobTask: init")
        self.job = None
        self.jobs = []

        self.check_interval = kwargs.get("check_interval")
        if not self.check_interval:
            self.check_interval = 1

        self.jobs_completed = 0
        self.max_jobs_completed = kwargs.get("max_jobs_completed")
        if not self.max_jobs_completed:
            self.max_jobs_completed = -1

        self.max_jobs = 20

        self.queue_type = kwargs.get("queue")
        self.pid_path = kwargs.get("pid_path")
        super(JobTask, self).__init__()


    def get_check_interval(self):
        return self.check_interval


    def set_check_interval(self, interval):
        self.check_interval = interval

    def get_process_key(self):
        import platform;
        host = platform.uname()[1]
        pid = os.getpid()
        return "%s:%s" % (host, pid)


    def get_job_search_type(self):
        return "sthpw/queue"


    def get_next_job(self, queue_type=None):
        return Queue.get_next_job(queue_type=queue_type)




    def cleanup_db_jobs(self):
        # clean up the jobs that this host previously had

        process_key = self.get_process_key()
        job_search = Search(self.get_job_search_type())
        job_search.add_filter("host", process_key)
        self.jobs = job_search.get_sobjects()
        self.cleanup()



    def cleanup(self, count=0):
        if count >= 3:
            return
        try:
            for job in self.jobs:
                # reset all none complete jobs to pending

                current_state = job.get_value("state")
                if current_state not in ['locked']:
                    continue

                #print("setting to pending")
                job.set_value("state", "pending")
                job.set_value("host", "")
                job.commit()

            self.jobs = []

        except Exception as e:
            print("Exception: ", e.message)
            count += 1
            self.cleanup(count)
            


    def execute(self):

        import atexit
        import time
        atexit.register( self.cleanup )
        while 1:
            time.sleep(20)

            pid_path = self.pid_path
            if pid_path and os.path.exists(pid_path):
                os.utime(pid_path, None)

            self.check_existing_jobs()
            self.check_new_job()
            time.sleep(self.check_interval)
            DbContainer.close_thread_sql()

            if self.max_jobs_completed != -1 and self.jobs_completed > self.max_jobs_completed:
                Common.restart()
                while 1:
                    print("Waiting to restart...")
                    time.sleep(1)



    def check_existing_jobs(self):
        self.keep_jobs = []
        for job in self.jobs:
            job_code = job.get_code()
            search = Search(self.get_job_search_type())
            search.add_filter("code", job_code)
            job = search.get_sobject()

            if not job:
                print("Cancel ....")
                scheduler = Scheduler.get()
                scheduler.cancel_task(job_code)
                continue

            state = job.get_value("state")
            if state == 'cancel':
                print("Cancel task [%s] ...." % job_code)
                scheduler = Scheduler.get()
                scheduler.cancel_task(job_code)

                job.set_value("state", "terminated")
                job.commit()
                continue

            self.keep_jobs.append(job)

        self.jobs = self.keep_jobs



    def check_new_job(self, queue_type=None):


        num_jobs = len(self.jobs)
        if num_jobs >= self.max_jobs:
            print("Already at max jobs [%s]" % self.max_jobs)
            return
      
        self.job = self.get_next_job(queue_type)
        if not self.job:
            return

		
        # set the process key
        process_key = self.get_process_key()
        self.job.set_value("host", process_key)
        self.job.commit()

        self.jobs.append(self.job)

        # get some info from the job
        command = self.job.get_value("command")
        job_code = self.job.get_value("code")

        try: 
            kwargs = self.job.get_json_value("data")
        except:
            try:
                # DEPRECATED
                kwargs = self.job.get_json_value("serialized")
            except:
                kwargs = {}
        if not kwargs:
            kwargs = {}

        login = self.job.get_value("login")
        script_path = self.job.get_value("script_path", no_exception=True)

        project_code = self.job.get_value("project_code")

        if script_path:
            command = 'tactic.command.PythonCmd'

            folder = os.path.dirname(script_path)
            title = os.path.basename(script_path)

            search = Search("config/custom_script")
            search.add_filter("folder", folder)
            search.add_filter("title", title)
            custom_script = search.get_sobject()
            script_code = custom_script.get_value("script")

            kwargs['code'] = script_code



        # add the job to the kwargs
        kwargs['job'] = self.job

        #print("command: ", command)
        #print("kwargs: ", kwargs)


        # Because we started a new thread, the environment may not
        # yet be initialized
        try:
            from pyasm.common import Environment
            Environment.get_env_object()
        except:
            # it usually is run at the very first transaction
            Batch()
        Project.set_project(project_code)


        queue = self.job.get_value("queue", no_exception=True)
        queue_type = 'repeat'

        stop_on_error = False

        print("Running job: ", self.job.get_value("code") )

        if queue_type == 'inline':

            cmd = Common.create_from_class_path(command, kwargs=kwargs)
            try:
                Container.put(Command.TOP_CMD_KEY, None)
                Container.put(Transaction.KEY, None)
                Command.execute_cmd(cmd)

                # set job to complete
                self.job.set_value("state", "complete")
            except Exception as e:
                self.job.set_value("state", "error")

            self.job.commit()
            self.jobs.remove(self.job)
            self.job = None

            self.jobs_completed += 1


        elif queue_type == 'repeat':

           
            attempts = 0
            max_attempts = 3
            retry_interval = 5
            Container.put(Transaction.KEY, None)
            while 1:
		    
                try:
                    cmd = Common.create_from_class_path(command, kwargs=kwargs)
                    
                    Container.put(Command.TOP_CMD_KEY, None)
                    
                    Command.execute_cmd(cmd)
                    #cmd.execute()

                    # set job to complete
                    self.job.set_value("state", "complete")
                    break
                except TacticException as e:

                    # This is an error on this server, so just exit
                    # and don't bother retrying
                    print("Error: ", e)
                    self.job.set_value("state", "error")
                    break


                except Exception as e:
                    if stop_on_error:
                        raise
                    print("WARNING in Queue: ", e)
                    import time
                    time.sleep(retry_interval)
                    attempts += 1

                    if attempts >= max_attempts:
                        print("ERROR: reached max attempts")
                        self.job.set_value("state", "error")
                        break

                    print("Retrying [%s]...." % attempts)

            self.job.commit()
            self.jobs.remove(self.job)
            self.job = None

            self.jobs_completed += 1


        else:
            class ForkedTask(SchedulerTask):
                def __init__(self, **kwargs):
                    super(ForkedTask, self).__init__(**kwargs)
                def execute(self):
                    # check to see the status of this job
                    """
                    job = self.kwargs.get('job')
                    job_code = job.get_code()
                    search = Search("sthpw/queue")
                    search.add_filter("code", job_code)
                    self.kwargs['job'] = search.get_sobject()

                    if not job:
                        print("Cancelling ...")
                        return

                    state = job.get_value("state")
                    if state == "cancel":
                        print("Cancelling 2 ....")
                        return
                    """

                    subprocess_kwargs = {
                        'login': login,
                        'project_code': project_code,
                        'command': command,
                        'kwargs': kwargs
                    }
                    subprocess_kwargs_str = jsondumps(subprocess_kwargs)
                    install_dir = Environment.get_install_dir()
                    python = Config.get_value("services", "python")
                    if not python:
                        python = 'python'
                    args = ['%s' % python, '%s/src/tactic/command/queue.py' % install_dir]
                    args.append(subprocess_kwargs_str)

                    import subprocess
                    p = subprocess.Popen(args)

                    DbContainer.close_thread_sql()

                    return

                    # can't use a forked task ... need to use a system call
                    #Command.execute_cmd(cmd)

            # register this as a forked task
            task = ForkedTask(name=job_code, job=self.job)
            scheduler = Scheduler.get()
            scheduler.start_thread()

            # FIXME: the queue should not be inline
            if queue == 'interval':

                interval = self.job.get_value("interval")
                if not interval:
                    interval = 60

                scheduler.add_interval_task(task, interval=interval,mode='threaded')

            else:
                scheduler.add_single_task(task, mode='threaded')



    def start(**kwargs):
         
        scheduler = Scheduler.get()
        scheduler.start_thread()
        task = JobTask(**kwargs)
        task.cleanup_db_jobs()

        scheduler.add_single_task(task, mode='threaded', delay=1)
    start = staticmethod(start)



def run_batch(kwargs):
    command = k.get("command")
    kwargs = k.get("kwargs")
    login = k.get("login")
    project_code = k.get("project_code")
    site = k.get("site")

    from pyasm.security import Batch
    Batch(site=site, project_code=project_code, login_code=login)

    cmd = Common.create_from_class_path(command, kwargs=kwargs)
    Command.execute_cmd(cmd)



__all__.append("QueueTest")

class QueueTest(Command):
    def execute(self):
        # this command has only a one in 10 chance of succeeding
        import random
        value = random.randint(0, 10)
        if value != 5:
            sdaffsfda




if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    k = args[0]
    k = jsonloads(k)
    run_batch(k)

