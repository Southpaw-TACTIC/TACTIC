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

__all__ = [ 'FlashLayerCheckboxWdg','FlashAssetCheckboxWdg', 
            'FlashShotInstanceCheckboxWdg', 'FlashShotCheckboxWdg']


from pyasm.widget import CheckboxColWdg
from pyasm.flash import *



class FlashLayerCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with select-all control'''
    
    CB_NAME = 'flash_layer'
    def set_cb_name(my):
        my.name = my.CB_NAME

    
class FlashAssetCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with select-all control'''
    
    CB_NAME = 'flash_asset'
    def set_cb_name(my):
        my.name = my.CB_NAME

class FlashShotInstanceCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with select-all control'''
    
    CB_NAME = 'flash_shot_instance'
    def set_cb_name(my):
        my.name = my.CB_NAME
   
    def get_sobject(my):
        return my.get_current_sobject().get_reference('flash/asset')  


class FlashShotCheckboxWdg(CheckboxColWdg):
    '''widget to display a checkbox in the column with select-all control'''
    
    CB_NAME = 'flash_shot'
    def set_cb_name(my):
        my.name = my.CB_NAME


