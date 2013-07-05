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

__all__ = ["FlashCodeNaming"]

from pyasm.biz import CodeNaming

import re


class FlashCodeNaming(CodeNaming):


    """
    def flash_asset(my, code):
        # <episode_code>_<asset_library><padding>_<related>
        pattern = r"(\w+)-(\w+)(\d{3})_?([a-z]+)?(\d{2})?"
        keys = ["episode_code", "asset_library", "padding", "ext", "related"]
        matches = my._match(pattern, my.code, keys)
        return matches
    """

    def flash_asset(my, code):
        # <asset_library><padding>(whatever)_<related>
        pattern = r"(\w+)(\d{3})(?:[_\w]*_([a-z]+)(\d{2}))?$"
        keys = ["asset_library", "padding", "ext", "related"]
        matches = my._match(pattern, my.code, keys)
        return matches



    def flash_shot(my, code):
        padding = 3
        # <episode_code>_<asset_library><padding>_<related>
        pattern = r"(\w+)-(\d{%d})" % padding
        keys = ["episode_code", "padding"]
        matches = my._match(pattern, my.code, keys)
        return matches




