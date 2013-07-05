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


from pyasm.common import Base 



class SObjectMapping(Base):
    '''Base class for remappaing search types for generic programming'''

    def __init__(my):
        my.mapping = {}


    def get_mapping(my, search_key):
        try:
            return my.mapping[search_key]
        except:
            return search_key



    def get_parent(my, search_key):
        for parent, child in my.mapping.items():
            if child == search_key:
                return parent
        return search_key

