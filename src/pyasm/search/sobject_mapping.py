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

    def __init__(self):
        self.mapping = {}


    def get_mapping(self, search_key):
        try:
            return self.mapping[search_key]
        except:
            return search_key



    def get_parent(self, search_key):
        for parent, child in self.mapping.items():
            if child == search_key:
                return parent
        return search_key

