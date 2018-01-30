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

__all__ = ['ProdDirNaming']

from pyasm.biz import DirNaming
from pyasm.search import SearchType


class ProdDirNaming(DirNaming):


    def _get_subdir(self, snapshot):
        '''make the sub directory look like a maya project'''
        context = snapshot.get_value("context")
        snapshot_type = snapshot.get_value("snapshot_type")

        if context == "none" or context == "icon":
            subdir = "icon"
        elif snapshot_type == "texture":
            subdir = "textures"
        elif context == "render":
            subdir = "images"
        else:
            subdir = "scenes"
        return subdir




    def prod_asset(self, dirs):

        dirs = self.get_default(dirs)

        template = "{asset_library}/{code}"
        dirs.extend( self.get_template_dir(template) )

        if self.snapshot:
            subdir = self._get_subdir(self.snapshot)
            dirs.append( subdir )


        return dirs


    def prod_shot_instance(self, dirs):
        
        dirs = self.get_parent_dir("prod/shot")
        
        #template = "instance/{name}"
        #dirs.extend( self.goet_template_dir(template) )
        dirs.append("instance")

        return dirs


    def prod_texture(self, dirs):

        parent_context = self.sobject.get_value("asset_context")

        # get the the assets directory
        dirs = self.get_parent_dir("prod/asset", parent_context)

        # replace the scenes directory
        #if not parent_context:
        #    dirs[-1] = "textures"
        #else:
        #    dirs.append("textures")
        if dirs[-1] == "scenes":
            dirs[-1] = "textures"
        else:
            dirs.append("textures")

        return dirs


    def prod_shot_texture(self, dirs):
        parent_context = self.sobject.get_value("asset_context")

        # get the the assets directory
        dirs = self.get_parent_dir(context=parent_context)
        
        dirs.append("textures")

        return dirs



    def prod_texture_source(self, dirs):
        ''' can't use prod_texture any more since it uses
            asset_context'''
        dirs = self.get_parent_dir("prod/asset")
        
        dirs.append("textures")
        return dirs

    """
    def prod_shot(self, dirs):            
            shot = self.sobject
            snapshot = self.snapshot
            print 'shot', shot
            print 'dict', shot.data
            print 'id', shot.get_value('id')
            print 'snapshot', snapshot
            #if shot.get_value('id') == -1:
            #        return 
            #if snapshot.get_context() == "icon":
            #	return super(SheenCustomDirNaming, self).prod_shot(dirs)
    
            dirs.append("sheen")
            dirs.append("episodes")
    
            # get the shot code...i.e. - 1001_01_001_00
            shot_code = shot.get_code()
            shot_tokens = shot_code.split('_',3)
            print 'shot code', shot_code
            # get/add the episode
            dirs.append(shot_tokens[1])
    
            # get/add the sequence code...batv_1001_01
            dirs.append(shot_tokens[2])
    
            # get/add episode number from sequence code
            dirs.append(shot_tokens[3])

            # get snapshot context
            snapshot_context = snapshot.get_context()
                
            # determine if has subcontext --> blocking/review...blocking/scene
            snapshot_context_tokens = snapshot_context.split("/")
            
            if len(snapshot_context_tokens) == 2:
                dirs.append(snapshot_context_tokens[0])
                dirs.append(snapshot_context_tokens[1])                    
            else:
                # get/add context from snapshot
                dirs.append(snapshot_context)		
    
            return dirs

    """

    def prod_shot(self, dirs):
        dirs = self.get_default(dirs)

        # TODO: have to put seqeuence code in there sometime
        #template = "{sequence_code}/{code}"
        template = "{code}"
        dirs.extend( self.get_template_dir(template) )

        if self.snapshot:
            subdir = self._get_subdir(self.snapshot)
            dirs.append( subdir )

            if self.snapshot.get_value("context") == "cache":
                dirs.append( "data" )

        return dirs
   
    def prod_sequence(self, dirs):
        dirs = self.get_default(dirs)

        template = "{code}"
        dirs.extend( self.get_template_dir(template) )

        if self.snapshot:
            context = self.snapshot.get_value("context")
            dirs.append( context )


        return dirs

    def prod_submission(self, dirs):
        dirs = self.get_default(dirs)

        bins = self.sobject.get_bins()
        if not bins:
            return dirs
        
        bin = bins[0]
        type = bin.get_value("type")
        dirs.append(type)
        label = bin.get_value("label")
        if label:
            dirs.append(label)
        code = bin.get_value("code")
        dirs.append(code)

        return dirs


    def prod_render(self, dirs):
        dirs = self.get_default(dirs)

        search_type = SearchType.get( self.sobject.get_value("search_type") )
        table = search_type.get_table()
        dirs.append( table )

        base_search_type = search_type.get_base_search_type()

        parent = self.sobject.get_parent()

        if base_search_type =='prod/layer':
            shot_code = parent.get_value('shot_code')
            name = parent.get_value('name')
            dirs.append(shot_code)
            dirs.append(name)
        else:
            code = parent.get_code()
            dirs.append( code )

        if self.snapshot:
            version = self.snapshot.get_value("version")
        if not version:
            version = 1
        dirs.append("v%0.3d" % int(version))

        return dirs

    def prod_composite(self, dirs):
        dirs = self.get_default(dirs)

        sobject = self.sobject
        shot_code = sobject.get_value('shot_code')
        dirs.append(shot_code)
        context = self.snapshot.get_value("context")
        dirs.append(context)
        return dirs
    
    def effects_plate(self, dirs):
        dirs = self.get_default(dirs)

        dirs.extend(self.get_template_dir('{shot_code}'))
        if self.snapshot:
            version = self.snapshot.get_value("version")
        if not version:
            version = 1
        dirs.append("v%0.3d" % int(version))

        return dirs

