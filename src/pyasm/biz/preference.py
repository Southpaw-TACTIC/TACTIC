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


__all__ = ['PrefSetting', 'PrefList']

from pyasm.search import SObject, Search, DatabaseException
from pyasm.common import Container, TacticException, Environment

class PrefList(SObject):
    '''Defines all of the pref settings in the Admin area'''

    SEARCH_TYPE = "sthpw/pref_list"

    def get_value_by_key(cls, key, search_type=None):
        prod_setting = cls.get_by_key(key, search_type)

        value = ""
        if prod_setting:
            value = prod_setting.get_value("options")
        return value
    get_value_by_key = classmethod(get_value_by_key)


    def get_by_key(cls, key, search_type=None):
       
        dict_key = '%s:%s' %(key, search_type)
        cached = cls.get_cached_obj(dict_key)
        if cached:
            return cached

        search = Search(cls.SEARCH_TYPE)
        search.add_filter("key", key)
        if search_type:
            search.add_filter("search_type", search_type)
        prod_setting = search.get_sobject()
        
        dict = cls.get_cache_dict()
        dict[dict_key] = prod_setting

        return prod_setting
    get_by_key = classmethod(get_by_key)



class PrefSetting(PrefList):
    '''Defines all of the user settings for a given prodution'''

    SEARCH_TYPE = "sthpw/pref_setting"

    def get_value_by_key(cls, key, user=None, project_code=None):
        ''' get the value of this pref '''

        #try:
        #    from pyasm.biz import SearchTypeCache
        #    cache = SearchTypeCache.get(cls.SEARCH_TYPE)
        #except Exception:
        #    print "WARNING: Cache not enabled"

        # protect against database connection issues (This is called at a very
        # low level, so it needs this)
        try:
            pref_setting = cls.get_by_key(key, user, project_code)
            value = ''
            if pref_setting:
                value = pref_setting.get_value("value")
        except DatabaseException:
            value = ''

        return value
    get_value_by_key = classmethod(get_value_by_key)



    def get_by_key(cls, key, user=None, project_code=None, use_cache=True):
      
        if not user:
            user = Environment.get_user_name()

        # ignore the project_code column for now
        dict_key = '%s:%s:%s' %(cls.SEARCH_TYPE, project_code, user) 
        if use_cache:
            settings_dict = Container.get(dict_key)
        else:
            settings_dict = None

        # explicit check for None
        if settings_dict == None:
            settings_dict = {}

            if use_cache:
                Container.put(dict_key, settings_dict)

            search = Search(cls.SEARCH_TYPE)
            search.add_filter("login", user)
            if project_code:
                search.add_filter("project_code", project_code)
            else:
                search.add_null_filter("project_code")
            # don't filter with the key in order to build a dict
            pref_settings = search.get_sobjects()
            for setting in pref_settings:
                settings_dict[setting.get_value('key')] = setting

        pref_setting = settings_dict.get(key)

        return pref_setting
    get_by_key = classmethod(get_by_key)



    def create(cls, key, value, user=None, project_code=None):

        if not user:
            user = Environment.get_user_name()


        setting = cls.get_by_key(key, user, project_code, use_cache=False)
        print "setting: ", setting
        if not setting:
            setting = PrefSetting.create_new()
            setting.set_value("key", key)
            setting.set_value("login", user)
            if project_code:
                setting.set_value("project_code", project_code)

        setting.set_value("value", value)
        setting.commit()

        # ignore the project_code column for now
        dict_key = '%s:%s:%s' %(cls.SEARCH_TYPE, project_code, user) 
        settings_dict = Container.put(dict_key, None)

        return setting

    create = classmethod(create)



