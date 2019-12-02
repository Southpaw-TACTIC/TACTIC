###########################################################
#
# Copyright (c) 2005-2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['CacheStartup', 'TableInfoCache']

import tacticenv

from pyasm.common import Config, Common, Container, GlobalContainer
from pyasm.search import DbContainer, DatabaseImpl, DbResource
from tactic.command import Scheduler, SchedulerTask
from pyasm.security import Batch
from pyasm.biz import BaseCache, CacheContainer, SearchTypeCache

import time

STHPW_TABLES = ['project', 'search_object', 'login', 'login_group', 'login_in_group','snapshot','file','trigger','notification','ticket', 'task', 'task', 'status_log', 'pref_setting', 'cache', 'transaction_log', 'change_timestamp']

# custom cache class
class TableInfoCache(BaseCache):
    def __init__(self, **kwargs):
        self.database = kwargs.get("database")
        self.tables = kwargs.get("tables") or []

        self.db_resource = kwargs.get("db_resource")
        if not self.db_resource:
            self.db_resource = DbResource.get_default(self.database)

        if not kwargs.get("key") and self.db_resource:
            self.key = str(self.db_resource)
        else:
            self.key = kwargs.get("key")

        super(TableInfoCache, self).__init__(self.key)


        # precache some of the sthpw tables
        if not self.tables and  self.db_resource.get_database() == "sthpw":
            self.tables = STHPW_TABLES



    def init_cache(self):

        data = {}
        self.caches['data'] = data
        columns = {}
        self.caches['columns'] = columns

        for table in self.tables:
            DatabaseImpl.get().get_column_info(self.db_resource, table)



    def add_table(self, table, column_data):
        data = self.caches['data']
        data[table] = column_data

        sql = self.db_resource.get_sql()
        columns = self.caches['columns']
        column_list = sql.get_columns(table)
        columns[table] = column_list



class CacheStartup(object):
    '''do a bunch of caching on startup of the web process'''

    def __init__(self, mode='complete'):
        '''Windows uses basic mode'''
        self.mode = mode

    def execute(self):
        if self.mode == 'basic':
            return


        from pyasm.search import DbResource
        db_resource = DbResource.get_default("sthpw")

        # pre-cache sthpw tables definitions
        kwargs = {
            "db_resource": db_resource,
            "tables": STHPW_TABLES
        }
        cache = TableInfoCache( **kwargs )




        from pyasm.security import Sudo
        sudo = Sudo()
        try:

            # cache search object table
            search_type_cache = SearchTypeCache.get("sthpw/search_object")
            search_type_cache.build_cache_by_column("search_type")

            # cache login table
            search_type_cache = SearchTypeCache.get("sthpw/login")
            search_type_cache.build_cache_by_column("login")

            # cache login_group table
            search_type_cache = SearchTypeCache.get("sthpw/login_group")
            search_type_cache.build_cache_by_column("login_group")

            # DISABLING this ... needs to be written often and is large
            #search_type_cache = SearchTypeCache.get("sthpw/ticket")
            #search_type_cache.build_cache_by_column("ticket")
        finally:
            sudo.exit()




    def init_scheduler(self):

        scheduler = Scheduler.get()

        if self.mode == 'basic':
            self.start_basic_tasks(scheduler)
        else:
            self.start_cache_tasks(scheduler)
            self.start_basic_tasks(scheduler)

        print("Starting Scheduler ....")
        scheduler.start_thread()

    def start_cache_tasks(self, scheduler):

        
        # do a dirty check every X seconds
        class DirtyTask(SchedulerTask):
            def execute(self):
                #Batch()

                dirty_caches = CacheContainer.get_dirty()
                for dirty_cache in dirty_caches:
                    key = dirty_cache.get_value("key")
                    #print("... caching: ", key)
                    cache = CacheContainer.get(key)
                    if not cache:
                        print("WARNING: cache [%s] does not exist in memory" % key)
                        continue

                    cache.init_cache()

                DbContainer.commit_thread_sql()
                DbContainer.close_all()

        task = DirtyTask()
        interval = 30
        scheduler.add_interval_task(task, interval=interval, mode='threaded', delay=10)

        # do a full cache refresh every 180 seconds
        class RefreshTask(SchedulerTask):
            def execute(self):
                start = time.time()
                #Batch()

                #print("refresh caches ...")
                caches = CacheContainer.get_all_caches()
                for key, cache in caches.items():
                    #print("... %s" % key, cache)
                    cache.init_cache()
                #print("... %s seconds" % (time.time() - start))

                DbContainer.commit_thread_sql()
                DbContainer.close_all()

        task = RefreshTask()
        interval = 600 
        scheduler.add_interval_task(task, interval=interval, mode='threaded', delay=30)


    def start_basic_tasks(self, scheduler):

        # close all extraneous database connections 15 minutes
        class DatabaseCloseTask(SchedulerTask):
            def execute(self):
                #print("Closing all connections")
                DbContainer.close_all_global_connections()

        task = DatabaseCloseTask()
        interval = 15*60
        scheduler.add_interval_task(task, interval=interval, mode='threaded', delay=60)



        # Kill cherrypy every interval.  This overcomes some of the memory
        # problems with long running Python processes.  In order to
        # use this properly, it is essential that a load balancer with
        # proper failover is used
        #
        class KillTacticTask(SchedulerTask):
            def execute(self):
                # wait until KillThread is premitted
                while GlobalContainer.get("KillThreadCmd:allow") == "false":
                    print("Kill locked ... waiting 5 seconds")
                    time.sleep(5)
                    continue

                import cherrypy
                print("\n")
                print("Stopping TACTIC ...")
                print("\n")
                print(" ... stopping Schduler")
                scheduler = Scheduler.get()
                scheduler.stop()
                print(" ... stopping Cherrypy")
                cherrypy.engine.stop()
                cherrypy.engine.exit()
                print(" ... closing DB connections")
                DbContainer.close_all_global_connections()
                print(" ... kill current process")
                Common.kill()
                print("Done.")



        from .web_container import WebContainer

        if not WebContainer.is_dev_mode():
            task = KillTacticTask()
            config_delay = Config.get_value("services", "process_time_alive")
            if config_delay:
                # put in a randomizer so that not all processes die at once
                delay = int(config_delay)
                offset = Common.randint(0, delay) - delay/2
                delay += offset
                seconds = int(delay * 60)
                print("Process will exit in [%s] seconds" % seconds)
                scheduler.add_single_task(task, mode='sequential', delay=seconds)


        

if __name__ == '__main__':
    Batch(project_code='cg')
    cmd = CacheStartup()
    cmd.execute()
    cmd.init_scheduler()

    try:
        import time
        time.sleep(600)
    except KeyboardInterrupt:
        scheduler = Scheduler.get()
        scheduler.stop()

    cache = CacheContainer.get("sthpw_column_info")
    print("cache value: ", cache.get_value_by_key('data', 'login'))







