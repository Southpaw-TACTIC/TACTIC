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

__all__ = ["CustomScript"]

from pyasm.search import SearchType, SObject, Search

import os


class CustomScript(SObject):

    def get_by_path(cls, path):

        dirname = os.path.dirname(path)
        basename = os.path.basename(path)

        search = Search("config/custom_script")
        search.add_filter('folder', dirname)
        search.add_filter('title', basename)
        sobject = search.get_sobject()

        return sobject

    get_by_path = classmethod(get_by_path)



