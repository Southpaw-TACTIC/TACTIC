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
__all__ = ["AssetLibraryTypeWdg"]

from pyasm.widget import *
from pyasm.search import SearchType



class AssetLibraryTypeWdg(SelectWdg):

    def init(my):
        my.set_name("type")
        
    def get_display(my):

        project = SearchType.get_project()
        
        my.set_option("labels", "%s|general" % (project))
        my.set_option("values", "%s|gen" % (project))
        return super(AssetLibraryTypeWdg,my).get_display()
    





