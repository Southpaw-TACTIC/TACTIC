###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ["Cache", "CacheTrigger"]

import tacticenv

import sys,time

from pyasm.common import Container
from pyasm.search import Search, SearchType
from pyasm.command import Trigger, Command


class CacheList(object):
    '''Generic caching class'''

    def __init__(my):
        
        # on startup, build all of the cache objects and remember the timestamp
        my.caches = {}
        my.mtimes = {}


    def get_cache(my, key):
        cache = my.caches.get(key)
        return cache
        
        

    def set_cache(my, key, cache):
        my.caches[key] = cache
        now = time.time()
        my.mtimes[key] = now


    def check(my):
        
        for key, mtime in my.mtimes.items():

            # get all of the dirty values (where keys have modification values
            # greter than mtime of the key
            search = Search("sthpw/cache")
            search.add_filter(key)
            search.add_filter('''"mtime" > %s''' % mtime)
            dtime = search.get_sobject()

            if dtime:
                print "re-caching ..."
                cache = my.caches[key]
                cache.cache()

                now = time.time()
                my.mtimes[key] = now


        for key, mtime in my.mtimes.items():
            print key, mtime, now - mtime


    def get():
        key = 'CacheList'
        cache_list = Container.get(key)
        if not cache_list:
            cache_list = CacheList()
            Container.put(key, cache_list)
        return cache_list
    get = staticmethod(get)


    def get_cache_by_key(key):
        cache_list = CacheList.get()
        return cache_list.get_cache(key)
    get_cache_by_key = staticmethod(get_cache_by_key)




class Cache(object):
    '''Generic caching class'''

    def __init__(my, key):
        my.key = key
        my.attrs = {}

        my.cache()


    def cache(my):

        # get the value from cache
        from pyasm.biz import ExpressionParser
        parser = ExpressionParser()
        logins = parser.eval("@SOBJECT(sthpw/login)")

        my.attrs[my.key] = logins


    def get_key(my):
        return my.key


    def make_dirty(my):
        dirty = SearchType.create("sthpw/cache")
        dirty.set_value("key", my.key)
        dirty.set_now("mtime")
        dirty.commit()


    def get_attr(my, key):
        return my.attrs.get(key)



    def get_events(my):
        # set an event to listen for to update caches
        return [
            "change|sthpw/login"
        ]



    def get(key):
        # in usage, you get it from the cache list
        cache_list = CacheList.get()

        cache = cache_list.get_cache(key)
        if not cache:
            cache = Cache(key)
            
            # store the cache in the container
            cache_list.set_cache(key, cache)
        return cache

    get = staticmethod(get)



class CacheTrigger(Trigger):

    #def set_cache(my, cache):
    #    my.cache = cache

    def execute(my):
        print "running cache trigger"
        cache = Cache.get("logins")
        cache.make_dirty()



class TestCommand(Command):

    def execute(my):

        # get the cache list
        login_cache = Cache.get("logins")
        logins = login_cache.get_attr("logins")
        print logins



        # in memory triggers?
        events = login_cache.get_events()
        for event in events:
            trigger_sobj = SearchType.create("sthpw/trigger")
            trigger_sobj.set_value("event", event)
            trigger_sobj.set_value("class_name", "pyasm.search.cache.CacheTrigger")
            Trigger.append_static_trigger(trigger_sobj)


        login = logins[0]
        print "email [%s]" % login.get_value("email")
        login.set_value("email", "remko@southpawtech.com")
        print "email [%s]" % login.get_value("email")
        login.commit()

        #dsaasf




if __name__ == '__main__':

    from pyasm.security import Batch
    Batch(project_code='MMS')

    cmd = TestCommand()
    Command.execute_cmd(cmd)



