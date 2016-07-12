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

__all__ = ['TacticThread', 'TacticTimedThread', 'WatchFolderThread', 'ASyncThread', 'TacticMonitor', 'CustomPythonProcessThread']


import os, sys, threading, time, urllib, random, subprocess, re
import tacticenv
tactic_install_dir = tacticenv.get_install_dir()
tactic_site_dir = tacticenv.get_site_dir()
app_server = "cherrypy"

#try:
#    import setproctitle
#    setproctitle.setproctitle("TACTICmaster")
#except:
#    pass


from pyasm.common import Environment, Common, Date, Config, jsonloads, jsondumps
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
    def __init__(my, **kwargs):
        my.kwargs = kwargs
        my.num_checks = 0
        my.kill_interval = 30 + random.randint(0,30)
        my.kill_interval = 1
        my.end = False
        my.port = None
        super(BaseProcessThread,my).__init__()

    def run(my):
        print "Starting %s ..." % my.get_title()

        while 1:

            my.execute()

            # TACTIC has exited
            time.sleep(1)
            
            if my.end:
                #print "Stopping %s ..." % my.get_title()
                break
            else:
                #print "Restarting %s ..." % my.get_title()
                pass

    def get_title(my):
        return "No Title"


    def execute(my):
        raise Exception("Must override execute")

    def write_log(my, msg):
        '''for debugging only'''
        log_dir = "%s/log" % Environment.get_tmp_dir()
 
        f = open('%s/monitor.log' % log_dir,'a')
        import datetime
        f.write('\nTime: %s\n\n' %datetime.datetime.now())
        f.write('%s\n'%msg)

    def check(my):
        pass


    def _get_pid(my):
        '''Get PID from a file'''
        log_dir = "%s/log" % Environment.get_tmp_dir()
        pid_path = "%s/pid.%s" % (log_dir, my.port)
        pid = 0
        if os.path.exists(pid_path):
            file = open(pid_path, "r")
            pid = file.read()
            file.close()
        return pid
       
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
                Common.kill(pid)

                #my.run()
                my.num_checks += 1
                return


        my.num_checks += 1

        start = time.clock()
        try:
            response = my.check()
        except IOError, e:

            pid = my._get_pid() 
            if pid:
                Common.kill(pid)
        else:
            if response and response != "OK":
                #my.end = True
                pid = my._get_pid() 
                if pid:
                    Common.kill(pid)
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




class CustomPythonProcessThread(BaseProcessThread):

    def get_title(my):
        return my.kwargs.get("title")

    def execute(my):
        # Run the job queue service
        path = my.kwargs.get("path")

        plugin_dir = Environment.get_plugin_dir()
        path = path.replace("${TACTIC_PLUGIN_DIR}", plugin_dir)

        cmd_list = []
        cmd_list.append(python)
        cmd_list.append(path)

        program = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        #program.wait()

        buffer = []
        while 1:
            char = program.stdout.read(1)
            if not char:
                break

            if char == "\n":
                line = "".join(buffer)
                #print line

            buffer.append(char)
 



class ASyncThread(BaseProcessThread):

    def get_title(my):
        return "aSync Queue"

    def execute(my):
        # Run the job queue service
        executable = '%s "%s/src/bin/startup_async.py"' % (python, tactic_install_dir)
        os.system('%s' % (executable) )




class JobQueueThread(BaseProcessThread):

    def __init__(my, idx):
        super(JobQueueThread,my).__init__()
        my.idx = idx

    def get_title(my):
        return "Job Task Queue"

    def _check(my):
        pass

    def execute(my):
        # Run the job queue service
        executable = '%s "%s/src/bin/startup_queue.py" -i %s' % (python, tactic_install_dir, my.idx)
        os.system('%s' % (executable) )



class WatchFolderThread(BaseProcessThread):

    def __init__(my, **kwargs):
        super(WatchFolderThread,my).__init__()
        my.project_code = kwargs.get("project_code")
        my.base_dir = kwargs.get("base_dir")
        my.search_type = kwargs.get("search_type")
        my.process = kwargs.get("process")
        my.script_path=kwargs.get("script_path")
        my.watch_folder_code = kwargs.get("watch_folder_code")
 
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
        parts.append('--script_path="%s"'%my.script_path)
        if my.watch_folder_code:
            parts.append('--watch_folder_code="%s"' % my.watch_folder_code)
        if my.process:
            parts.append('--process="%s"' % my.process)

        executable = " ".join(parts)

        os.system('%s' % (executable) )


# DEPRECATED: use TacticSchedulerThread below
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
                if not timed_trigger.is_ready():
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
                #print "Stopping timed thread"
                break


 
class TacticSchedulerThread(threading.Thread):

    def __init__(my):
        my.dev_mode = False
        super(TacticSchedulerThread,my).__init__()

    def _check(my):
        pass

    def set_dev(my, mode):
        my.dev_mode = mode

    def run(my):
        import time
        time.sleep(3)

        #print "Starting Scheduler ...."

        # NOTE: not sure why we have to do a batch here
        from pyasm.security import Batch
        Batch(login_code="admin")

        timed_triggers = []

        from pyasm.biz import Project
        search = Search("sthpw/project")
        # only requires the admin project
        search.add_filter('code', 'sthpw', op='!=')
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
                #print "WARNING: ", e
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

            if has_triggers and my.dev_mode:
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
        my.startup = True
        my.num_processes = num_processes
        my.dev_mode = False

        import sys
        plugin_dir = Environment.get_plugin_dir()
        sys.path.insert(0, plugin_dir)

        sql = DbContainer.get("sthpw")
        # before batch, clean up the ticket with a NULL code
        sql.do_update('DELETE from "ticket" where "code" is NULL;')

        my.tactic_threads = []
        my.mode = 'normal'


    def write_log(my, msg):
        '''for debugging only'''
        log_dir = "%s/log" % Environment.get_tmp_dir()
 
        f = open('%s/monitor.log' % log_dir,'a')
        import datetime
        f.write('\nTime: %s\n\n' %datetime.datetime.now())
        f.write('%s\n'%msg)

    def set_check_interval(my, check_interval):
        my.check_interval = check_interval

    def set_dev(my, mode):
        my.dev_mode = mode

    def watch_folder_cleanup(my, base_dir):
        '''removes old action files from previous watch
        folder processes.'''
        if os.path.exists(base_dir):
            files = os.listdir(base_dir)
            for file_name in files:
                base_file, ext = os.path.splitext(file_name)
                if ext in [".lock", ".checkin"]:
                    path = "%s/%s" % (base_dir, file_name)
                    os.remove(path)
             
    def execute(my):
        if my.mode == 'monitor':
            my.monitor()
        else:
            my._execute()

    def _execute(my):
        '''if mode is normal, this runs both the main startup (init) logic plus monitor'''
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

        #start_tactic = Config.get_value("services", "tactic")
        #start_job_queue = Config.get_value("services", "job_queue")
        #start_watch_folder = Config.get_value("services", "watch_folder")

        start_tactic = False
        start_job_queue = False
        start_watch_folder = False
        start_async = False

        services = Config.get_value("services", "enable")
        custom_services = []
        if services:
            #services = services.split("|")
            services = re.split("[|,]", services)
            for service in services:
                if service == 'tactic':
                    start_tactic = True
                elif service == 'job_queue':
                    start_job_queue = True
                elif service == 'watch_folder':
                    start_watch_folder = True
                elif service == 'async':
                    start_async = True
                else:
                    custom_services.append(service)
        else:
            start_tactic = True


        # create a number of processes
        if start_tactic:
            my.remove_monitor_pid()
            #for i in range(0, my.num_processes):
            for port in ports:

                # start cherrypy
                tactic_thread = TacticThread(port)
                tactic_thread.set_dev(my.dev_mode)

                tactic_thread.start()
                tactic_threads.append(tactic_thread)
                time.sleep(1)
                #port += 1


        # aSync Queue services
        if start_async:
            num_processes = Config.get_value("async", "process_count")
            if not num_processes:
                num_processes = 1
            else:
                num_processes = int(num_processes)

            for i in range(0, num_processes):
                job_thread = ASyncThread()
                job_thread.start()
                tactic_threads.append(job_thread)


        # Job Queue services
        if start_job_queue:
            num_processes = Config.get_value("services", "queue_process_count")
            if not num_processes:
                num_processes = 1
            else:
                num_processes = int(num_processes)

            for i in range(0, num_processes):
                job_thread = JobQueueThread(i)
                job_thread.start()
                tactic_threads.append(job_thread)


        # Watch Folder services
        if start_watch_folder:
            search = Search("sthpw/watch_folder")
            watch_folders = search.get_sobjects()

            for watch_folder in watch_folders:
                project_code = watch_folder.get("project_code")
                base_dir = watch_folder.get("base_dir")
                search_type = watch_folder.get("search_type")
                process = watch_folder.get("process")
                script_path = watch_folder.get("script_path")
                watch_folder_code = watch_folder.get("code")

                if not project_code:
                    print "Watch Folder missing project_code ... skipping"
                    continue

                if not base_dir:
                    print "Watch Folder missing base_dir ... skipping"
                    continue

                if not search_type:
                    print "Watch Folder missing search_type ... skipping"
                    continue

                my.watch_folder_cleanup(base_dir)

                watch_thread = WatchFolderThread(
                        project_code=project_code,
                        base_dir=base_dir,
                        search_type=search_type,
                        process=process,
                        script_path = script_path,
                        watch_folder_code=watch_folder_code
                )
                watch_thread.start()
                tactic_threads.append(watch_thread)



        # set up custom services 
        for service in custom_services:
            kwargs = Config.get_section_values(service)
            custom_thread = CustomPythonProcessThread(**kwargs)
            custom_thread.start()
            tactic_threads.append(custom_thread)



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

        start_scheduler = Config.get_value("services", "scheduler")
        if start_scheduler == 'true':
            tactic_scheduler_thread = TacticSchedulerThread()
            tactic_scheduler_thread.set_dev(my.dev_mode)
            tactic_scheduler_thread.start()
            tactic_threads.append(tactic_scheduler_thread)





        DbContainer.close_thread_sql()
        my.tactic_threads = tactic_threads
        if my.mode == "normal":
            my.monitor()


    def remove_monitor_pid(my):
        '''remove the stop.monitor file'''
        log_dir = "%s/log" % Environment.get_tmp_dir()

        if os.path.exists("%s/stop.monitor" % log_dir):
            os.unlink("%s/stop.monitor" % log_dir)

    def monitor(my):
        '''monitor the tactic threads'''
        start_time = time.time()
        log_dir = "%s/log" % Environment.get_tmp_dir()
        
        while 1:
            end = False
            try:
                monitor_stop = os.path.exists('%s/stop.monitor'%log_dir)
                if monitor_stop:
                    for tactic_thread in my.tactic_threads:
					    tactic_thread.end = True
                    break
                if my.check_interval:
                    # don't check threads during startup period
                    if not my.startup:
                        time.sleep(my.check_interval)
                        for tactic_thread in my.tactic_threads:
                            tactic_thread._check()
                    else:
                        if time.time() - start_time > my.check_interval:
                            my.startup = False

                else:
                    # Windows Service does not need this 0 check_interval
                    # any more.  
                    break

            except KeyboardInterrupt, e:
                #print "Keyboard interrupt ... exiting Tactic"
                for tactic_thread in my.tactic_threads:
                    tactic_thread.end = True
                    end = True

            if end:
                break

        my.final_kill()
        

    def final_kill(my):
        '''Kill the startup, startup_queue, watch_folder processes. This is used primarily in Windows Service.
           Linux service should have actively killed the processes already'''
        log_dir = "%s/log" % Environment.get_tmp_dir()
        files = os.listdir(log_dir)
        ports = []
        watch_folders = []
        queues = []

        for filename in files:
            base, ext = os.path.splitext(filename)
            if base == 'pid':
                ports.append(ext[1:])
            elif base == 'watch_folder':
                watch_folders.append(ext[1:])
            elif base == 'startup_queue':
                queues.append(ext[1:])

    
        for port in ports:
            try:
                file_name = "%s/pid.%s" % (log_dir,port)
                file = open(file_name, "r")
                pid = file.readline().strip()
                file.close()
                Common.kill(pid)
            except IOError, e:
                continue

        # kill watch folder processes
        for watch_folder in watch_folders:
            try:
                filename = "%s/watch_folder.%s" % (log_dir, watch_folder)
                f = open(filename, "r")
                pid = f.readline()
                f.close()
                Common.kill(pid)
            except IOError, e:
                continue
        for idx, queue in enumerate(queues):
            try:
                filename = "%s/startup_queue.%s" % (log_dir, idx)
                f = open(filename, "r")
                pid = f.readline()
                f.close()
                Common.kill(pid)
            except IOError, e:
                continue

if __name__ == '__main__':
    monitor = TacticMonitor()

    monitor.execute()


