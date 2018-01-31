############################################################
#
#    Copyright (c) 2012, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#


__all__ = ['WatchDropFolderTask']




import tacticenv
import time, os, shutil, sys
import os.path
import sys

from pyasm.common import Environment, Config, Common
from pyasm.security import Batch
from pyasm.biz import Project
from pyasm.search import DbContainer
from pyasm.search import Search, Transaction, SearchType
from pyasm.command import Command
from tactic.command import SchedulerTask, Scheduler
from time import gmtime, strftime
from optparse import OptionParser
from tactic.command import PythonCmd
from dateutil import parser

import threading


import logging
#logging.basicConfig(filename='/tmp/myapp.log', level=logging.INFO)

try:
    from watchdog.observers import Observer
    from watchdog.events import LoggingEventHandler
except:
    Observer = None
    LoggingEventHandler = object

class TestLoggingEventHandler(LoggingEventHandler):
    """Logs all the events captured."""

    def on_moved(self, event):
        super(LoggingEventHandler, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        print "Moved %s: from %s to %s" % (what, event.src_path, event.dest_path)

    def on_created(self, event):
        super(LoggingEventHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        print "Created %s: %s" % (what, event.src_path)

    def on_deleted(self, event):
        super(LoggingEventHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        print "Deleted %s: %s" % (what, event.src_path)

    def on_modified(self, event):
        super(LoggingEventHandler, self).on_modified(event)

        what = 'directory' if event.is_directory else 'file'
        print "Modified %s: %s" % (what, event.src_path)




class WatchFolderFileActionThread(threading.Thread):
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super(WatchFolderFileActionThread, self).__init__()

    def run(self):

        task = self.kwargs.get("task")
        site = task.site
        project_code = task.project_code
        Batch(site=site, project_code=project_code)
        try:
            self._run()
        finally:
            task = self.kwargs.get("task")
            paths = task.get_paths()
            task.set_clean(True)
            for path in paths:
                lock_path = "%s.lock" % path
                if os.path.exists(lock_path):
                    os.unlink(lock_path)
            task.set_clean(False)


    def _run(self):

        task = self.kwargs.get("task")
        paths = task.get_paths()
        count = 0
        restart = False

        while True:
            
            if not paths:
                time.sleep(1)
                continue
            
            path = paths.pop(0)
            checkin_path = "%s.checkin" % path
            lock_path = "%s.lock" % path
            error_path = "%s.error" % path

            if not os.path.exists(path):
                continue
            if not os.path.exists(checkin_path):
                #print "Action Thread SKIP: no checkin path [%s]" % checkin_path
                continue
            else:
                # Exit if another process is also checking this file in.                
                f = open(checkin_path, "r")
                pid = f.readline()
                f.close()
                if pid != str(os.getpid()):
                    continue

            try:

                kwargs = {
                    "project_code": task.project_code,
                    "search_type": task.search_type,
                    "base_dir": task.base_dir,
                    "process": task.process,
                    "script_path": task.script_path,
                    "path": path
                }

                handler = task.get("handler")
                if handler:
                    cmd = Common.create_from_class_path(handler, [], kwargs)
                else:
                    # create a "custom" command that will act on the file
                    cmd = CheckinCmd(**kwargs)

                #print "Process [%s] checking in [%s]" % (os.getpid(), path)
                cmd.execute()

                # TEST
                #time.sleep(1)
                #if os.path.exists(path):
                #    os.unlink(path)

                count += 1
                if count == 20:
                    restart = True
                    task.set_clean(True)
                    break


            except Exception as e:
                print "Error: ", e
                f = open(error_path,"w")
                f.write(str(e))
                f.close()
                #raise

            finally:

                task.set_clean(True)
                if os.path.exists(checkin_path):
                    os.unlink(checkin_path)
                if os.path.exists(lock_path):
                    os.unlink(lock_path)
                task.set_clean(False)
                
                if restart:
                    task.set_clean(True)



        # restart every 20 check-ins
        if restart:
            for path in paths:
                checkin_path = "%s.checkin" % path
                lock_path = "%s.lock" % path
                if os.path.exists(checkin_path):
                    os.unlink(checkin_path)
                if os.path.exists(lock_path):
                    os.unlink(lock_path)
            # this exaggerates the effect of not pausing check thread for cleaning
            #time.sleep(10)
            Common.kill()



class WatchFolderCheckFileThread(threading.Thread):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super(WatchFolderCheckFileThread, self).__init__()

        path = self.kwargs.get("path")
        self.lock_path = "%s.lock" % path
        self.error_path = "%s.error" % path
        self.checkin_path = "%s.checkin" % path


    def run(self):

        try:
            path = self.kwargs.get("path")
           
            # this extra checkin_path check may not be needed
            if os.path.exists(self.lock_path) or os.path.exists(self.checkin_path):
                return

            task = self.kwargs.get("task")
 
            if task.in_clean():
                return
            
            pid = os.getpid()
            f = open(self.lock_path, "w")
            f.close()

            changed = self.verify_file_size(path)
            if changed:
                if os.path.exists(self.lock_path):
                    os.unlink(self.lock_path)
                return

            # time has passed, check again
            if task.in_clean():
                return



            f = open(self.checkin_path, "w")
            f.write(str(pid))
            f.close()

            task.add_path(path)


        except Exception as e:
            print "Error: ", e
            f = open(self.error_path, "w")
            f.write(str(e))
            f.close()
            raise

        finally:
            if os.path.exists(self.lock_path):
                os.unlink(self.lock_path)


    def verify_file_size(self, file_path):
        '''Check if the file size changes over a period of 5 seconds. If so, file is not ready'''

        # assume nothing has changed
        changed = False

        # Chech whether the file_path exists or not. Once the file is ready, the or
        if not os.path.exists(file_path):
            return True

        for i in range(0, 5):
            file_size = os.path.getsize(file_path)
            mtime = os.path.getmtime(file_path)
            #print "file_size: ", file_size
            #print "mtime: ", mtime

            time.sleep(2)

            if not os.path.exists(file_path):
                changed = True
                break

            if os.path.isdir(file_path):
                file_size2 = os.path.getsize(file_path)
            else:
                file_size2 = os.path.getsize(file_path)

            mtime2 = os.path.getmtime(file_path)
            #print "file_size2: ", file_size2
            #print "mtime2: ", mtime2
            #print

            if file_size != file_size2:
                changed = True
                break
            if mtime != mtime2:
                changed = True
                break

        return changed


from pyasm.command import Command
__all__.append("TestCmd")
class TestCmd(Command):

    def execute(self):

        path = self.kwargs.get("path")

        # do something
        print "path: ", path





class CheckinCmd(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs


    def is_image(self, file_name):
        base, ext = os.path.splitext(file_name)
        ext = ext.lstrip(".").lower()
        if ext in ['tif','tiff','jpg','jpeg','png','pic','bmp','gif','psd']:
            return True
        else:
            return False

    def is_movie(self, file_name):
        base, ext = os.path.splitext(file_name)
        ext = ext.lstrip(".").lower()
        if ext in ['mov','wmv','mpg','mpeg','m1v','mp2','mpa','mpe','mp4','wma','asf','asx','avi','wax','wm','wvx']:
            return True
        else:
            return False

    def get_asset_type(self, file_path):
        if self.is_movie(file_path):
            return 'movie'
        elif self.is_image(file_path):
            return 'image'
        else:
            return 'other'

    def create_checkin_log(self):
        base_dir = self.kwargs.get("base_dir")
        log_path = '%s/TACTIC_log.txt' %(base_dir)
        if not (os.path.isfile(log_path)):
            file = open(log_path, 'w')   
            title='File Name'+40*' '+'Checkin-Time'+20*' '+'Version#'+6*' ' +'Message\n'
            f = open(log_path, 'a')
            f.write(title)
            f.close()




    def execute(self):

        file_path = self.kwargs.get("path")
        site = self.kwargs.get("site")
        project_code = self.kwargs.get("project_code")
        base_dir = self.kwargs.get("base_dir")
        search_type = self.kwargs.get("search_type")
        process = self.kwargs.get("process")
        watch_script_path = self.kwargs.get("script_path")
        if not process:
            process = "publish"

        basename = os.path.basename(file_path)

        context = self.kwargs.get("context")
        if not context:
            context = '%s/%s'  % (process, basename)


        # find the relative_dir and relative_path
        relative_path = file_path.replace("%s/" % base_dir, "")
        relative_dir = os.path.dirname(relative_path)

        file_name = os.path.basename(file_path)
        log_path = '%s/TACTIC_log.txt' %(base_dir)
        self.create_checkin_log()

        # Define asset type of the file
        asset_type = self.get_asset_type(file_path)
        description = "drop folder check-in of %s" %file_name

        from client.tactic_client_lib import TacticServerStub
        server = TacticServerStub.get(protocol='local')
        server.set_project(project_code)

        transaction = Transaction.get(create=True)
        server.start(title='Check-in of media', description='Check-in of media')

        server_return_value = {}

        try:
            filters = [
                    [ 'name', '=', file_name ],
                    #[ 'relative_dir', '=', relative_dir ]
                ]
            sobj = server.query(search_type, filters=filters, single=True)

            if not sobj:
                # create sobject if it does not yet exist
                sobj = SearchType.create(search_type)
                if SearchType.column_exists(search_type, "name"):
                    sobj.set_value("name", basename)
                if SearchType.column_exists(search_type, "media_type"):
                    sobj.set_value("media_type", asset_type)


                if SearchType.column_exists(search_type, "relative_dir"):
                    sobj.set_value("relative_dir", relative_dir)

                if SearchType.column_exists(search_type, "keywords"):
                    relative_path = relative_path
                    keywords = Common.extract_keywords_from_path(relative_path)
                    keywords = " ".join( keywords )
                    sobj.set_value("keywords", keywords)

                sobj.commit()
                search_key = sobj.get_search_key()
            else:
                search_key = sobj.get("__search_key__")


            #task = server.create_task(sobj.get('__search_key__'),process='publish')
            #server.update(task, {'status': 'New'})
            
            """
            #TEST: simulate different check-in duration
            from random import randint
            sec = randint(1, 5)
            print "checking in for ", sec, "sec"
            server.eval("@SOBJECT(sthpw/login)")
            import shutil
            dir_name,base_name = os.path.split(file_path)
            dest_dir = 'C:/ProgramData/Southpaw/watch_temp'
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            shutil.move(file_path, '%s/%s'%(dest_dir, base_name))
            time.sleep(sec)
            # move back the file in a few seconds 
            shutil.move('%s/%s'%(dest_dir, base_name), file_path)
            """
            server_return_value = server.simple_checkin(search_key,  context, file_path, description=description, mode='move')

            if watch_script_path:
                cmd = PythonCmd(script_path=watch_script_path,search_type=search_type,drop_path=file_path,search_key=search_key)
                cmd.execute()



            
        except Exception as e:
            print "Error occurred", e
            error_message=str(e)

            import traceback
            tb = sys.exc_info()[2]
            stacktrace = traceback.format_tb(tb)
            stacktrace_str = "".join(stacktrace)
            print "-"*50
            print stacktrace_str


            version_num='Error:'
            system_time=strftime("%Y/%m/%d %H:%M", gmtime())
            pre_log=file_name+(50-len(file_name))*' '+system_time+(33-len(system_time))*' '+version_num+(15-len(version_num))*' ' +error_message+'\n'\
                    + stacktrace_str + '\n' + watch_script_path
            # Write data into TACTIC_log file under /tmp/drop
            f = open(log_path, 'a')
            f.write(pre_log)
            f.close()

            #server.abort()
            transaction.rollback()
            raise
        
        else:
            transaction.commit()
        
        #server.finish()

        if server_return_value:
            # Create the TACTIC_log file to record every check-in. 
            # Search for all required data
            checkin_time=server_return_value.get('timestamp')
            version_nu=server_return_value.get('version')
            version_num=str(version_nu)
            try:
                value = parser.parse(checkin_time)
                value = value.strftime("%Y/%m/%d %H:%M")
            except:
                value = checkin_time

            pre_log=file_name+(50-len(file_name))*' '+value+(33-len(value))*' '+version_num+(15-len(version_num))*' ' +'ok\n'      
            # Write data into TACTIC_log file under /tmp/drop
            f = open(log_path, 'a')
            f.write(pre_log)
            f.close()

            # Invoke Trigger:called_triggers
            from pyasm.command import Trigger
            Trigger.call_all_triggers()

            # Delete the source file after check-in step.
            print "File handled."
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    os.rmdirs(file_path)
                else:
                    os.unlink(file_path)
                print "Source file [%s] deleted: " %file_name







class WatchDropFolderTask(SchedulerTask):

    def __init__(self, **kwargs):

        self.input_kwargs = kwargs
        self.base_dir = kwargs.get("base_dir")
        self.site = kwargs.get("site")
        self.project_code = kwargs.get("project_code")
        self.search_type = kwargs.get("search_type")
        self.process = kwargs.get("process")
        self.script_path = kwargs.get("script_path")
        self.watch_folder_code = kwargs.get("watch_folder_code")

        super(WatchDropFolderTask, self).__init__()

        self.checkin_paths = []
        self.in_clean_mode = False

        self.files_checked = 0

    def add_path(self, path):
        self.checkin_paths.append(path)

    def get_paths(self):
        return self.checkin_paths


    def get(self, key):
        return self.input_kwargs.get(key)


    def set_clean(self, clean):
        self.in_clean_mode = clean

    def in_clean(self):
        return self.in_clean_mode

    def _execute(self):

        base_dir = self.base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        dirs = os.listdir(base_dir)
        test_dirs = dirs[:]
        for dirname in test_dirs:
            base, ext = os.path.splitext(dirname)
            if ext in [".lock", ".error", ".checkin"]:
                dirs.remove(dirname)

                try:
                    dirs.remove(base)
                except:
                    pass

        if not dirs:
            return

        # skip certain files like log
        dir_set = set(dirs)
        for dirname in dirs:
            if dirname.startswith("TACTIC_log"):
                dir_set.remove(dirname)
            if dirname.startswith("."):
                dir_set.remove(dirname)
        dirs = list(dir_set)

        if not dirs:
            return

        

        # go thru the list to check each file
        for file_name in dirs:
            file_path = '%s/%s' %(self.base_dir, file_name)
            if file_path in self.get_paths():
                continue
            thread = WatchFolderCheckFileThread(
                    task=self,
                    path=file_path
                    )
            thread.daemon = True
            thread.start()

            #print "count: ", threading.active_count()


    def execute(self):

        base_dir = self.base_dir
        if not base_dir:
            print "WARNING: No base dir defined."
            return

        # Start action thread
        checkin = WatchFolderFileActionThread(
                task=self,
        )
        checkin.start()

        # execute and react based on a loop every second
        mode = "loop"
        if mode == "loop":
            while True:
                self._execute()
                time.sleep(1)


        elif mode == "event":

            try:
                event_handler = TestLoggingEventHandler()
                observer = Observer()

                print "base: ", self.base_dir
                path = self.base_dir
                observer.schedule(event_handler, path=path, recursive=True)
                observer.start()

            except Exception as e:
                print "... skipping: ", e
                raise

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                for observer in observers:
                    observer.stop()






    def start(cls):

        print "Running Watch Folder ..."



        # Check whether the user define the drop folder path.
        # Default dop folder path: /tmp/drop
        parser = OptionParser()
        parser.add_option("-p", "--project", dest="project", help="Define the project_name.")
        parser.add_option("-d", "--drop_path", dest="drop_path", help="Define drop folder path")
        parser.add_option("-s", "--search_type", dest="search_type", help="Define search_type.")
        parser.add_option("-P", "--process", dest="process", help="Define process.")
        parser.add_option("-S", "--script_path",dest="script_path", help="Define script_path.")
        parser.add_option("-w", "--watch_folder_code",dest="watch_folder_code", 
				help="Define watch folder code. If no code is used, then it assumed that this process \
				is managed in a standalone script.")
        parser.add_option("-x", "--site",dest="site", help="Define site.")

        parser.add_option("-c", "--handler",dest="handler", help="Define Custom Handler Class.")
        (options, args) = parser.parse_args()

        



        if options.project != None :
            project_code= options.project
        else:
            raise Exception("No project specified")


        if options.drop_path!=None :
            drop_path= options.drop_path
        else:
            tmp_dir = Environment.get_tmp_dir()
            drop_path = "%s/drop" % tmp_dir
        print "    using [%s]" % drop_path
        if not os.path.exists(drop_path):
            os.makedirs(drop_path)

        if options.search_type!=None :
            search_type = options.search_type
        else:
            search_type = None


        if options.process!=None :
            process = options.process
        else:
            process= 'publish'

        if options.script_path != None :
            script_path = options.script_path
        else:
            script_path = None
          
        if options.site != None:
            site = options.site
        else:
            site = None

        if options.handler != None:
            handler = options.handler
        else:
            handler = None

        if options.watch_folder_code != None:
            watch_folder_code = options.watch_folder_code
        else:
            watch_folder_code = None
        if watch_folder_code:   
            # record pid in watch folder pid file
            pid = os.getpid()
            pid_file = "%s/log/watch_folder.%s" % (Environment.get_tmp_dir(), watch_folder_code)
            f = open(pid_file, "w")
            f.write(str(pid))
            f.close()

        Batch(project_code=project_code, site=site)



        task = WatchDropFolderTask(
            base_dir=drop_path, 
            site=site, 
            project_code=project_code,
            search_type=search_type, 
            process=process,
            script_path=script_path, 
            handler=handler,
            watch_folder_code=watch_folder_code
        )
        
        scheduler = Scheduler.get()
        scheduler.add_single_task(task, delay=1)
        scheduler.start_thread()
        return scheduler
    start = classmethod(start)

if __name__ == '__main__':
    WatchDropFolderTask.start()
    while 1:
        try:
            time.sleep(15)
        except (KeyboardInterrupt, SystemExit), e:
            scheduler = Scheduler.get()
            scheduler.stop()
            break



