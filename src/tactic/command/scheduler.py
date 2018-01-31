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

    def __init__(self):
        self.scheduler = KronosScheduler()
        self.tasks = {}
        self.is_started = False


    def cancel_task(self, name, delay=0):
        task = self.tasks.get(name)
        if not task:
            return

        class CancelTask(SchedulerTask):
            def execute(self2):
                print "Cancelling task [%s]" % name
                self.scheduler.cancel(task)
                del(self.tasks[name])
        self.add_single_task( CancelTask(), delay=delay )


    def _process_task(self, task, mode):
        project = Project.get_project_code()
        if not task.kwargs.get("user"):
            user = Environment.get_user_name()
        if not task.kwargs.get("project"):
            project_code = Project.get_project_code()
            task.kwargs['project'] = project_code

        task.kwargs['mode'] = mode

    def add_single_task(self, task, delay=0, mode='threaded'):
        action = task._do_execute
        self._process_task(task, mode)
        self.scheduler.add_single_task(
            action=action, taskname=task.get_name(),
            initialdelay=delay,
            processmethod=mode, args=None, kw=None )

    def add_interval_task(self, task, interval, mode='threaded',delay=0):
        action = task._do_execute
        self._process_task(task, mode)
        scheduler_task = self.scheduler.add_interval_task(
            action=action, taskname=task.get_name(),
            initialdelay=delay, interval=interval,
            processmethod=mode, args=None, kw=None )
        self.tasks[task.get_name()] = scheduler_task


    def add_daily_task(self, task, time, mode="threaded", weekdays=range(1,8)):

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
        self._process_task(task, mode)

        self.scheduler.add_daytime_task(
            action=action, taskname=task.get_name(),
            weekdays=weekdays, monthdays=None, timeonday=timeonday,
            processmethod=mode, args=None, kw=None )

    def add_weekly_task(self, task, weekday, time, mode='threaded'):

        weekdays = (weekday)
        timeonday = (time.hour, time.minute)
        action = task._do_execute
        self._process_task(task, mode)

        self.scheduler.add_daytime_task(
            action=action, taskname=task.get_name(),
            weekdays=weekdays, monthdays=None, timeonday=timeonday,
            processmethod=mode, args=None, kw=None )


    def start(self):
        self.scheduler.start()



    def start_thread(self):
        if self.is_started:
            return
            
        import threading
        self.thread = threading.Thread(None, self.start)
        #self.thread.daemon = True
        self.thread.setDaemon(True)
        self.thread.start()

        self.is_started = True


    def stop(self):
        self.scheduler.stop()



    def add_sobject(self, sobject):

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
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        user = self.kwargs.get('user')
        project = self.kwargs.get('project')

        self.site = self.kwargs.get('site')
        if not self.site:
            # if not explicitly set, keep the site that is current
            self.site = Site.get_site()

        if user and project:
            from pyasm.security import Batch
            Batch(site=self.site, login_code=user, project_code=project)

        self.security = Environment.get_security()


    def get_name(self):
        return self.kwargs.get("name")

    def _do_execute(self):
        # reestablish the site
        if self.site:
            try:
                Site.set_site(self.site)
            except:
                return
        try:
            Environment.set_security(self.security)
            self.execute()
        finally:
            if self.site:
                Site.pop_site()

    def execute(self):
        print self.kwargs

    def execute_test(self):
        print self.kwargs


class TestTask(SchedulerTask):
    def execute(self):
        print "!!!! TestTask: ", self.get_name()
        print "\ttime: ", datetime.datetime.now()



class TestTask2(SchedulerTask):
    def execute(self):
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
    def execute(self):
        command = self.kwargs.get("command")
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





