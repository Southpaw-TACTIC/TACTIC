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


__all__ = ['Folder']

from pyasm.search import SObject, Search
from pyasm.common import Container, TacticException, Environment

class Folder(SObject):
    '''Defines all of the settings for a given production'''

    SEARCH_TYPE = "sthpw/folder"


    def get_children(my):
        search = Search(Folder)
        search.add_filter("parent_id", my.get_id() )
        return search.get_sobjects()


    def create(my, parent, subdir, sobject):

        folder = SearchType.create(Folder)
        if parent:
            folder.set_value("parent_id", parent.get_id() )
            parent_path = parent.get_value("path")

            path = "%s/%s" % (parent_path,subdir)
            folder.set_value("path", path)
        else:
            folder.set_value("path", "/")

        folder.set_value("search_type", sobject.get_search_type() )
        folder.set_value("search_id", sobject.id() )
            
        folder.commmit()
        return folder






