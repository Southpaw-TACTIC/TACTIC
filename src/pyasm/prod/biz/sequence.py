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

__all__ = ['Sequence', 'CutSequence']


from pyasm.search import *


class Sequence(SObject):

    #SEARCH_TYPE = "{prod}/sequence"
    SEARCH_TYPE = "prod/sequence"


    def get_code(self):
        return self.get_value("code")


    # Static methods
    def get_search_columns():
        search_columns = ['code', 'description']
        return search_columns
    get_search_columns = staticmethod(get_search_columns)

    def create(code, description):
        sequence = SObjectFactory.create( Sequence.SEARCH_TYPE )
        sequence.set_value("code",code)
        sequence.set_value("description",description)
        sequence.commit()
        return sequence
    create = staticmethod(create)

    def get_order():
        search = Search(Sequence.SEARCH_TYPE)
        search.add_order_by('sort_order')
        sobjs = search.get_sobjects()
        order = SObject.get_values(sobjs, 'code', unique=False)
        return order
    get_order = staticmethod(get_order)

class CutSequence(SObject):
    ''' Cut sequence in the form of quicktime'''
    SEARCH_TYPE = "prod/cut_sequence"




