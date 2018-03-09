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


__all__ = ['Asset', 'AssetLibrary', 'ShotInstance','LayerInstance','SequenceInstance']

from pyasm.biz import Snapshot, Task, Pipeline, Project
from pyasm.search import *
from pyasm.common import *

import re

class Asset(SObject):

    SEARCH_TYPE = "prod/asset"

    def get_search_columns():
        return ['code','name','description','asset_library']
    get_search_columns = staticmethod(get_search_columns)

    def get_required_columns():
        '''for csv import'''
        #return ['name', 'asset_library']
        return []
    get_required_columns = staticmethod(get_required_columns)

    def get_defaults(self):
        '''specifies the defaults for this sobject'''
        # use the naming the generate the next code
        from naming import AssetCodeNaming
        naming = AssetCodeNaming()
        asset_code = naming.get_next_code(self)

        defaults = super(Asset, self).get_defaults()
        defaults.update({
            "asset_type": "asset",
            'code': asset_code
        })

        return defaults


    def get_asset_type(self):
        return self.get_value("asset_type")


    def get_asset_library(self):
        return self.get_value("asset_library")

    def get_asset_library_obj(self):
        search = Search("prod/asset_library")
        search.add_filter("code", self.get_asset_library() )
        return search.get_sobject()

    def get_icon_context(cls, context=None):
        if context:
            return context
        else:
            return "icon"
    get_icon_context = classmethod(get_icon_context)

    
    def get_full_name(self):
        return "%s|%s" %(self.get_value('name'), self.get_code())


    def has_auto_current(self):
        #return False
        return True



    def delete(self, log=True):

        '''This is for undo'''
        # TODO: the should probably be clearer!!!!
        if log == False:
            super(Asset,self).delete(log)
            return
            

        # An asset can only be deleted if only icon snapshots exist
        snapshots = Snapshot.get_by_sobject(self)

        only_icons = True
        for snapshot in snapshots:
            context = snapshot.get_value("context")
            if context != self.get_icon_context():
                only_icons = False

        if not only_icons:
            raise TacticException("Cannot delete because snapshots exist")

        # only delete if not tasks have been assigned
        tasks = Task.get_by_sobject(self)
        has_assigned = False
        for task in tasks:
            assigned = task.get_value("assigned")
            if assigned != "" and assigned != "None":
                has_assigned = True
        
        if has_assigned:
            raise TacticException("Cannot delete because tasks have been assigned")

        # delete tasks and icons
        for snapshot in snapshots:
            snapshot.delete()
        for task in tasks:
            task.delete()

        self.description = "Deleted '%s', search_type '%s'" % (self.get_code(), self.get_search_type)

        super(Asset,self).delete(log)


    # Static methods

    def alter_search(search):
        '''allow the sobject to alter the search'''
        search.add_order_by("code")
    alter_search = staticmethod(alter_search)


    def get_by_id(id):
        search = Search( Asset.SEARCH_TYPE )
        search.add_id_filter(id)
        return search.get_sobject()
    get_by_id = staticmethod(get_by_id)



    def get_by_sobject(sobject, column="asset_code"):
        '''gets the sobject by an sobject.  All an sobject needs to be
        contained by this sobject is to have the asset_code column'''
        code = sobject.get_value(column)
        search = Search(Asset.SEARCH_TYPE)
        search.add_filter("code", code)
        return search.get_sobject()
    get_by_sobject = staticmethod(get_by_sobject)



    def get_by_name(cls, name):
        search = Search( cls.SEARCH_TYPE )
        search.add_filter("name",name)
        return search.get_sobject()
    get_by_name = classmethod(get_by_name)



    def create(code, name, asset_library, description):
        '''create with an explicit code'''
        asset = SObjectFactory.create( Asset.SEARCH_TYPE )
        asset.set_value("code",code)
        asset.set_value("name",name)
        asset.set_value("asset_library",asset_library)
        asset.set_value("description",description)

        asset.set_value("asset_type","asset")

        asset.commit()
        return asset
    create = staticmethod(create)


    def create_with_autocode(cls, name, asset_library, description, asset_type="asset"):

        # create the new asset
        asset = SObjectFactory.create( cls.SEARCH_TYPE )
        asset.set_value("name",name)
        asset.set_value("asset_library",asset_library)
        asset.set_value("description",description)

        asset.set_value("asset_type",asset_type)

        # use the naming the generate the next code
        from naming import AssetCodeNaming
        naming = AssetCodeNaming()
        asset_code = naming.get_next_code(asset)
        asset.set_value("code",asset_code)

        asset.commit()
        return asset
    create_with_autocode = classmethod(create_with_autocode)


class AssetLibrary(SObject):

    SEARCH_TYPE = "prod/asset_library"

    def get_foreign_key(self):
        return "asset_library"

    def get_required_columns():
        '''for csv import'''
        return ['code', 'title', 'padding']
    get_required_columns = staticmethod(get_required_columns)

    def get_defaults(self):
        '''specifies the defaults for this sobject'''
        # use the naming the generate the next code

        defaults = {
            "padding": "3"
        }
        return defaults


class ShotInstance(SObject):
    '''Represents an instance of an asset in a shot'''

    SEARCH_TYPE = "prod/shot_instance"

   
    def get_code(self):
        '''This is kept for backward-compatibility. code is auto-gen now'''
        return self.get_value("name")

    def get_asset(self, search_type='prod/asset'):
        asset_code = self.get_value("asset_code")
        asset = Search.get_by_code(search_type, asset_code)
        return asset


    def get_shot(self, search_type='prod/shot'):
        shot_code = self.get_value("shot_code")
        shot = Search.get_by_code(search_type, shot_code)
        return shot

    def get_title(self):
        shot_code = self.get_value("shot_code")
        name = self.get_value("name")
        return "%s in %s" % (name, shot_code)



    # Static methods
    def get_by_shot(shot, instance_name, parent_codes=[], type=None):
        shot_col = shot.get_foreign_key()
        search = Search( ShotInstance.SEARCH_TYPE )

        if parent_codes:
            parent_codes.append(shot.get_code())
            search.add_filters(shot_col, parent_codes)
        else:
            search.add_filter(shot_col, shot.get_code())
            
        search.add_filter("name", instance_name)
        if type:
            search.add_filter("type", type)
        return search.get_sobject()
    get_by_shot = staticmethod(get_by_shot)





    def get_all_by_shot(shot, parent_codes=[], type='asset'):
        shot_col = shot.get_foreign_key()
        search = Search( ShotInstance.SEARCH_TYPE )

        if parent_codes:
            parent_codes.append(shot.get_code())
            search.add_filters(shot_col, parent_codes)
        else:
            search.add_filter(shot_col, shot.get_code())

        search.add_filter("type", type)
        return search.do_search()
    get_all_by_shot = staticmethod(get_all_by_shot)


    def filter_instances(instances, shot_code):
        ''' filter out the parents' shot instances if child shot instances exist'''
        instance_dict = {}
        for instance in instances:
            key = "%s:%s" %(instance.get_value('asset_code'), instance.get_value('name'))
            if key not in instance_dict.keys():
                instance_dict[key] = instance
                continue
            if instance.get_value('shot_code') == shot_code: 
                instance_dict[key] = instance

        return Common.sort_dict(instance_dict)
    filter_instances = staticmethod(filter_instances)


    def get_by_shot_and_asset(cls, shot, asset, type='asset'):
        shot_col = shot.get_foreign_key()
        search = Search( cls.SEARCH_TYPE )
        search.add_filter(shot_col, shot.get_code())
        search.add_filter("type", type)
        search.add_filter("asset_code", asset.get_code())
        search.add_order_by('name desc')
        return search.get_sobjects()
    get_by_shot_and_asset = classmethod(get_by_shot_and_asset)


   

    def create(cls, shot, asset, instance_name="", type="asset", unique=False):

        shot_col = shot.get_foreign_key()
        search = Search( cls.SEARCH_TYPE )
        search.add_filter(shot_col, shot.get_code())
        search.add_filter("type", type)
        #if unique:
        #    search.add_filter("name", instance_name)
        search.add_filter("asset_code", asset.get_code())
        search.add_order_by('name desc')
        sobjs = search.get_sobjects()

        # if unique and exists, then return
        if unique and sobjs:
            Environment.add_warning("Instance exists", "Shot '%s' already has an instance for asset '%s'" % (shot.get_code(), asset.get_code()) )
            return

        naming = Project.get_naming("node")
        instance_name = naming.get_shot_instance_name(shot, asset, sobjs)
        
        #instance_name = cls.get_instance_name(sobjs, instance_name) 
        
        instance = SObjectFactory.create( cls.SEARCH_TYPE )
        instance.set_value(shot_col,shot.get_code())
        instance.set_value("asset_code",asset.get_code())
        instance.set_value("name",instance_name)
        instance.set_value("type",type)

        instance.commit()
        return instance
    create = classmethod(create)

    def add_related_connection(self, src_sobject, dst_sobject, src_path=None):
        '''adding the related sobject code to this current sobject''' 
        self.add_related_sobject(src_sobject)
        self.add_related_sobject(dst_sobject)


        #shot_col =  dst_sobject.get_foreign_key()
        schema = self.get_schema()
        st1 = self.get_base_search_type()
        st2 =  dst_sobject.get_base_search_type()
        relationship = schema.get_relationship(st1, st2)
        attrs = schema.get_relationship_attrs(st1, st2)
        
        from_col = attrs.get("from_col")

        search = Search( self.SEARCH_TYPE )
        search.add_filter(from_col,  dst_sobject.get_code())
        search.add_filter("type", "asset")
        search.add_filter("asset_code",  src_sobject.get_code())
        search.add_order_by('name desc')
        instances = search.get_sobjects()
        """
        # if it allows order by, I can switch to this
        filters = [('asset_code', src_sobject.get_code())]
        instances = dst_sobject.get_related_sobjects(self.SEARCH_TYPE, filters=filters)
        """
        naming = Project.get_naming("node")
        instance_name = naming.get_shot_instance_name(dst_sobject, src_sobject, instances)
        self.set_value('name', instance_name)
        self.set_value('type', 'asset')
        #self.commit()


    def get_instance_name(sobjs, instance_name):
        ''' append a digit to the instance_name if necessary '''
        if sobjs:
            pat = re.compile('(%s)(_\d{2}$)?'% instance_name)
            m = pat.match(sobjs[0].get_value('name'))
            ext = 1 
            if m:
                if m.group(2):
                    ext = int(m.group(2)[1:])
            instance_name = "%s_%0.2d" % (instance_name, ext + 1)

        return instance_name

    get_instance_name = staticmethod(get_instance_name)

    def get_aux_data(top_instances, asset_stype='prod/asset'):
        '''get the aux data for asset_name'''
        if not top_instances or not top_instances[0].has_value('asset_code'):
            return []
        search = Search(asset_stype)
        
        asset_codes = SObject.get_values(top_instances, 'asset_code')
        search.add_filters('code', asset_codes)
        assets = search.get_sobjects()
        
        asset_dict = SObject.get_dict(assets, ['code'])
        
        aux_data = []
        for inst in top_instances:
            asset = asset_dict.get(inst.get_value('asset_code'))
            asset_name = "RETIRED"
            if asset:
                asset_name = asset.get_value('name')
            aux_data.append({'asset_name': asset_name})
   
        return aux_data
    get_aux_data = staticmethod(get_aux_data)


class LayerInstance(ShotInstance):
    '''Represents an instance of an asset in a layer'''

    SEARCH_TYPE = "prod/layer_instance"
   

    def get_shot(self):
        pass


    def get_code(self):
        return self.get_value("name")

    # Static methods
    def get(layer, instance_name):
        shot_col = shot.get_foreign_key()
        search = Search( LayerInstance.SEARCH_TYPE )
        search.add_filter("name", instance_name)
        search.add_filter("layer_id", layer.get_id())
        return search.get_sobject()
    get = staticmethod(get)


    def get_all_by_layer(layer, parent_codes=[]):
        search = Search( LayerInstance.SEARCH_TYPE )
        search.add_filter("layer_id", layer.get_id())
        return search.get_sobjects()
    get_all_by_layer = staticmethod(get_all_by_layer)

        
    def get_all_by_shot(shot, parent_codes=[]):
        pass



    def create(layer, asset, instance_name, type="asset", unique=False):
        layer_col = layer.get_foreign_key()
        search = Search( LayerInstance.SEARCH_TYPE )
        search.add_filter(layer_col, layer.get_code())
        search.add_filter("asset_code", asset.get_code())
        if unique:
            search.add_filter("name", instance_name)
        search.add_order_by('name desc')
        sobjs = search.get_sobjects()
        instance_name = LayerInstance.get_instance_name(sobjs, instance_name)   
            
        instance = SObjectFactory.create( LayerInstance.SEARCH_TYPE )
        instance.set_value(layer_col, layer.get_code())
        instance.set_value("asset_code",asset.get_code())
        instance.set_value("name",instance_name)
        instance.set_value("type",type)

        instance.commit()
        return instance
    create = staticmethod(create)


class SequenceInstance(ShotInstance):
    '''Represents an instance of an asset in a layer'''

    SEARCH_TYPE = "prod/sequence_instance"

    def get_code(self):
        return self.get_value("id")



   


"""    
class GeoCache(SObject):
    SEARCH_TYPE = "prod/geo_cache"

 
    def create(shot_code, instance_name):
        geo_cache = SObjectFactory.create( GeoCache.SEARCH_TYPE )
        geo_cache.set_value("shot_code",shot_code)
        geo_cache.set_value("instance",instance_name)
        geo_cache.commit()
    create = staticmethod(create)
"""





