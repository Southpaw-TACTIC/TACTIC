
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
import time, hashlib, os, shutil, sys
import os.path
import sys

from dateutil import parser
from pyasm.common import Environment, Config
from pyasm.security import Batch
from pyasm.biz import Project
from pyasm.search import DbContainer
from pyasm.search import Search, Transaction, SearchType
from pyasm.command import Command
from tactic.command import SchedulerTask, Scheduler
from time import gmtime, strftime
from optparse import OptionParser

import threading


from pyasm.common import WatchFolder

class WatchFolderCheckin(WatchFolder):

    def on_moved(self, event):

        src_path = event.src_path
        dest_path = event.dest_path
        print "src_path: ", src_path

        # this file should be in the relative path
        upload_dir = self.upload_dir
        print "upload_dir: ", upload_dir

        basename = os.path.basename(dest_path)
        dirname = os.path.dirname(dest_path)
        rel_dir = dirname.replace("%s" % upload_dir, "")
        print "rel_dir: ", rel_dir
        print "---"


class WatchFolderCheckinThread(threading.Thread):

    def __init__(my, **kwargs):
        my.kwargs = kwargs
        super(WatchFolderCheckinThread, my).__init__()

        path = my.kwargs.get("path")
        my.lock_path = "%s.lock" % path
        my.error_path = "%s.error" % path


        if os.path.exists(my.lock_path):
            raise Exception()

        f = open(my.lock_path, "w")
        f.close()

    def run(my):
        path = my.kwargs.get("path")

        try:

            changed = my.verify_file_size(path)
            print " .... changed: ", changed

            if changed:
                return

            task = my.kwargs.get("task")
            task.checkin(path)


        except Exception, e:
            print "Error: ", e
            f = open(my.error_path, "w")
            f.write(str(e))
            f.close()
            raise
        finally:
            if os.path.exists(my.lock_path):
                os.unlink(my.lock_path)



    def verify_file_size(my, file_path):
        '''Check if the file size changes over a period of 5 seconds. If so, file is not ready'''
        # Chech whether the file_path exists or not. Once the file is ready, the or
        if not os.path.exists(file_path):
            return False

        changed = False
        for i in range(0, 5):
            file_size=os.path.getsize(file_path)
            time.sleep(2)
            if not os.path.exists(file_path):
                changed = True
                break

            file_size_check=os.path.getsize(file_path)
            if file_size != file_size_check:
                changed = True
                break

        return changed


class WatchDropFolderTask(SchedulerTask):

    def __init__(my, **kwargs):

        print "Check-in script is Running..."
        my.last_md5 = None
        my.last_dir_set = None

        my.base_dir = kwargs.get("base_dir")
        my.project_name = kwargs.get("project_name")
        my.search_type = kwargs.get("search_type")

        super(WatchDropFolderTask, my).__init__()
        # find out all of the jobs in the queue that are not in the
        # database
        #my.init()

    def is_image(my, file_name):
        base, ext = os.path.splitext(file_name)
        ext = ext.lstrip(".").lower()
        if ext in ['tif','tiff','jpg','jpeg','png','pic','bmp','gif','psd']:
            return True
        else:
            return False

    def is_movie(my, file_name):
        base, ext = os.path.splitext(file_name)
        ext = ext.lstrip(".").lower()
        if ext in ['mov','wmv','mpg','mpeg','m1v','mp2','mpa','mpe','mp4','wma','asf','asx','avi','wax','wm','wvx']:
            return True
        else:
            return False

    def get_asset_type(my, file_path):
        if my.is_movie(file_path):
            return 'movie'
        elif my.is_image(file_path):
            return 'image'
        else:
            return 'other'

    def create_checkin_log(my):
        log_path = '%s/TACTIC_log.txt' %(my.base_dir)
        if not (os.path.isfile(log_path)):
            file = open(log_path, 'w')   
            title='File Name'+40*' '+'Checkin-Time'+20*' '+'Version#'+6*' ' +'Message\n'
            f = open(log_path, 'a')
            f.write(title)
            f.close()

            
    def init(my):

        base_dir = my.base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        print "base_dir: ", base_dir

        dirs = os.listdir(base_dir)
        test_dirs = dirs[:]
        for dirname in test_dirs:
            if dirname.endswith(".lock") or dirname.endswith(".error"):
                dirs.remove(dirname)

        print "dirs: ", dirs

        # skip certain files like log
        dir_set = set(dirs)
        for dirname in dirs:

            if dirname.startswith("TACTIC_log"):
                dir_set.remove(dirname)
        dirs = list(dir_set)

        tmp_set = set(dirs)
        dirs_set = set()
        dirs_dict = {}
        image_list = []
        movie_list = []
        other_list = []

        # these are probably files in this demo
        for dir in tmp_set:
            if dir.startswith("."):
                continue
            elif my.is_image(dir):
                image_list.append(dir)
            elif my.is_movie(dir):
                movie_list.append(dir)
            else:
                other_list.append(dir)

        # start a bunch of threads for each file which will apply the check
        # algorithm


        # go thru the list to check in  
        for file_list in [image_list, movie_list, other_list]:
            for file_name in file_list:

                file_path = '%s/%s' %(my.base_dir, file_name)
                print "file_path: ", file_path

                try:
                    thread = WatchFolderCheckinThread(
                            task=my,
                            path=file_path
                            )
                    thread.start()
                except Exception, e:
                    print "... Locked"

                #if not my.verify_file(file_path):
                #    continue
                #my.checkin(file_path)


    def verify_file(my, file_path):
        return my.verify_file_size(file_path)


    def verify_file_size(my, file_path):
        '''Check if the file size changes over a period of 5 seconds. If so, file is not ready'''
        # Chech whether the file_path exists or not. Once the file is ready, the or
        if not os.path.exists(file_path):
            return False
        file_size=os.path.getsize(file_path)
        time.sleep(5)
        if not os.path.exists(file_path):
            return False
        file_size_check=os.path.getsize(file_path)
        if file_size!=file_size_check:
            return False
        return True


    def checkin(my, file_path):
        context = 'publish' 
        file_name = os.path.basename(file_path)
        log_path = '%s/TACTIC_log.txt' %(my.base_dir)
        my.create_checkin_log()

        # Define asset type of the file
        asset_type = my.get_asset_type(file_path)
        description = "drop folder check-in of %s" %file_name
        from client.tactic_client_lib import TacticServerStub
        server = TacticServerStub.get(protocol='local')

        server.set_project(my.project_name)

        # Set up the basic check-in step
        sobj = server.query(my.search_type, filters=[['name', 'EQ', '^%s'%file_name]], single=True)

        if sobj and sobj.get('occupied') == True:
            print "The media item [%s] 'occupied' state is set to True now. Will check again later." %sobj.get('name')
            return


        transaction = Transaction.get(create=True)
        server.start(title='Check-in of media', description='Check-in of media')

        # occupied prevents a long-running checkin from being detected as a brand-new file
        if not sobj:
            sobj = server.insert(my.search_type, {'name': file_name, 'asset_type': asset_type, 'occupied': True})
        else:
            sobj = server.update(sobj, {'occupied': True})

        
        server_return_value = {}

        try:
            if not sobj:
                # TODO: add pipeline_code
                #sobj = server.insert('viacom/media', {'name': file_name, 'asset_type': asset_type})
                task = server.create_task(sobj.get('__search_key__'),process='publish')
                server.update(task, {'status': 'New'})

            server_return_value = server.simple_checkin(sobj.get('__search_key__'),  context, file_path, description=description, mode='copy')
            
        except Exception, e:
            print "Error occurred", e
            error_message=str(e)
            version_num='Error:'
            system_time=strftime("%Y/%m/%d %H:%M", gmtime())
            pre_log=file_name+(50-len(file_name))*' '+system_time+(33-len(system_time))*' '+version_num+(15-len(version_num))*' ' +error_message+'\n'      
            # Write data into TACTIC_log file under /tmp/drop
            f = open(log_path, 'a')
            f.write(pre_log)
            f.close()

            #server.abort()
            transaction.rollback()
        
        finally:
            if sobj:
                sobj = server.update(sobj, {'occupied': False})

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

            # Delete the sourse file after check-in step.
            print "File checked in. Source file [%s] deleted: " %file_name
            os.unlink(file_path)

    def execute(my):
        Batch()
        base_dir = my.base_dir
        if not base_dir:
            print "WARNING: No base dir defined."
            return
        my.init()

    def start(cls):
        # Check whether the user define the drop folder path.
        # Default dop folder path: /tmp/drop
        parser = OptionParser()
        parser.add_option("-p", "--project_name", dest="project_name", help="Define the project_name. Default:Viacom")
        parser.add_option("-d", "--drop_path", dest="drop_path", help="Define drop folder path. Default:/tmp/drop")
        parser.add_option("-s", "--search_type", dest="search_type", help="Define search_type.")
        (options, args) = parser.parse_args()

        if options.project_name!=None :
            project_name= options.project_name
        else:
            project_name= 'viacom'

        if options.drop_path!=None :
            drop_path= options.drop_path
        else:
            drop_path= '/tmp/drop'

        if options.search_type!=None :
            search_type= options.drop_path
        else:
            search_type= 'viacom/media'

        task = WatchDropFolderTask(base_dir=drop_path, project_name=project_name,search_type=search_type)
        
        scheduler = Scheduler.get()
        scheduler.add_interval_task(task, 30, delay=0)
        scheduler.start_thread()
        return scheduler
    start = classmethod(start)

if __name__ == '__main__':
    Batch()
    WatchDropFolderTask.start()
    while 1:
        try:
            time.sleep(15)
        except (KeyboardInterrupt, SystemExit), e:
            scheduler = Scheduler.get()
            scheduler.stop()
            break




