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

__all__ = ["BaseCache", "SearchTypeCache", "CacheContainer", "CustomCache"]

import tacticenv

import sys, time, datetime, types
from dateutil import parser

from pyasm.common import Container

from pyasm.search import SObject, Search, SearchType, SearchKey

CACHE = {}


class BaseCache(object):
    def __init__(self, key, register=True):
        self.mtime = None
        self.key = key
        self.caches = {}

        self.init_cache()

        if register:
            CacheContainer.add(key, self)



    def init_cache(self):
        '''initialize the cache'''
        self.mtime = datetime.datetime.now()


    def get_value_by_key(self, cache_name, key):
        cache = self.caches.get(cache_name)
        if cache == None:
            return None
        value = cache.get(key)
        return value

    def get_cache(self, cache_name):
        cache = self.caches.get(cache_name)
        return cache


    def get_mtime(self):
        return self.mtime


    def get_refresh_events(self):
        return []



    def make_dirty(self):
        '''function to make the cache dirty.  All proceses will compare this
        change time with their internal time and update the cache if necessary
        '''
        dirty = Search.eval("@SOBJECT(sthpw/cache['key','%s'])" % self.key, single=True)
        if not dirty:
            dirty = SearchType.create("sthpw/cache")

        dirty.set_value("key", self.key)
        now = datetime.datetime.now()
        dirty.set_value("mtime", now)
        dirty.commit(triggers=False)


    def is_dirty(self):
        '''function check to see if this cache is dirty'''
        cache_sobj = Search.eval("@SOBJECT(sthpw/cache['key','%s'])" % self.key, single=True)
        if not cache_sobj:
            return False

        dirty_time = cache_sobj.get_value("mtime")
        dirty_time = parser.parse(dirty_time)

        if self.mtime <= dirty_time:
            return True
        else:
            return False


    def get(cls, search_type):
        # TODO: make this thread safe
        cache = CacheContainer.get(search_type)
        if cache == None:
            # create a new instances of the Search Type cache
            cache = cls(search_type)
            CacheContainer.add(search_type, cache)

        return cache
    get = classmethod(get)




class SearchTypeCache(BaseCache):
    '''Generic class to cache an entire table
    There should only be one of these for each search type.  It is used
    for data that does not change much and is much faster to have
    cached in memory
    '''
    def __init__(self, search_type):
        self.search_type = search_type
        self.sobjects = []

        super(SearchTypeCache,self).__init__(search_type)


    def init_cache(self):
        '''initialize the cache'''
        self.mtime = datetime.datetime.now()

        keys = self.caches.keys()
        self.caches = {}

        search = Search(self.search_type)
        search.set_show_retired(True)
        self.sobjects = search.get_sobjects()


        # build a search_key cache
        search_key_cache = {}
        search_keys = SearchKey.get_by_sobjects(self.sobjects)
        for search_key, sobject in zip(search_keys, self.sobjects):
            search_key_cache[search_key] = sobject
        self.caches['search_key'] = search_key_cache

        code_cache = {}
        for sobject in self.sobjects:
            code = sobject.get_code()
            code_cache[code] = sobject
        self.caches['code'] = code_cache 

        for key in keys:
            if key in ['search_key', 'code']:
                continue
            self.build_cache_by_column(key)


    def get_refresh_events(self):
        events = [
            "change|%s" % self.search_type,
        ]
        return events



    def build_cache_by_column(self, column):
        # do not build if it already exists
        if self.caches.has_key(column):
            return

        # build a search_key cache
        column_cache = SObject.get_dict(self.sobjects, key_cols=[column])
        self.caches[column] = column_cache
        return column_cache

    def get_sobjects(self):
        return self.sobjects


    def add_cache(self, key, cache):
        self.caches[key] = cache
        
    def get_cache_by_key(self, key):
        cache = self.caches.get(key)
        return cache

    def get_sobject_by_key(self, cache_name, key):
        cache = self.caches.get(cache_name)
        if not cache:
            return None
        sobject = cache.get(key)
        return sobject


    def add_sobject_to_cache(self, sobject):
        '''add an sobject to the cache.  This is useful if a new sobject
        has been inserted and it is too expensive to have to recache the entire
        table just for this one entry'''

        # make sure this sobject's search type is the same as the search type 
        # for this cache
        search_type = sobject.get_base_search_type()
        assert search_type == self.search_type


        # FIXME: add to all of the caches
        for key, cache in self.caches.items():
            if key == 'search_key':
                # add to the search_key cache
                search_key = SearchKey.get_by_sobject(sobject)
                cache[search_key] = sobject

            elif key == 'code':
                # add to the code cache
                code = sobject.get_code()
                cache[code] = sobject

            else:
                value = sobject.get_value(key)
                cache[value] = sobject

        # make sure this cache is set to dirty so other processes update
        self.make_dirty()




    def get(cls, search_type):
        # TODO: make this thread safe
        cache = CacheContainer.get(search_type)
        if cache == None:
            # create a new instances of the Search Type cache
            cache = cls(search_type)

        return cache
    get = classmethod(get)



class CustomCache(BaseCache):

    def __init__(self, key=None, action=None):
        self.action = action

        super(CustomCache,self).__init__(key)


    # We have to somehow remember how to recache ... pass in a rehash function
    def init_cache(self):
        '''do the cache'''
        self.mtime = datetime.datetime.now()
        self.caches = self.action()
        assert type(self.caches) == types.DictType



 
class CacheContainer(object):

    def add(key, cache):
        CACHE[key] = cache

        # when adding a new event, register its events
        events = cache.get_refresh_events()

        from pyasm.command import Trigger
        for event in events:
            #print "registering: ", event
            trigger = SearchType.create("sthpw/trigger")
            trigger.set_value("event", event)
            trigger.set_value("class_name", "pyasm.command.SearchTypeCacheTrigger")
            Trigger.append_static_trigger(trigger)



    add = staticmethod(add)


    def get_dirty():
        '''method to get all of the dirty caches'''
        caches = Search.eval("@SOBJECT(sthpw/cache)")
        if not caches:
            return []

        dirty_caches = []
        for cache_sobj in caches: 
            dirty_time = cache_sobj.get_value("mtime")
            dirty_time = parser.parse(dirty_time)

            key = cache_sobj.get_value("key")

            cache = CacheContainer.get(key)
            if not cache:
                print "WARNING: Cache [%s] does not exist in memory" % key
                continue

            mtime = cache.get_mtime()

            if mtime <= dirty_time:
                dirty_caches.append(cache_sobj)

        return dirty_caches

    get_dirty = staticmethod(get_dirty)


    def get_all():
        '''method to get all database cache sobjects'''
        return Search.eval("@SOBJECT(sthpw/cache)")
    get_all = staticmethod(get_all)


    def get_all_caches():
        '''method to get all in memory caches'''
        return CACHE
    get_all_caches = staticmethod(get_all_caches)


    def get(cls, key):
        return CACHE.get(key)
    get = classmethod(get)




