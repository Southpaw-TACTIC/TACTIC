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

__all__ = ['FlashSObject', 'FlashFunpack', 'FlashDesignPack', 'FlashShot', 'FlashAsset', 'FlashLayer', 'FlashShotInstance', 'FlashMapping', 'FlashTask', 'NatPause', 'FinalWave', 'FlashEpisodeInstance']

from pyasm.common import Config
from pyasm.search import *
from pyasm.prod.biz import *
from pyasm.biz import Task, Pipeline



class FlashMapping(SObjectMapping):
    '''Defines all the production assets'''

    def __init__(my):
        my.mapping = {}
        my.mapping['prod/sequence'] = "prod/episode"
        my.mapping['prod/asset'] = "flash/asset"
        my.mapping['prod/shot'] = "flash/shot"
        my.mapping['prod/layer'] = "flash/layer"
        my.mapping['prod/script'] = "flash/script"
        my.mapping['prod/storyboard'] = "flash/storyboard"
        my.mapping['prod/shot_instance'] = "flash/shot_instance"
        my.mapping['prod/sequence_instance'] = "flash/episode_instance"



class FlashSObject(SObject):
    '''All episodic flash animations are organized by episode'''

    def get_icon_context(my, context=None):
        return "publish"

    def get_pipeline(my):
        return Pipeline.get_by_code(my.get_value('pipeline'))


    def is_general_asset(my):

        if my.has_value('asset_type') and  \
            my.get_value("asset_type") in ["general", 'image']:
                return True

        if not my.has_value('asset_library'):
            return False
     
        return False


class FlashFunpack(SObject):
    SEARCH_TYPE = "flash/funpack"

class FlashDesignPack(SObject):
    SEARCH_TYPE = "flash/design_pack"



class FlashShot(Shot):
    SEARCH_TYPE = "flash/shot"

    def get_foreign_key(my):
        return "shot_code"

    def get_code(my):
        return my.get_value("code")

    def get_all_instances(my):
        return FlashInstance.get_all_by_shot(my)

    def get_icon_context(my, context=None):
        return "publish"

    def is_general_asset(my):
        return False

    def create(code, episode_code, description):
        shot = SObjectFactory.create( FlashShot.SEARCH_TYPE )
        shot.set_value("code",code)
        shot.set_value("episode_code", episode_code)
        shot.set_value("description",description)
        shot.commit()
        return shot
    create = staticmethod(create)


class FlashAsset(FlashSObject):
    SEARCH_TYPE = "flash/asset"
    
    def get_code(my):
        return my.get_value("code")

    def get_asset_type(my):
        return my.get_value("asset_type")

    def get_asset_type_obj(my):
        search = Search("prod/asset_type")
        search.add_filter("code", my.get_asset_type() )
        return search.get_sobject()

    def get_asset_library(my):
        return my.get_value("asset_library")

    def get_asset_library_obj(my):
        search = Search("prod/asset_library")
        search.add_filter("code", my.get_asset_library() )
        return search.get_sobject()

class FlashShotInstance(FlashSObject):
    SEARCH_TYPE = "flash/shot_instance"


class FlashEpisodeInstance(FlashSObject):
    SEARCH_TYPE = "flash/episode_instance"


class FlashLayer(FlashSObject):
    SEARCH_TYPE = "flash/layer"

    def get_foreign_key(my):
        return "layer_id"

    def get_frame_range(my):
        shot = my.get_shot()
        return shot.get_frame_range()

    def get_shot(my):
        return FlashShot.get_by_code( my.get_value("shot_code") )


    def get( shot_code, layer_name):
        search = Search("flash/layer")
        search.add_filter("shot_code", shot_code)
        search.add_filter("name", layer_name)
        return search.get_sobject()
    get = staticmethod(get)

    def get_description(my):
        return "%s %s" %(my.get_value("shot_code"), my.get_value("name"))



class FlashTask(Task):
    SEARCH_TYPE = "flash/task"

class NatPause(SObject):
    SEARCH_TYPE = "flash/nat_pause"

    def create(cls, episode_code, title=''):
        '''create with an episode code'''
        asset = SObjectFactory.create( cls.SEARCH_TYPE )
        asset.set_value("episode_code", episode_code)
        if title:
            asset.set_value("title", title)
        asset.commit()
        return asset
    create = classmethod(create)

    def get_by_episode_code(episode_code):
        search = Search(NatPause.SEARCH_TYPE)
        search.add_filter("episode_code", episode_code)
        return search.get_sobject()
    get_by_episode_code = staticmethod(get_by_episode_code)

    def get_update_description(my):
        code = my.get_value('episode_code')
        title = my.get_search_type_obj().get_title()
        description = "Updated %s: episode [%s]" % (title, code)
        return description

class FinalWave(SObject):
    SEARCH_TYPE = "flash/final_wave"

    def create(cls, episode_code, line, title=''):
        '''create with an episode code, line'''
        asset = SObjectFactory.create( cls.SEARCH_TYPE )
        asset.set_value("episode_code", episode_code)
        asset.set_value("line", line)
        if title:
            asset.set_value("title", title)
        asset.commit()
        return asset
    create = classmethod(create)

    def get(episode_code, line):
        search = Search(FinalWave.SEARCH_TYPE)
        search.add_filter("episode_code", episode_code)
        search.add_filter("line", line)
        return search.get_sobject()
    get = staticmethod(get)
