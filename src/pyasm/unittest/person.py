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

__all__ = ['Person']


from pyasm.search import SObject, SearchType

class Person(SObject):
    
    SEARCH_TYPE ='unittest/person'

    def create( name_first, name_last, nationality, description ):

        person = SearchType.create("unittest/person")

        person.set_value("name_first", name_first)
        person.set_value("name_last", name_last)
        person.set_value("nationality", nationality)
        person.set_value("description", description)

        person.commit()

        return person

    create = staticmethod(create)


