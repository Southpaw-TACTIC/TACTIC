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

__all__ = ['Texture', 'TextureSource', 'ShotTexture']

from pyasm.search import *
from pyasm.biz import Project

class Texture(SObject):

    SEARCH_TYPE = "prod/texture"


    
    def get_relation(self, name):
        from asset import Asset
        relations = {}
        relations['asset'] = Asset
        relations['texture'] = Texture
        return relations[name]

    def get_icon_context(self, context=None):
        return "publish"
    
    # static functions
    def create(cls, asset, code=None, category=None, description=None, sobject_context=None):
        sobject = SearchType.create( cls.SEARCH_TYPE )

        asset_code = asset.get_code()

        #asset_code = asset.get_code()
        sobject.set_value("asset_code", asset.get_code())

        if sobject_context != None:
            sobject.set_value("asset_context", sobject_context)

        if code != None:
            sobject.set_value("code", code)

        if category != None:
            sobject.set_value("category", category)

        if description != None:
            sobject.set_value("description", description)

        sobject.commit()
        return sobject

    create = classmethod(create)

    def get(cls, texture_code, parent_code, project_code=None, is_multi=False):
        '''TODO: use search_type, id for the parent search'''
        if not project_code:
            project_code = Project.get_project_code()
        search = Search( cls.SEARCH_TYPE, project_code )
        #search.set_show_retired(True)
        if texture_code:
            
            search.add_filter('code', texture_code)
        search.add_filter('asset_code', parent_code)
        search_type = search.get_search_type()
        key = "%s|%s|%s" % (search_type, texture_code, parent_code)
        sobj = cls.get_by_search(search, key, is_multi=is_multi)
        return sobj
    get = classmethod(get)

class TextureSource(Texture):
    SEARCH_TYPE = "prod/texture_source"

    def create(cls, asset_code, code=None, category=None, description=None, sobject_context=None):
        sobject = SearchType.create( cls.SEARCH_TYPE )

        sobject.set_value("asset_code", asset_code)

        if sobject_context != None:
            sobject.set_value("asset_context", sobject_context)

        if code != None:
            sobject.set_value("code", code)

        if category != None:
            sobject.set_value("category", category)

        if description != None:
            sobject.set_value("description", description)

        sobject.commit()
        return sobject

    create = classmethod(create)

    
        

class ShotTexture(Texture):
    SEARCH_TYPE = "prod/shot_texture"

    def get_shot_code(self):
        shot_code = ''

        search_type = self.get_value('search_type')

        search = Search( search_type )
        search.add_filter( 'id', self.get_value('search_id') )
        parent = search.get_sobject()

        if not parent:
            return shot_code

        if search_type.startswith('prod/shot_instance'):
            shot_code = parent.get_value('shot_code')
        else:
            shot_code = parent.get_value('code')

        return shot_code
    

    # static functions
    def create(cls, sobject, code=None, category=None, description=None, sobject_context=None):
        texture = SearchType.create( cls.SEARCH_TYPE )

        texture.set_value("search_type", sobject.get_search_type() )
        texture.set_value("search_id", sobject.get_id()) 
        #texture.set_value("shot_code", shot_code)

        if sobject_context != None:
            texture.set_value("asset_context", sobject_context)

        if code != None:
            texture.set_value("code", code)

        if category != None:
            texture.set_value("category", category)

        if description != None:
            texture.set_value("description", description)

        texture.commit()
        return texture

    create = classmethod(create)

    def get(cls, texture_code, parent_code, project_code=None, is_multi=False):
        if not project_code:
            project_code = Project.get_project_code()
        search = Search( cls.SEARCH_TYPE, project_code )
        
        #search.set_show_retired(True)
        
        if texture_code:
            search.add_filter('code', texture_code)
        
        # backward compatible with using shot code
        if isinstance(parent_code, basestring):
            from pyasm.prod.biz import Shot
            parent = Shot.get_by_code(parent_code)
        else:
            parent = parent_code
        if not parent:
            if is_multi:
                return []
            else:
                return None

        search.add_filter('search_type',  parent.get_search_type())
        search.add_filter('search_id',  parent.get_id())
        parent_key = SearchKey.get_by_sobject(parent)
        
        search_type = search.get_search_type()
        key = "%s|%s|%s" % (search_type, texture_code, parent_key)
        sobj = cls.get_by_search(search, key, is_multi=is_multi)
       
        return sobj
    get = classmethod(get)

