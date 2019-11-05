#!/usr/bin/env python3

# This is a simple command line script that can be used to backup the
# TACTIC database.  It is independent of TACTIC, so can be run on
# servers where TACTIC is not install with the database.

import datetime
import os
import time
import subprocess

import tacticenv
from pyasm.common import Environment
from pyasm.security import Batch

# Location of zip executable
#ZIP_EXE = "C:\\Users\\user\\Documents\\backups\\7za920\\7za.exe"
ZIP_EXE = "zip"
# Location of all back-up types
BACKUP_DIR = "/spt/tactic/tactic_temp/"
# Locations of different backup types 
DB_DIR = "backup_db"
PROJECT_DIR = "backup_tactic"
ASSETS_DIR = "backup_assets"
# Location of TACTIC src code
TACTIC_DIR = "/spt/tactic/tactic/"

class DatabaseBackup(object):
    
    def execute(my):
        base_dir = "%s%s" % (BACKUP_DIR, DB_DIR)

        import datetime
        now = datetime.datetime.now()
        date = now.strftime("%Y%m%d_%H%M")
        
        file_name = 'tacticDatabase_%s.sql' % date
        path = "%s/%s" % (base_dir, file_name)

        print("Backing up database to: [%s]" % path)

        # Check if base_dir is exists and writable.
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        
        # Create backup, and if successful, prune old
        # backups.
        try:
            cmd = 'pg_dumpall -U postgres -c > %s' % path
            os.system(cmd)            
        except Exception as e:
            print("Could not run database backup: %s" % e)
        else:
            cmd = PruneBackup()
            cmd.execute(base_dir, 30)   
            
            #cmd = 'gzip -f %s' % path
            #os.system(cmd)


class ProjectBackup(object):

    def execute(my):
        base_dir = "%s%s" % (BACKUP_DIR, PROJECT_DIR)
        
        zip_exe = ZIP_EXE
       
        now = datetime.datetime.now()
        date = now.strftime("%Y%m%d_%H%M")
        file_path = '%s/tactic_%s.zip' % (base_dir, date)
        
        # Check if base_dir is exists and writable.
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        
        # Create backup, and if successful, prune old
        # backups.
        try:
            subprocess.call([zip_exe, "-r", file_path, TACTIC_DIR])    
        except Exception as e:
            print("Could not zip project directory. %s" % e)
        else:
            cmd = PruneBackup()
            cmd.execute(base_dir, 1)

                
class AssetsBackup(object):

    def execute(my):
        base_dir = "%s%s" % (BACKUP_DIR, ASSETS_DIR)
        asset_dir = Environment.get_asset_dir()
        
        zip_exe = ZIP_EXE
        
        now = datetime.datetime.now()
        date = now.strftime("%Y%m%d_%H%M")
        file_path = '%s/assets_%s.zip' % (base_dir, date)
        
        # Check if base_dir is exists and writable.
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        
        # Create backup, and if successful, prune old
        # backups.
        try:
            subprocess.call([zip_exe, "-r", file_path, asset_dir])        
        except Exception as e:
            print("Could not zip assets directory: %s" % e)
        else:
            cmd = PruneBackup()
            cmd.execute(base_dir, 3)

class PruneBackup(object):
    def execute(my, directory, days):
        '''Removes files in directory older than specified days.'''
        dir = directory

        print("Pruning backup files older than [%s] days" % days)

        import datetime
        today = datetime.datetime.today()
        files = os.listdir(dir)
        for file in files:
            path = "%s/%s" % (dir, file)

            (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
            ctime = datetime.datetime.fromtimestamp(ctime)
            if today - ctime > datetime.timedelta(days=days):
                os.unlink(path)
                
                
if __name__ == '__main__':  
    
    '''
    # TODO
    os.system("vacuumdb -U postgres --all --analyze")
    '''

    Batch()

    cmd = DatabaseBackup()
    cmd.execute()
        
    cmd = AssetsBackup()
    cmd.execute()
    
    cmd = ProjectBackup()
    #cmd.execute()
    
