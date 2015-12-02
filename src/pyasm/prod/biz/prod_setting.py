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


__all__ = ['ProdSetting']

from pyasm.common import Container, TacticException
from pyasm.search import *
from pyasm.biz import Project

class ProdSetting(SObject):
    '''Defines all of the settings for a given production'''

    SEARCH_TYPE = "config/prod_setting"


    # FIXME: what is this for?
    def get_app_tabs(my):
        '''This controls what tabs are visible'''
        return ["3D Asset", "Checkin", "Sets", "Anim Loader", "Anim Checkin", "Layer Loader", "Layer Checkin", "Shot"]
               



    def _get_container_key(cls, key, search_type=None):
        if search_type:
            key = "ProdSetting:%s:%s" % (key, search_type)
        else:
            key = "ProdSetting:%s" % key
        return key

    _get_container_key = classmethod(_get_container_key)
            
        


    def get_value_by_key(cls, key, search_type=None):
        '''
        container_key = cls._get_container_key(key,search_type)
        value = Container.get(container_key)
        if value:
            return value
        '''
        if Project.get_project_name() in ['sthpw', 'admin']:
            return ''

        prod_setting = cls.get_by_key(key, search_type)
        value = '' 
        if prod_setting:
            value = prod_setting.get_value("value")

        return value
    get_value_by_key = classmethod(get_value_by_key)



    def get_by_key(cls, key, search_type=None):
        from pyasm.security import Site
        site = Site.get_site()
        Site.set_site( Site.get_first_site() )

        try:

            project = Project.get_project_code() 
            dict_key = '%s:%s' %(key, search_type)
           
            search = Search(cls.SEARCH_TYPE, project_code=project)
            search.add_filter("key", key)
            if search_type:
                search.add_filter("search_type", search_type)

            if Project.get_project_name() in ['admin', 'sthpw']:
                return None
            prod_setting = ProdSetting.get_by_search(search, dict_key)
        finally:
            Site.pop_site()

        return prod_setting

    get_by_key = classmethod(get_by_key)


    def get_seq_by_key(cls, key, search_type=None):
        seq = []
        value = cls.get_value_by_key(key, search_type)
        if value:
            seq = value.split("|")
        return seq
    get_seq_by_key = classmethod(get_seq_by_key)


    def add_value_by_key(cls, key, value, search_type=None):
        seq = cls.get_seq_by_key(key, search_type)
        if not seq:
            seq = []
        elif value in seq:
            return

        seq.append(value)

        setting = cls.get_by_key(key, search_type)
        if not setting:
            return


        setting.set_value( "value", "|".join(seq) )
        setting.commit()

        container_key = cls._get_container_key(key,search_type)
        value = Container.put(container_key, None)

    add_value_by_key = classmethod(add_value_by_key)





    def get_map_by_key(cls, key, search_type=None):
        ''' this is more like an ordered map'''
        seq = []
        map = []
        value = cls.get_value_by_key(key, search_type)
        if value:
            seq = value.split("|")
        for item in seq:
            try:
                key, value = item.split(':')
                map.append((key, value))
            except Exception, e:
                raise TacticException('ProdSettings should be formated like &lt;key1&gt;:&lt;value1&gt;|&lt;key2&gt;:&lt;value2&gt;|...')
        return map
    get_map_by_key = classmethod(get_map_by_key)

    def get_dict_by_key(cls, key, search_type=None):
        ''' this is to retrieve an unordered dict'''
        seq = []
        dict = {}
        value = cls.get_value_by_key(key, search_type)
        if value:
            seq = value.split("|")
        for item in seq:
            try:
                key, value = item.split(':')
                dict[key] = value
            except Exception, e:
                raise TacticException('ProdSettings should be formated like &lt;key1&gt;:&lt;value1&gt;|&lt;key2&gt;:&lt;value2&gt;|...')
        return dict
    get_dict_by_key = classmethod(get_dict_by_key)

    
    def create(key, value, type, description='', search_type=''):
        '''create a ProdSetting'''

        if Project.get_project_name() in ['admin', 'sthpw']:
            return None

        ProdSetting.clear_cache()
        setting = ProdSetting.get_by_key(key, search_type)
        if not setting:
            setting= SObjectFactory.create( ProdSetting.SEARCH_TYPE )
            setting.set_value("key", key)
            setting.set_value("value", value)
            
            setting.set_value("type", type)
            if description:
                setting.set_value("description", description)
            if search_type:
                setting.set_value("search_type", search_type)
        else:
            setting.set_value("value", value)

        setting.commit()
        return setting
    create = staticmethod(create)


