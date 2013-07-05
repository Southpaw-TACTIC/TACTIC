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

__all__ = ['Series', 'Episode']

from pyasm.search import *

class Series(SObject):
    SEARCH_TYPE = "prod/series"


    # Static methods
    def set_series(series):
        SearchType.set_global_template("project", series)
    set_series = staticmethod(set_series)

    def get_current():
        context = SearchType.get_global_template("project")
        return Series.get_by_code(context)
    get_current = staticmethod(get_current)




class Episode(SObject):
    SEARCH_TYPE = "prod/episode"

    def get_search_columns():
        search_columns = ['code', 'description']
        return search_columns
    get_search_columns = staticmethod(get_search_columns)

