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


__all__ = ['TranslationSObj']

from pyasm.search import SObject, Search
from pyasm.common import Container

class TranslationSObj(SObject):
    '''Defines all of the pref settings in the Admin area'''

    SEARCH_TYPE = "sthpw/translation"

    def get(language, msg):
        ''' get thru language and input msg string'''
        dict = TranslationSObj.get_cache_dict()
        main_key = '%s|%s' %(language, msg)
        sobject = None
        if dict.has_key(main_key):
            sobject = dict[main_key]
        else:
            search = Search(TranslationSObj)
            search.add_filter('language', language)
            sobjs = search.get_sobjects()
            for idx, sobj in enumerate(sobjs):
                key = '%s|%s' %(language, sobj.get_value('msgid'))
                TranslationSObj.cache_sobject(key, sobj)
                if key == main_key:
                    sobject = sobj
        return sobject
    get = staticmethod(get)



                



