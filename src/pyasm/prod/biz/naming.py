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

__all__ = ['BaseNaming', 'AssetCodeNaming', 'TemplateCodeNaming', 
            'TextureCodeNaming', 'FlashAssetNaming', 'FlashLayerNaming',
            'FlashShotNaming', 'NatPauseNaming', 'FinalWaveNaming', 
            'ShotAudioNaming', 'ProdAssetCodeNaming' ]

import os, re

from pyasm.common import Base, Xml
from pyasm.command import *
from pyasm.search import *
from pyasm.biz import *
from asset import *
from texture import *



class BaseNaming(Base):
    '''defines the required interface for code naming conventions'''

    def get_sobject_by_filename(self, filename):
        '''extract the code from the filename'''
        pass

    def get_current_code(self, sobject):
        ''' this is by default the value of the code column for the sobject'''    
        return sobject.get_code()
    
    def get_next_code(self, sobject):
        '''get the next code for this sobject'''
        pass


    
class AssetCodeNaming(BaseNaming):

    def get_sobject_by_filename(self, filename):
        '''extract the code from the filename'''
        index = filename.find("_")
        if index == -1:
            return None

        code = filename[0:index]

        asset = Asset.get_by_code(code)
        return asset

 
    def get_next_code(self, sobject):
        # generate a code
        self.asset_library = sobject.get_value("asset_library")
        insert_default = False
        if not self.asset_library:
            self.asset_library = 'default'
            insert_default = True
            sobject.set_value('asset_library', self.asset_library)

        search = Search("prod/asset_library")
        search.add_filter("code",self.asset_library)
        self.asset_library_obj = search.get_sobject()
        if not self.asset_library_obj and insert_default:
            self.asset_library_obj  = SearchType.create('prod/asset_library')
            self.asset_library_obj.set_value('code', 'default')
            self.asset_library_obj.set_value('title', 'Default')
            self.asset_library_obj.set_value('description', 'TACTIC Default')

            self.asset_library_obj.commit()
        
        if not self.asset_library_obj:
            print "WARNING: Asset library [%s] does not exist" % self.asset_library
        assert self.asset_library_obj != None


        columns = ['asset_library']
        code_num = self._get_next_num(sobject, columns)
        padding = self._get_code_padding()
        code_num = str(code_num).zfill( padding )

        # build the new code
        new_code = "%s%s" % (self.asset_library, code_num)

        return new_code



    def _get_code_padding(self):
        return int(self.asset_library_obj.get_value("padding"))


    def _get_start_code(self):
        return 1



    def _get_next_num(self, sobject, columns):

        # set the default
        code_num = self._get_start_code()

        # get the highest number, extract the number and increase by 1
        search_type = sobject.get_search_type()
        search = Search(search_type)
        search.set_show_retired_flag(True)

        for column in columns:
            value = sobject.get_value(column)
            search.add_filter(column, value)


        # to exclude related asset code and assuming regular 
        # asset code don't have _
        #search.add_regex_filter('code', '_', op='NEQ')
        search.add_regex_filter('code', '%s\\\\d{%d}' %(self.asset_library, self._get_code_padding()), op='EQ')
        # order by descending codes
        search.add_order_by("code desc")

        last_sobject = search.get_sobject()
        if last_sobject != None:
            code = last_sobject.get_value("code")
            start = len(self.asset_library)
            end = start + self._get_code_padding()
            code_num = code[start:end]
            if not code_num:
                code_num = 0
            try:
                code_num = int(code_num) + 1
            except:
                code_num = 1

        return code_num



class TemplateCodeNaming(AssetCodeNaming):
 
    def get_sobject_by_filename(self, filename):
        '''extract the code from the filename'''
        index = filename.find(".")
        if index == -1:
            return None
        project_code = Project.get_project_code()
        return Template.get(filename[0:index], project_code)

    def _get_code_padding(self):
        return 3
    
    def get_next_code(self, sobject):
        # generate a code
        search_type = sobject.get_value("search_type")
        search_type = search_type.replace('/','-')
        category = sobject.get_value("category")
      
        columns = ['search_type','category']
        code_num = self._get_next_num(sobject, columns)
        padding = self._get_code_padding()
        code_num = str(code_num).zfill( padding )

        # build the new code
        new_code = "%s_%s%s" % (search_type, category, code_num)

        return new_code

     




class TextureCodeNaming(AssetCodeNaming):

    
    def get_sobject_by_filename(self, filename):
        '''extract the texture code from the filename'''
        base, ext = os.path.splitext(filename)

        # assuming a version (v) in the texture name
        index = base.find("_v")
        if index == -1:
            return None

        texture_code = base[:index]
        #asset_code, tmp = texture_code.split("_")
        sobject = Texture.get_by_code(texture_code)
        return sobject


    def get_next_code(self, sobject):
        '''get the next code'''
        asset_code = sobject.get_value("asset_code")

        columns = ['asset_code']
        code_num = self._get_next_num(sobject, columns)
        padding = self._get_code_padding()
        code_num = str(code_num).zfill( padding )

        # build the new code
        new_code = "%s_%s" % (asset_code, code_num)
        asset_context = sobject.get_value("asset_context")
        if asset_context:
            new_code = "%s_%s" %(new_code, asset_context)


        return new_code

    def _get_code_padding(self):
        return 3


    def _get_next_num(self, sobject, columns):

        # set the default
        code_num = self._get_start_code()

        # get the highest number, extract the number and increase by 1
        search_type = sobject.get_search_type()
        search = Search(search_type)
        search.set_show_retired_flag(True)

        for column in columns:
            value = sobject.get_value(column)
            search.add_filter(column, value)

       
        # order by descending codes
        search.add_order_by("code desc")
        last_sobject = search.get_sobject()
        
        if last_sobject != None:
            code = last_sobject.get_value("code")
            pat = re.compile('.*_(\d+)_?.*')
            m = pat.match(code)
            if m:
                code_num = m.groups()[0]
            if not code_num:
                code_num = 0

            try:
                code_num = int(code_num) + 1
            except ValueError:
                code_num = 1

        return code_num


# Note this class probably should not be here

class FlashAssetNaming(AssetCodeNaming):
    '''class that encapsulates checking of naming conventions'''
    
    def get_sobject_by_filename(self, filename):
        '''extract the code from the filename'''

        index = filename.find(".")
        if index == -1:
            return None

        code = filename[0:index]

        from pyasm.flash.biz import FlashAsset
        asset = FlashAsset.get_by_code(code)
        return asset



class FlashLayerNaming(AssetCodeNaming):
    '''class that encapsulates checking of naming conventions'''

    def get_current_code(self, sobject):
        return "%s_%s" % (sobject.get_value('shot_code'), \
                sobject.get_value('name'))
    
    def get_sobject_by_filename(self, filename):
        '''extract the code from the filename'''
        index = filename.rfind("_")
        if index == -1:
            return None
        ext_index = filename.find(".")

        shot_code = filename[0:index]
        layer_code = filename[index+1:ext_index]
        from pyasm.flash.biz import FlashLayer
        layer = FlashLayer.get(shot_code, layer_code)
        return layer


class FlashShotNaming(AssetCodeNaming):
    '''class that encapsulates checking of naming conventions'''
    
    def get_sobject_by_filename(self, filename):
        '''extract the code from the filename'''

        # EP01A-003.png
        p = re.compile("(\w+)-(\w+).(\w+)")
        m = p.match(filename)
        if not m:
            return None
        groups = m.groups() 
        code = "%s-%s" % (groups[0], groups[1])

        from pyasm.flash.biz import FlashShot
        shot = FlashShot.get_by_code(code)
        return shot

class NatPauseNaming(AssetCodeNaming):
    '''class that encapsulates checking of naming conventions'''
    
    def get_sobject_by_filename(self, filename):
        '''extract the code from the filename'''

        # EP01A_sometext.aiff
        # we can restrict the extension to aiff|mp3 if required in the future
        p = re.compile("(\w+)_(\w+).(\w+)")
        m = p.match(filename)
        if not m:
            return None
        groups = m.groups() 
        episode_code = "%s" % groups[0]
        
        # verify the code
        from pyasm.prod.biz import Episode
        episode = Episode.get_by_code(episode_code)
        if not episode:
            return None

        from pyasm.flash.biz import NatPause
        nat = NatPause.get_by_episode_code(episode_code)
        if not nat:
            nat = NatPause.create(episode_code)

        return nat


class FinalWaveNaming(AssetCodeNaming):
    '''class that encapsulates checking of naming conventions'''
    
    def get_sobject_by_filename(self, filename):
        '''extract the code from the filename'''

        # EP01A_15_sometext.aiff
        # we can restrict the extension to aiff|mp3 if required in the future
        p = re.compile("(\w+)_(\d+)_(\w+).(\w+)")
        m = p.match(filename)
        if not m:
            return None
        groups = m.groups() 
        episode_code = "%s" % groups[0]
        line = groups[1]
        # verify the code
        from pyasm.prod.biz import Episode
        episode = Episode.get_by_code(episode_code)
        if not episode or not line:
            return None

        from pyasm.flash.biz import FinalWave
        wav = FinalWave.get(episode_code, line)
        if not wav:
            wav = FinalWave.create(episode_code, line)

        return wav

class ShotAudioNaming(AssetCodeNaming):
    '''class that encapsulates checking of naming conventions'''
    
    def get_sobject_by_filename(self, filename):
        '''extract the code from the filename'''
        naming = Naming.get_by_search_type('prod/shot_audio')
        if not naming:  
            return None

        shot_code = NamingUtil.extract_sobject_code(naming, filename, 'shot_code')
        # verify the code
        from pyasm.prod.biz import Shot
        shot = Shot.get_by_code(shot_code)
        if not shot:
            return None

        from pyasm.prod.biz import ShotAudio
        audio = ShotAudio.get_by_shot_code(shot_code)
        
        if not audio:
            audio = ShotAudio.create(shot_code)

        return audio


'''new set of CodeNaming classes'''
class ProdAssetCodeNaming(CodeNaming):
    
    def prod_asset(self, code):
        # <asset_library><padding>(whatever)_<related>
        pattern = r"(\w+)(\d{3})(?:[_\w]*_([a-z]+)(\d{2}))?$"
        keys = ["asset_library", "padding", "ext", "related"]
        matches = self._match(pattern, self.code, keys)
        return matches

