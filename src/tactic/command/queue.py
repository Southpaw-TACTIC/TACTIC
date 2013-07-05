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
import tacticenv

from pyasm.security import Batch
from pyasm.common import Common, Config, Environment, jsonloads, jsondumps
from pyasm.biz import Project
from pyasm.search import Search, DbContainer
from pyasm.command import Command
from tactic.command import Scheduler, SchedulerTask

import os

# create a task from the job
class JobTask(SchedulerTask):

    def __init__(my):
        #print "JobTask: init"
        my.job = None
        my.jobs = []


        my.check_interval = 5
        my.max_jobs = 2


        super(JobTask, my).__init__()


    def set_check_interval(my, interval):
        my.check_interval = interval

    def get_process_key(my):
        host = "192.168.109.132"

        import platform;
        host = platform.uname()[1]
        pid = os.getpid()
        return "%s:%s" % (host, pid)


    def cleanup_db_jobs(my):
        # clean up the jobs that this host previously had

        process_key = my.get_process_key()

        job_search = Search("sthpw/queue")
        job_search.add_filter("host", process_key)
        my.jobs = job_search.get_sobjects()
        my.cleanup()



    def cleanup(my, count=0):
        #print "Cleaning up ..."
        if count >= 3:
            return
        try:
            for job in my.jobs:
                # reset all of the jobs to pending
                job.set_value("state", "pending")
                job.set_value("host", "")
                job.commit()

            my.jobs = []

        except Exception, e:
            print "Exception: ", e.message
            count += 1
            my.cleanup(count)
            


    def execute(my):

        import atexit
        import time
        atexit.register( my.cleanup )

        while 1:
            my.check_existing_jobs()
            my.check_new_job()
            time.sleep(my.check_interval)
            DbContainer.close_thread_sql()


    def check_existing_jobs(my):
        my.keep_jobs = []
        for job in my.jobs:
            job_code = job.get_code()
            search = Search("sthpw/queue")
            search.add_filter("code", job_code)
            job = search.get_sobject()

            if not job:
                print "Cancel ...."
                scheduler = Scheduler.get()
                scheduler.cancel_task(job_code)
                continue

            state = job.get_value("state")
            if state == 'cancel':
                print "Cancel task [%s] ...." % job_code
                scheduler = Scheduler.get()
                scheduler.cancel_task(job_code)

                job.set_value("state", "terminated")
                job.commit()
                continue

            my.keep_jobs.append(job)

        my.jobs = my.keep_jobs



    def check_new_job(my):

        num_jobs = len(my.jobs)
        if num_jobs >= my.max_jobs:
            #print "Already at max jobs [%s]" % my.max_jobs
            return


        from pyasm.prod.queue import Queue
        my.job = Queue.get_next_job()
        if not my.job:
            return

        queue = my.job.get_value("queue")

        # set the process key
        process_key = my.get_process_key()
        my.job.set_value("host", process_key)
        my.job.commit()

        my.jobs.append(my.job)

        # get some info from the job
        command = my.job.get_value("command")
        job_code = my.job.get_value("code")
        #print "Grabbing job [%s] ... " % job_code

        try: 
            data = my.job.get_value("serialized")
            if data:
                kwargs = eval( my.job.get_value("serialized") )
            else:
                kwargs = {}
        except:
            kwargs = {}


        interval = my.job.get_value("interval")
        if not interval:
            interval = 60

        project_code = my.job.get_value("project_code")
        login = my.job.get_value("login")
        queue = my.job.get_value("queue")
        script_path = my.job.get_value("script_path", no_exception=True)



        if script_path:
            Project.set_project(project_code)
            command = 'tactic.command.PythonCmd'

            folder = os.path.dirname(script_path)
            title = os.path.basename(script_path)

            search = Search("config/custom_script")
            search.add_filter("folder", folder)
            search.add_filter("title", title)
            custom_script = search.get_sobject()
            script_code = custom_script.get_value("script")

            kwargs = {
               'code': script_code,
            }

        print "command: ", command
        print "kwargs: ", kwargs


        if queue != 'interval':
            cmd = Common.create_from_class_path(command, kwargs=kwargs)
            Command.execute_cmd(cmd)

        else:
            class ForkedTask(SchedulerTask):
                def __init__(my, **kwargs):
                    super(ForkedTask, my).__init__(**kwargs)
                def execute(my):
                    # check to see the status of this job
                    """
                    job = my.kwargs.get('job')
                    job_code = job.get_code()
                    search = Search("sthpw/queue")
                    search.add_filter("code", job_code)
                    my.kwargs['job'] = search.get_sobject()

                    if not job:
                        print "Cancelling ..."
                        return

                    state = job.get_value("state")
                    if state == "cancel":
                        print "Cancelling 2 ...."
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
            task = ForkedTask(name=job_code, job=my.job)
            scheduler = Scheduler.get()
            scheduler.start_thread()
            scheduler.add_interval_task(task, interval=interval,mode='threaded')


    def start():

        scheduler = Scheduler.get()
        scheduler.start_thread()

        task = JobTask()
        task.cleanup_db_jobs()

        scheduler.add_single_task(task, mode='threaded')
    start = staticmethod(start)



def run_batch(kwargs):
    command = k.get("command")
    kwargs = k.get("kwargs")
    login = k.get("login")
    project_code = k.get("project_code")

    from pyasm.security import Batch
    Batch(project_code=project_code, login_code=login)

    cmd = Common.create_from_class_path(command, kwargs=kwargs)
    Command.execute_cmd(cmd)






if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    k = args[0]
    k = jsonloads(k)
    run_batch(k)

