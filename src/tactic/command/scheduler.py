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

'''Scheduler class provides a thin layer on top of the Kronos module
by Kronos scheduler (c) Irmen de Jong.  It provides a more object oriented
abraction layer and also adds some Tactic integration and conveniences'''

__all__ = ['Scheduler', 'SchedulerTask']

import tacticenv

from kronos import Scheduler as KronosScheduler
from pyasm.common import Container, Environment
from pyasm.biz import Project
from pyasm.security import Site

import time, datetime, types



class Scheduler(object):
    '''Wrapper around kronos'''

    def __init__(my):
        my.scheduler = KronosScheduler()
        my.tasks = {}
        my.is_started = False


    def cancel_task(my, name, delay=0):
        task = my.tasks.get(name)
        if not task:
            return

        class CancelTask(SchedulerTask):
            def execute(my2):
                print "Cancelling task [%s]" % name
                my.scheduler.cancel(task)
                del(my.tasks[name])
        my.add_single_task( CancelTask(), delay=delay )


    def _process_task(my, task, mode):
        project = Project.get_project_code()
        if not task.kwargs.get("user"):
            user = Environment.get_user_name()
        if not task.kwargs.get("project"):
            project_code = Project.get_project_code()
            task.kwargs['project'] = project_code

        task.kwargs['mode'] = mode

    def add_single_task(my, task, delay=0, mode='threaded'):
        action = task._do_execute
        my._process_task(task, mode)
        my.scheduler.add_single_task(
            action=action, taskname=task.get_name(),
            initialdelay=delay,
            processmethod=mode, args=None, kw=None )

    def add_interval_task(my, task, interval, mode='threaded',delay=0):
        action = task._do_execute
        my._process_task(task, mode)
        scheduler_task = my.scheduler.add_interval_task(
            action=action, taskname=task.get_name(),
            initialdelay=delay, interval=interval,
            processmethod=mode, args=None, kw=None )
        my.tasks[task.get_name()] = scheduler_task


    def add_daily_task(my, task, time, mode="threaded", weekdays=range(1,8)):

        if isinstance(time, basestring):
            hour, minute = time.split(":")
            hour = int(hour)
            minute = int(minute)
        else:
            hour = time.hour
            minute = time.minute
        timeonday = (hour, minute)

        weekdays = weekdays
        action = task._do_execute
        my._process_task(task, mode)

        my.scheduler.add_daytime_task(
            action=action, taskname=task.get_name(),
            weekdays=weekdays, monthdays=None, timeonday=timeonday,
            processmethod=mode, args=None, kw=None )

    def add_weekly_task(my, task, weekday, time, mode='threaded'):

        weekdays = (weekday)
        timeonday = (time.hour, time.minute)
        action = task._do_execute
        my._process_task(task, mode)

        my.scheduler.add_daytime_task(
            action=action, taskname=task.get_name(),
            weekdays=weekdays, monthdays=None, timeonday=timeonday,
            processmethod=mode, args=None, kw=None )


    def start(my):
        my.scheduler.start()



    def start_thread(my):
        if my.is_started:
            return
            
        import threading
        my.thread = threading.Thread(None, my.start)
        #my.thread.daemon = True
        my.thread.setDaemon(True)
        my.thread.start()

        my.is_started = True


    def stop(my):
        my.scheduler.stop()



    def add_sobject(my, sobject):

        '''
        <task class="TestTask">
          <type>interval</type>
          <interval>10</interval>
        </task>
        '''

        type = "interval"
        class_name = "TestTask"

        options = {
            "interval": 10
        }

        if type == "interval": 
            task = Common.create_from_class_path(class_name)
            scheduler.add_interval_task(task, **options)
        elif type == "daily": 
            task = Common.create_from_class_path(class_name)
            scheduler.add_daily_task(task, **options)
        elif type == "weekly": 
            task = Common.create_from_class_path(class_name)
            scheduler.add_weekly_task(task, **options)


    def get():
        scheduler = Container.get("Scheduler")
        if scheduler == None:
            scheduler = Scheduler()
            Container.put("Scheduler", scheduler)
        return scheduler
    get = staticmethod(get)        




class SchedulerTask(object):
    '''Base class for the scheduler'''
    def __init__(my, **kwargs):
        my.kwargs = kwargs
        user = my.kwargs.get('user')
        project = my.kwargs.get('project')

        my.site = my.kwargs.get('site')
        if not my.site:
            # if not explicitly set, keep the site that is current
            my.site = Site.get_site()

        if user and project:
            from pyasm.security import Batch
            Batch(site=my.site, login_code=user, project_code=project)

        my.security = Environment.get_security()


    def get_name(my):
        return my.kwargs.get("name")

    def _do_execute(my):
        # reestablish the site
        if my.site:
            try:
                Site.set_site(my.site)
            except:
                return
        try:
            Environment.set_security(my.security)
            my.execute()
        finally:
            if my.site:
                Site.pop_site()

    def execute(my):
        print my.kwargs

    def execute_test(my):
        print my.kwargs


class TestTask(SchedulerTask):
    def execute(my):
        print "!!!! TestTask: ", my.get_name()
        print "\ttime: ", datetime.datetime.now()



class TestTask2(SchedulerTask):
    def execute(my):
        print "time: ", datetime.datetime.now()
        now = datetime.datetime.now()
        now, xx = str(now).split(".")
        date, timestamp = now.split(" ")
        date = date.replace("-", "")
        timestamp = timestamp.replace(":", "")

        filename = "db_%s_%s.sql" % (date, timestamp)
        print filename

        import os
        print("pg_dumpall -U postgres > %s" % filename)
        os.system("pg_dumpall -U postgres > %s" % filename)


class SystemTask(SchedulerTask):
    def execute(my):
        command = my.kwargs.get("command")
        import os
        os.system(command)




def main():
    from pyasm.security import Batch
    batch = Batch(login_code='admin')
    scheduler = Scheduler.get()

    task = TestTask(name="cow")
    scheduler.add_interval_task(task, 30)

    task = SystemTask(name="wowowow", command='ls', mode='forked')
    scheduler.add_single_task(task, 5)

    task = SystemTask(name="wowowow", command='ls', mode='forked')
    scheduler.add_single_task(task, 13)

    task = TestTask2(name="cow2")
    time = datetime.time(22,00)
    scheduler.add_daily_task(task, time, weekdays=range(4,7))

    scheduler.start_thread()

    import time
    """
    try:
        time.sleep(5)

        task = TestTask(name="horse")
        scheduler.add_interval_task(task, 5)

        time.sleep(30)

    except KeyboardInterrupt, e:
        print 'stopping'
        #scheduler.stop()
    else:
        scheduler.stop()

    """
    while 1:
        try:
            time.sleep(15)
        except (KeyboardInterrupt, SystemExit), e:
            scheduler.stop()
            break
        else:
            scheduler.stop()
    
    scheduler.stop()

if __name__ == '__main__':
    main()





