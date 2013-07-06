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
    def __init__(my, key, register=True):
        my.mtime = None
        my.key = key
        my.caches = {}

        my.init_cache()

        if register:
            CacheContainer.add(key, my)



    def init_cache(my):
        '''initialize the cache'''
        my.mtime = datetime.datetime.now()


    def get_value_by_key(my, cache_name, key):
        cache = my.caches.get(cache_name)
        if cache == None:
            return None
        value = cache.get(key)
        return value

    def get_cache(my, cache_name):
        cache = my.caches.get(cache_name)
        return cache


    def get_mtime(my):
        return my.mtime


    def get_refresh_events(my):
        return []



    def make_dirty(my):
        '''function to make the cache dirty.  All proceses will compare this
        change time with their internal time and update the cache if necessary
        '''
        dirty = Search.eval("@SOBJECT(sthpw/cache['key','%s'])" % my.key, single=True)
        if not dirty:
            dirty = SearchType.create("sthpw/cache")

        dirty.set_value("key", my.key)
        now = datetime.datetime.now()
        dirty.set_value("mtime", now)
        dirty.commit(triggers=False)


    def is_dirty(my):
        '''function check to see if this cache is dirty'''
        cache_sobj = Search.eval("@SOBJECT(sthpw/cache['key','%s'])" % my.key, single=True)
        if not cache_sobj:
            return False

        dirty_time = cache_sobj.get_value("mtime")
        dirty_time = parser.parse(dirty_time)

        if my.mtime <= dirty_time:
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
    def __init__(my, search_type):
        my.search_type = search_type
        my.sobjects = []

        super(SearchTypeCache,my).__init__(search_type)


    def init_cache(my):
        '''initialize the cache'''
        my.mtime = datetime.datetime.now()

        keys = my.caches.keys()
        my.caches = {}

        search = Search(my.search_type)
        search.set_show_retired(True)
        my.sobjects = search.get_sobjects()


        # build a search_key cache
        search_key_cache = {}
        search_keys = SearchKey.get_by_sobjects(my.sobjects)
        for search_key, sobject in zip(search_keys, my.sobjects):
            search_key_cache[search_key] = sobject
        my.caches['search_key'] = search_key_cache

        code_cache = {}
        for sobject in my.sobjects:
            code = sobject.get_code()
            code_cache[code] = sobject
        my.caches['code'] = code_cache 

        for key in keys:
            if key in ['search_key', 'code']:
                continue
            my.build_cache_by_column(key)


    def get_refresh_events(my):
        events = [
            "change|%s" % my.search_type,
        ]
        return events



    def build_cache_by_column(my, column):
        # do not build if it already exists
        if my.caches.has_key(column):
            return

        # build a search_key cache
        column_cache = SObject.get_dict(my.sobjects, key_cols=[column])
        my.caches[column] = column_cache
        return column_cache

    def get_sobjects(my):
        return my.sobjects


    def add_cache(my, key, cache):
        my.caches[key] = cache
        
    def get_cache_by_key(my, key):
        cache = my.caches.get(key)
        return cache

    def get_sobject_by_key(my, cache_name, key):
        cache = my.caches.get(cache_name)
        if not cache:
            return None
        sobject = cache.get(key)
        return sobject


    def add_sobject_to_cache(my, sobject):
        '''add an sobject to the cache.  This is useful if a new sobject
        has been inserted and it is too expensive to have to recache the entire
        table just for this one entry'''

        # make sure this sobject's search type is the same as the search type 
        # for this cache
        search_type = sobject.get_base_search_type()
        assert search_type == my.search_type


        # FIXME: add to all of the caches
        for key, cache in my.caches.items():
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
        my.make_dirty()




    def get(cls, search_type):
        # TODO: make this thread safe
        cache = CacheContainer.get(search_type)
        if cache == None:
            # create a new instances of the Search Type cache
            cache = cls(search_type)

        return cache
    get = classmethod(get)



class CustomCache(BaseCache):

    def __init__(my, key=None, action=None):
        my.action = action

        super(CustomCache,my).__init__(key)


    # We have to somehow remember how to recache ... pass in a rehash function
    def init_cache(my):
        '''do the cache'''
        my.mtime = datetime.datetime.now()
        my.caches = my.action()
        assert type(my.caches) == types.DictType



 
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




