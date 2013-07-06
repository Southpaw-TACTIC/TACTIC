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

from pyasm.common import *
from pyasm.flash import FlashShot
from pyasm.prod.render import BaseRenderContext

__all__= ['FlashFinalSequenceRenderContext', 'FlashSwfRenderContext']

class FlashFinalSequenceRenderContext(BaseRenderContext):
    '''The context under which a render take place.  This includes all
    of the settings and specific flags for a particular render'''

    def __init__(my, sobject):
        super(FlashFinalSequenceRenderContext,my).__init__()
        my.set_sobject(sobject)
        my.set_context("publish")

        # set a default render polixy
        my.set_policy(None)


        shot = FlashShot.get_by_code(sobject.get_value('shot_code'))
        my.set_shot(shot)
        #my.options = my.get_render_options()
        
    def get_render_dir(my):
        render_dir = '%s/renders/%s' % (Environment.get_tmp_dir(), \
            my.get_sobject().get_value('shot_code'))
        
        return render_dir

    def get_render_log(my):
        return 'renderLog.txt'

    def get_render_file_naming(my):
        ''' returns a tuple of the original file name and final(desired) 
            file name pattern'''
        layer_name = my.get_sobject().get_value('name')
        original_pat = "(%s)(\.img)(\d{4}\.png)" % layer_name
        final_pat = r"\1.\3"
        return original_pat, final_pat
    
   

    def get_file_format(my):
        return 'png'


class FlashSwfRenderContext(FlashFinalSequenceRenderContext):
    
    def get_render_file_naming(my):
        ''' returns a tuple of the original file name and final(desired) 
            file name pattern'''
        layer_name = my.get_sobject().get_value('name')
        original_pat = "(%s)\.(swf|png)$"  % (layer_name)
        final_pat = r"\1.\2" 
        return original_pat, final_pat

    def get_file_format(my):
        return 'swf'
