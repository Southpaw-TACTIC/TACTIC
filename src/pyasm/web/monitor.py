############################################################
#
#    Copyright (c) 2005, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#


# scripts that starts up a number of Tactic and monitors them

__all__ = ['TacticThread', 'TacticTimedThread', 'TacticMonitor']


import os, sys, threading, time, urllib, random
import tacticenv
tactic_install_dir = tacticenv.get_install_dir()
tactic_site_dir = tacticenv.get_site_dir()
app_server = "cherrypy"

#try:
#    import setproctitle
#    setproctitle.setproctitle("TACTICmaster")
#except:
#    pass


from pyasm.common import Environment, Common, Date, Config
from pyasm.search import Search, DbContainer, SearchType

python = Config.get_value("services", "python")
if not python:
    python = os.environ.get('PYTHON')
if not python:
    python = 'python'
STARTUP_EXEC = '%s "%s/src/bin/startup.py"' % (python, tactic_install_dir)
STARTUP_DEV_EXEC = '%s "%s/src/bin/startup_dev.py"' % (python, tactic_install_dir)



class BaseProcessThread(threading.Thread):
    '''Each Thread runs a separate TACTIC service'''
    def __init__(my):
        my.num_checks = 0
        my.kill_interval = 30 + random.randint(0,30)
        my.kill_interval = 1
        my.end = False
        super(BaseProcessThread,my).__init__()

    def run(my):
        while 1:
            my.execute()

            # TACTIC has exited
            time.sleep(1)
            
            if my.end:
                print "Stopping port %s ..." % my.get_title()
                break
            else:
                print "Restarting %s ..." % my.get_title()

    def get_title(my):
        return "No Title"


    def execute(my):
        raise Exception("Must override execute")


    def check(my):
        pass


    def _check(my):

        # This will kill the TACTIC process 
        # This is very harsh and should be used sparingly if at all
        use_restart = Config.get_value("services", "use_periodic_restart")
        if use_restart in [True, 'true']:
            if my.num_checks and my.num_checks % my.kill_interval == 0:
                # read pid file
                log_dir = "%s/log" % Environment.get_tmp_dir()
                file = open("%s/pid.%s" % (log_dir,my.port), "r")
                pid = file.read()
                file.close()
                print "Killing process: ", pid
                Common.kill(pid)

                #my.run()
                my.num_checks += 1
                return



        my.num_checks += 1

        start = time.clock()
        try:
            response = my.check()
        except IOError, e:
            print "Tactic IOError: ", str(e)

            # Kill if unresponsive ... (only on linux)
            log_dir = "%s/log" % Environment.get_tmp_dir()
            file = open("%s/pid.%s" % (log_dir,my.port), "r")
            pid = file.read()
            file.close()
            print "Killing process: ", pid
            Common.kill(pid) 
        else:
            if response and response != "OK":
                my.end = True
                return

        '''
        # check the time it took to respond
        end = time.clock()
        interval = end - start

        # if greater than 5 second, kill the process and restart
        if interval > 5:
            # read pid file
            log_dir = "%s/log" % Environment.get_tmp_dir()
            file = open("%s/pid.%s" % (log_dir,my.port), "r")
            pid = file.read()
            file.close()

            print "WARNING : port %s is not responsive!!" % my.port
        '''




class TacticThread(BaseProcessThread):
    def __init__(my, port):
        super(TacticThread,my).__init__()

        my.dev_mode = False
        my.port = port

    def set_dev(my, mode):
        my.dev_mode = mode

    def get_title(my):
        return my.port


    def execute(my):
        if my.dev_mode:
            exec_file = STARTUP_DEV_EXEC
        else:
            exec_file = STARTUP_EXEC
        os.system('%s %s' % (exec_file, my.port) )

    def check(my):
        f = urllib.urlopen("http://localhost:%s/test" % my.port )
        response = f.readlines()
        f.close()
        return response[0]



class JobQueueThread(BaseProcessThread):

    def get_title(my):
        return "Job Task Queue"

    def execute(my):
        # Run the job queue service
        executable = '%s "%s/src/bin/startup_queue.py"' % (python, tactic_install_dir)
        os.system('%s' % (executable) )



class WatchFolderThread(BaseProcessThread):

    def __init__(my, **kwargs):
        super(WatchFolderThread,my).__init__()
        my.project_code = kwargs.get("project_code")
        my.base_dir = kwargs.get("base_dir")
        my.search_type = kwargs.get("search_type")
        my.process = kwargs.get("process")

 
    def get_title(my):
        return "Watch Folder"

    def execute(my):

        # Run the job queue service
        parts = []
        parts.append(python)
        parts.append('"%s/src/tactic/command/watch_drop_folder.py"'% tactic_install_dir)
        parts.append('--project="%s"' % my.project_code)
        parts.append('--drop_path="%s"' % my.base_dir)
        parts.append('--search_type="%s"' % my.search_type)
        if my.process:
            parts.append('--process="%s"' % my.process)

        executable = " ".join(parts)

        os.system('%s' % (executable) )




# DEPRECATED: use SchedulerThread below
class TacticTimedThread(threading.Thread):

    def __init__(my):
        my.end = False
        super(TacticTimedThread,my).__init__()

    def _check(my):
        pass


    def run(my):

        import time
        time.sleep(6)

        #print "Starting Timed Trigger"

        # checks are done every 60 seconds
        chunk = 60

        # FIXME: not sure why we have to do a batch here
        from pyasm.security import Batch
        Batch(login_code="admin")

        # get the all of the timed triggers
        #search = Search("sthpw/timed_trigger")
        #search.add_filter("type", "timed")
        search = Search("sthpw/trigger")
        search.add_filter("event", "timed")
        timed_trigger_sobjs = search.get_sobjects()
        timed_triggers = []


        
        for trigger_sobj in timed_trigger_sobjs:
            trigger_class = trigger_sobj.get_value("class_name")
            try:
                timed_trigger = Common.create_from_class_path(trigger_class)
            except ImportError:
                raise Exception("WARNING: [%s] does not exist" % trigger_class)
                
            timed_triggers.append(timed_trigger)


        while 1:
            time.sleep(chunk)
            #print "Running timer"

            date = Date()
            #print "utc: ", date.get_display_time()

            # go through each trigger
            for timed_trigger in timed_triggers:
                print timed_trigger
                if not timed_trigger.is_ready():
                    print "... not ready"
                    continue

                if timed_trigger.is_in_separate_thread():
                    class xxx(threading.Thread):
                        def run(my):
                            try:
                                Batch()
                                timed_trigger._do_execute()
                            finally:
                                DbContainer.close_thread_sql()
                    xxx().start()
                else:
                    timed_trigger._do_execute()

            DbContainer.close_thread_sql()


            if my.end:
                print "Stopping timed thread"
                break


 
class TacticSchedulerThread(threading.Thread):

    def __init__(my):
        super(TacticSchedulerThread,my).__init__()

    def _check(my):
        pass


    def run(my):
        import time
        time.sleep(3)

        print "Starting Scheduler ...."

        # NOTE: not sure why we have to do a batch here
        from pyasm.security import Batch
        Batch(login_code="admin")

        timed_triggers = []

        from pyasm.biz import Project
        search = Search("sthpw/project")
        projects = search.get_sobjects()

        # get the all of the timed triggers
        #search = Search("sthpw/timed_trigger")
        #search.add_filter("type", "timed")
        for project in projects:

            project_code = project.get_code()
            try:
                search = Search("config/trigger?project=%s" % project_code)
                search.add_filter("event", "schedule")
                timed_trigger_sobjs = search.get_sobjects()
            except Exception, e:
                print "WARNING: ", e
                continue

            # example
            """
            if project_code == 'broadcast2':
                tt = SearchType.create("config/trigger")
                tt.set_value("class_name", "tactic.command.PythonTrigger")

                # data = timed_trigges.get("data")
                tt.set_value("data", '''{
                    "type": "interval",
                    "interval": 5,
                    "delay": 5,
                    "mode": "threaded",
                    "script_path": "trigger/scheduled"
                } ''')
                timed_trigger_sobjs.append(tt)
            """


            has_triggers = False
            for trigger_sobj in timed_trigger_sobjs:
                trigger_class = trigger_sobj.get_value("class_name")
                if not trigger_class and trigger_sobj.get_value("script_path"):
                    trigger_class = 'tactic.command.PythonTrigger'

                data = trigger_sobj.get_json_value("data")

                data['project_code'] = trigger_sobj.get_project_code()

                try:
                    timed_trigger = Common.create_from_class_path(trigger_class, [], data)
                    timed_trigger.set_input(data)
                    has_triggers = True

                except ImportError:
                    raise Exception("WARNING: [%s] does not exist" % trigger_class)
                    
                timed_triggers.append(timed_trigger)

            if has_triggers:
                print "Found [%s] scheduled triggers in project [%s]..." % (len(timed_triggers), project_code)

        from tactic.command import Scheduler, SchedulerTask
        scheduler = Scheduler.get()

        scheduler.start_thread()



        class TimedTask(SchedulerTask):
            def __init__(my, **kwargs):
                super(TimedTask, my).__init__(**kwargs)
                my.index = kwargs.get("index")
                my.project_code = kwargs.get("project_code")

            def execute(my):
                try:
                    #Batch()
                    #Command.execute_cmd(timed_trigger)
                    Project.set_project(my.project_code)
                    timed_triggers[my.index].execute()
                except Exception, e:
                    print "Error running trigger"
                    raise
                finally:
                    DbContainer.close_thread_sql()
                    DbContainer.commit_thread_sql()
                    DbContainer.close_all()


        for idx, timed_trigger in enumerate(timed_triggers):

            data = timed_trigger.get_input()
            if not data:
                continue

            """
            data = {
                'type': 'interval',
                'interval': 10,
                'delay': 0,
                'mode': 'threaded'
            }
            """

            project_code = data.get("project_code")
            task = TimedTask(index=idx, project_code=project_code)

            args = {}
            if data.get("mode"):
                args['mode'] = data.get("mode")

            trigger_type = data.get("type")

            if trigger_type == 'interval':
                #scheduler.add_interval_task(task, interval=interval, mode='threaded', delay=0)

                args = {
                    'interval': int( data.get("interval") ),
                    'delay': int( data.get("delay") ),
                }

                scheduler.add_interval_task(task, **args)


            elif trigger_type == "daily":

                from dateutil import parser

                args['time'] = parser.parse( data.get("time") )

                if data.get("weekdays"):
                    args['weekdays'] = eval( data.get("weekdays") )

                scheduler.add_daily_task(task, **args)

                #scheduler.add_daily_task(task, time, mode="threaded", weekdays=range(1,7))

            elif trigger_type == "weekly":
                #scheduler.add_weekly_task(task, weekday, time, mode='threaded'):
                args['time'] = parser.parse( data.get("time") )

                if data.get("weekday"):
                    args['weekday'] = eval( data.get("weekday") )

                scheduler.add_weekly_task(task, **args)



      

class TacticMonitor(object):

    def __init__(my, num_processes=None):
        my.check_interval = 120
        my.num_processes = num_processes
        my.dev_mode = False
        sql = DbContainer.get("sthpw")
        # before batch, clean up the ticket with a NULL code
        sql.do_update('DELETE from "ticket" where "code" is NULL;')


    def set_check_interval(my, check_interval):
        my.check_interval = check_interval

    def set_dev(my, mode):
        my.dev_mode = mode

    def execute(my):
        from pyasm.security import Batch
        Batch(login_code="admin")

        os.environ["TACTIC_MONITOR"] = "true"

        if not my.num_processes:
            my.num_processes = Config.get_value("services", "process_count")
            if my.num_processes:
                my.num_processes = int(my.num_processes)
            else:
                my.num_processes = 3



        start_port = Config.get_value("services", "start_port")

        ports_str = os.environ.get("TACTIC_PORTS")
        if not ports_str:
            ports_str = Config.get_value("services", "ports")

        if ports_str:
            ports = ports_str.split("|")
            ports = [int(x) for x in ports]
        else:
            if start_port:
                start_port = int(start_port)
            else:
                start_port = 8081
            ports = []
            for i in range(0, my.num_processes):
                ports.append( start_port + i )
        

        tactic_threads = []

        use_tactic = Config.get_value("services", "tactic")
        use_job_queue = Config.get_value("services", "job_queue")
        use_watch_folder = Config.get_value("services", "watch_folder")


        # create a number of processes
        if use_tactic != 'false':
            #for i in range(0, my.num_processes):
            for port in ports:

                # start cherrypy
                tactic_thread = TacticThread(port)
                tactic_thread.set_dev(my.dev_mode)

                tactic_thread.start()
                tactic_threads.append(tactic_thread)
                time.sleep(1)
                #port += 1


        # Job Queue services
        if use_job_queue == 'true':
            num_processes = Config.get_value("services", "queue_process_count")
            if not num_processes:
                num_processes = 1
            else:
                num_processes = int(num_processes)

            for i in range(0, num_processes):
                job_thread = JobQueueThread()
                job_thread.start()
                tactic_threads.append(job_thread)


        # Watch Folder services
        if use_watch_folder == 'true':
            search = Search("sthpw/watch_folder")
            watch_folders = search.get_sobjects()

            for watch_folder in watch_folders:
                project_code = watch_folder.get("project_code")
                base_dir = watch_folder.get("base_dir")
                search_type = watch_folder.get("search_type")
                process = watch_folder.get("process")

                if not project_code:
                    print "Watch Folder missing project_code ... skipping"
                    continue

                if not project_code:
                    print "Watch Folder missing base_dir ... skipping"
                    continue

                if not search_type:
                    print "Watch Folder missing search_type ... skipping"
                    continue

                watch_thread = WatchFolderThread(
                        project_code=project_code,
                        base_dir=base_dir,
                        search_type=search_type,
                        process=process
                        )
                watch_thread.start()
                tactic_threads.append(watch_thread)




        if len(tactic_threads) == 0:
            print
            print "No services started ..."
            print
            return



        # create a separate thread for timed processes
        # DEPRECATED
        tactic_timed_thread = TacticTimedThread()
        tactic_timed_thread.start()
        tactic_threads.append(tactic_timed_thread)

        # create a separate thread for scheduler processes

        use_scheduler = Config.get_value("services", "scheduler")
        if use_scheduler == 'true':
            tactic_scheduler_thread = TacticSchedulerThread()
            tactic_scheduler_thread.start()
            tactic_threads.append(tactic_scheduler_thread)





        DbContainer.close_thread_sql()


        # check each thread every 20 seconds
        while 1:
            end = False
            try:
                if my.check_interval:
                    time.sleep(my.check_interval)
                    for tactic_thread in tactic_threads:
                        tactic_thread._check()

                else:
                    # FIXME: break for now (for windows service)
                    break

            except KeyboardInterrupt, e:
                print "Keyboard interrupt ... exiting Tactic"
                for tactic_thread in tactic_threads:
                    tactic_thread.end = True
                    end = True

            if end:
                break

        #print "exiting Tactic"
        #sys.exit(0)



if __name__ == '__main__':
    monitor = TacticMonitor()

    monitor.execute()


