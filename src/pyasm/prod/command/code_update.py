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

__all__ = ['BaseCodeUpdate', 'AssetCodeUpdate', 'TextureCodeUpdate', 
            'TemplateCodeUpdate']

import os, shutil

from pyasm.command import *
from pyasm.search import *

from pyasm.common import Environment
from pyasm.checkin import FileCheckin
from pyasm.biz import Pipeline, Snapshot, Template, File
from pyasm.prod.biz import *


class BaseCodeUpdate(DatabaseAction):
    '''Provides the next code following a naming convention'''
    '''This class supports the naming convention:
       < asset_category >< unique_code >
    '''
    def get_naming(my):
        raise CommandException("override this to return a naming scheme")
    
    def execute(my):
        if not my.sobject.is_insert():
            return

        # use naming to figure out the code for this asset
        naming = my.get_naming()
        code = naming.get_next_code(my.sobject)
        my.sobject.set_value("code", code)

class TemplateCodeUpdate(BaseCodeUpdate):
    
    def get_naming(my):
        return TemplateCodeNaming()
   


class AssetCodeUpdate(BaseCodeUpdate):
    SEARCH_TYPE = "prod/asset"

    def get_naming(my):
        return AssetCodeNaming()

    def get_default_code(my):
        return "prod-asset_default"

    def execute(my):
        if not my.sobject.is_insert():
            return

        if ProdSetting.get_value_by_key("use_name_as_asset_code") == "true":
            name = my.sobject.get_value("name")
            my.sobject.set_value("code", name)
        else:    
            super(AssetCodeUpdate,my).execute()



class TextureCodeUpdate(BaseCodeUpdate):
    '''Provides the next asset code following a naming convention'''
    '''This class supports the naming convention:
    <asset_code>_###_<asset_context>
    '''

    def get_naming(my):
        return TextureCodeNaming()

    """
    def execute(my):
        # register the trigger on renaming files
        #print "registering"
        #Trigger.register(my,"UploadAction")
        pass


    def handle_rename_files(my):
        '''called by trigger'''

        return
        files = my.command.files
        sobject = my.command.sobject

        asset_code = sobject.get_value("asset_code")

        code = sobject.get_value("code")

        # if there is no code yet, then the extract the code from the filename
        is_code_new = False
        if code == "":
            main = files[0]
            dirname = os.path.dirname(main)
            filename = os.path.basename(main)
            code, ext = os.path.splitext(filename)

            # if it already starts with the asset code, then remove the
            # asset_code
            if code.startswith("%s_" % asset_code):
                code = code.replace("%s_" % asset_code, "")

            sobject.set_value("code", code)

            is_code_new = True


        base = "%s_%s" % (asset_code, code)

        # prepend the sobject code to every file
        new_paths = []
        for file_path in files:

            if is_code_new:
                # move the file to the new name
                filename = os.path.basename(file_path)
                dirname = os.path.dirname(file_path)

                if not filename.startswith("%s_" % asset_code):
                    filename = "%s_%s" % (asset_code, filename)

                new_path = "%s/%s" % (dirname,filename)
                shutil.move(file_path,new_path)
                new_paths.append(new_path)
            else:
                # the file must start with base
                if not os.path.basename(file_path).startswith(base):
                    raise CommandException("File '%s' does not belong to texture '%s'" % (file_path, base)  )

                new_paths.append(file_path)

        # remap to the new paths
        my.command.files = new_paths

    """



