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


__all__ = ['Translation', 'TranslationGlobal']

from pyasm.search import SObject, Search
from pyasm.common import Container
from pyasm.search import Search


#import gettext
import os

class Translation(SObject):
    '''Defines all of the pref settings in the Admin area'''

    SEARCH_TYPE = "config/translation"


    def install(language=""):
        # get from preferences
        if not language:
            from pyasm.biz import PrefSetting
            language = PrefSetting.get_value_by_key("language")

        # else get from project setting
        #if not language:
        #    from pyasm.prod.biz import ProdSetting
        #    language = ProdSetting.get_by_key("language")

        if os.environ.get("LC_MESSAGES"):
            language = os.environ.get("LC_MESSAGES")

        if os.environ.get("TACTIC_LANG"):
            language = os.environ.get("TACTIC_LANG")

        # else it is english
        if not language:
            language = "en"

        Container.put("language", language)

        # add some localization code
        #gettext.install("messages", unicode=True)
        #path = "%s/src/locale" % Environment.get_install_dir()
        #lang = gettext.translation("messages", localedir=path, languages=[language])
        #lang.install()

        # override the _ function
        import __builtin__
        __builtin__._ = Translation._translate

    install = staticmethod(install)



    def _translate(msg, language=None, chk=None):

        if not language:
            language = Container.get("language")

        sobject = Translation.get(language, msg)
        if sobject:
            if chk:
                chk = chk.strip("...")
                orig = sobject.get_value("en".lower())
                assert(orig)
                assert(orig.startswith(chk))

            msgstr = sobject.get_value(language)
            if not msgstr:
                return "No Translation"
            else:
                return msgstr


        sobject = TranslationGlobal.get(language, msg)
        if sobject:
            if chk:
                chk = chk.strip("...")
                orig = sobject.get_value("en".lower())
                assert(orig)
                assert(orig.startswith(chk))

            msgstr = sobject.get_value(language)
            if not msgstr:
                return "No Translation"
            else:
                return msgstr

        # DEBUG
        #if language != 'en':
        #    return "__%s__" % msg

        return msg

    _translate = staticmethod(_translate)



    def get(cls, language, msg):

        base_language = 'en'

        dictionary = cls.get_cache_dict()
        main_key = '%s|%s' %(language, msg)

        sobject = None
        if dictionary.has_key("__loaded__"):
            sobject = dictionary.get(main_key)
        else:

            dictionary['__loaded__'] = True

            search = Search(cls)
            sobjs = search.get_sobjects()
            for idx, sobj in enumerate(sobjs):

                key = '%s|%s' %(language, sobj.get_value('id'))
                cls.cache_sobject(key, sobj)
                if key == main_key:
                    sobject = sobj

                name = sobj.get_value("name")
                if name:
                    key = '%s|%s' %(language, name)
                    cls.cache_sobject(key, sobj)
                    if key == main_key:
                        sobject = sobj

                key = '%s|%s' %(language, sobj.get_value(base_language))
                cls.cache_sobject(key, sobj)
                if key == main_key:
                    sobject = sobj


                cls.cache_sobject(main_key, sobj)

       
        # autocreate
        """
        if not sobject:
            sobject = SearchType.create(SEARCH_TYPE)
            sobject.set_value(language, msg)
            sobject.commit()
            key = '%s|%s' %(language, sobj.get_value(base_language))
            cls.cache_sobject(key, sobj)
        """

        return sobject
    get = classmethod(get)


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


 


class TranslationGlobal(Translation):
    '''Defines all of the pref settings in the Admin area'''

    SEARCH_TYPE = "sthpw/translation"


 



