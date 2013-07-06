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

__all__ = ['FlashDirNaming']

from pyasm.biz import DirNaming
from pyasm.search import SearchType, Search
from pyasm.prod.biz import Shot


class FlashDirNaming(DirNaming):

    def flash_script(my, dirs):
        dirs = my.get_default(dirs)
        template = "{episode_code}"
        dirs.extend( my.get_template_dir(template) )
        return dirs

    def flash_storyboard(my, dirs):
        dirs = my.get_default(dirs)
        template = "{episode_code}"
        dirs.extend( my.get_template_dir(template) )
        return dirs


    def flash_asset(my, dirs):
        dirs = my.get_default(dirs)
        template = "{asset_library}/{code}"
        dirs.extend( my.get_template_dir(template) )
        return dirs

    def flash_instance(my, dirs):
        dirs = my.get_parent_dir("flash/asset")
        return dirs



    def flash_shot(my,dirs):
        dirs = my.get_default(dirs)
        template = "{episode_code}/{code}"
        dirs.extend( my.get_template_dir(template) )
        return dirs


    def flash_layer(my,dirs):
        dirs = my.get_parent_dir("flash/shot")
        #template = "layer/{name}"
        template = "layer"
        dirs.extend( my.get_template_dir(template) )
        return dirs



    def prod_render(my,dirs):
        search_type = my.sobject.get_value("search_type")
        search_id = my.sobject.get_value("search_id")

        ref_sobject = Search.get_by_search_key("%s|%s" % (search_type,search_id))
        # get shot and episode code
        shot_code = ref_sobject.get_value("code")
        shot = Shot.get_by_code(shot_code)
        episode_code = ''
        if shot:
            episode_code = shot.get_value("episode_code")

        name = ''
        if ref_sobject.has_value('name'):
            name = ref_sobject.get_value("name")

        # build the path
        dirs = my.get_default(dirs)
        dirs.append(episode_code)
        dirs.append(shot_code)
        if name:
            dirs.append(name)

        version = my.sobject.get_value("version")
        dirs.append("%04d" % version)

        return dirs

