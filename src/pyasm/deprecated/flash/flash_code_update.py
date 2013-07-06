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

__all__ = ['FlashAssetCodeUpdate', 'FlashShotCodeUpdate', 'FlashLayerCodeUpdate']

from pyasm.common import Config, Environment
from pyasm.biz import *
from pyasm.command import *
from pyasm.prod.command import BaseCodeUpdate
from pyasm.search import Search, SearchType
from pyasm.checkin import FileCheckin
from pyasm.prod.biz import *

#from pyasm.web import *
#from pyasm.widget import *

import os, re, shutil

from flash_code_naming import *



class FlashAssetCodeUpdate(BaseCodeUpdate):
    '''Provides the next asset code following a naming convention'''
    '''This class supports the naming convention:
    <series><episode_code>-<unique_code>
    for flash assets
    '''
    SEARCH_TYPE = 'flash/asset'
    def get_code_padding(my):
        return 3

    def get_default_code(my):
        return "flash-asset_default"
        
    def get_naming(my):
        from pyasm.prod.biz import FlashAssetNaming
        return FlashAssetNaming()
    
    def execute(my):

	if not my.sobject.is_insert():
	     return

        # generate a code
        #columns = ['episode_code','asset_library']
        #code_num = my._get_next_num(columns)
        #episode_code = my.sobject.get_value("episode_code")
        #asset_library = my.sobject.get_value("asset_library")
        #new_code = "%s-%s%0.3d" % (episode_code, asset_library, code_num)


        # generate a code without the episode
        columns = ['asset_library']
        code_num = my._get_next_num(columns)
        asset_library = my.sobject.get_value("asset_library")
        new_code = "%s%0.3d" % (asset_library, code_num)



        my.sobject.set_value("code", new_code)


    def _get_next_num(my, columns):

        # set the default
        code_num = 1

        # get the highest number, extract the number and increase by 1
        search_type = my.sobject.get_search_type()
        search = Search(search_type)
        search.set_show_retired_flag(True)

        for column in columns:
            value = my.sobject.get_value(column)
            search.add_filter(column, value)

        # order by descending codes
        search.add_order_by("code desc")
       
        sobject = search.get_sobject()

        if sobject != None:
            code = sobject.get_value("code")

            naming = Project.get_code_naming(sobject, code)
            code_num = naming.get_match("padding")
            code_num = int(code_num) + 1

        return code_num



    def get_template_obj(my):
        return Template.get_latest(my.SEARCH_TYPE)



    def postprocess(my):

        if my.sobject.is_general_asset():
            return
        # check to see if there are any snapshots
        # context is specified here to ignore any icon snapshots
        snapshot = Snapshot.get_latest_by_sobject(my.sobject, context='publish')

        if snapshot:
            return

        column = "snapshot"
        new_file_paths = []
        file_paths = []
        # copy the default file to /tmp
        template_code = my.get_default_code()
        template = my.get_template_obj()
        if template:
            template_code = template.get_value('code')
            tmpl_snapshot = Snapshot.get_latest_by_sobject(template)
                    
            file_paths = tmpl_snapshot.get_all_lib_paths()
        else:
            file_types = ['.fla','.png','_icon.png','.swf']    
            # TODO: this is a web depedency we don't need
            from pyasm.web import WebContainer
            web = WebContainer.get_web()
            for type in file_types:
                file_paths.append('%s/template/%s%s' % (web.get_context_dir(), \
                    template_code, type))
                
        for file_path in file_paths:
            # rename and copy each file to /tmp
            base_name = os.path.basename(file_path)
            base_name = File.remove_file_code(base_name)
            base_name = base_name.replace(template_code, \
                my.get_naming().get_current_code(my.sobject) )
            
            # do a straight copy : No undo
            tmp_dir = Environment.get_tmp_dir()
            new_file_path = "%s/download/%s" % (tmp_dir,base_name)
            shutil.copyfile(file_path, new_file_path)
            new_file_paths.append(new_file_path)


        file_types = [".fla", ".png", "icon",".swf"]
        checkin = FileCheckin( my.sobject, new_file_paths, file_types, \
            snapshot_type="flash", column=column  )
        checkin.execute()





class FlashShotCodeUpdate(FlashAssetCodeUpdate):

    SEARCH_TYPE = 'flash/shot' 
    def execute(my):

	if not my.sobject.is_insert():
	     return

        # generate a code
        columns = ['episode_code']

        episode_code = my.sobject.get_value("episode_code")
        code = my.get_value("code")

        new_code = "%s-%s" % (episode_code, code)

        my.sobject.set_value("code", new_code)

    #def postprocess(my):
    #    # do nothing
    #    pass




class FlashLayerCodeUpdate(FlashAssetCodeUpdate):
    
    SEARCH_TYPE = 'flash/layer' 
    def get_default_code(my):
        return "flash-layer_default"
    
    def get_naming(my):
        return FlashLayerNaming()
    
    def execute(my):

	if not my.sobject.is_insert():
	     return

