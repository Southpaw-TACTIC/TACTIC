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


__all__ = ['Translation', 'TranslationSObj']

from pyasm.search import SObject, Search
from pyasm.common import Container

import os

class Translation(SObject):
    '''Defines all of the pref settings in the Admin area'''

    SEARCH_TYPE = "config/translation"

    def get(language, msg):

        base_language = 'en'.lower()

        dict = Translation.get_cache_dict()
        main_key = '%s|%s' %(language, msg)
        sobject = None
        if dict.has_key(main_key):
            sobject = dict[main_key]
        else:
            search = Search(Translation)
            sobjs = search.get_sobjects()
            for idx, sobj in enumerate(sobjs):

                key = '%s|%s' %(language, sobj.get_value('id'))
                Translation.cache_sobject(key, sobj)
                if key == main_key:
                    sobject = sobj

                name = sobj.get_value("name")
                if name:
                    key = '%s|%s' %(language, name)
                    Translation.cache_sobject(key, sobj)
                    if key == main_key:
                        sobject = sobj

                key = '%s|%s' %(language, sobj.get_value(base_language))
                Translation.cache_sobject(key, sobj)
                if key == main_key:
                    sobject = sobj

       
        # autocreate
        """
        if not sobject:
            sobject = SearchType.create(SEARCH_TYPE)
            sobject.set_value(language, msg)
            sobject.commit()
            key = '%s|%s' %(language, sobj.get_value(base_language))
            Translation.cache_sobject(key, sobj)
        """

        return sobject
    get = staticmethod(get)


    def get_language():
        lang = Container.get("language")
        if lang:
            return lang

        import os
        lang = os.environ.get('TACTIC_LANG')
        if not lang:
            lang = 'en'


        return lang
    get_language = staticmethod(get_language)


 


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

                key = '%s|%s' %(language, sobj.get_value('id'))
                TranslationSObj.cache_sobject(key, sobj)
                if key == main_key:
                    sobject = sobj

                key = '%s|%s' %(language, sobj.get_value('msgid'))
                TranslationSObj.cache_sobject(key, sobj)
                if key == main_key:
                    sobject = sobj

        return sobject
    get = staticmethod(get)



 



