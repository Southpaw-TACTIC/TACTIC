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

__all__ = ["Clipboard"]

from pyasm.common import Container
from pyasm.search import SearchType, SObject, Search, SearchKey


class Clipboard(SObject):
    SEARCH_TYPE = "sthpw/clipboard"

    def get_count(cls, where=None, category=None):
        search = Search(Clipboard)
        search.add_user_filter()
        if not category:
            search.add_filter("category","select")
        if where:
            search.add_where(where)
        return search.get_count()
    get_count = classmethod(get_count)


    def get_search(cls, category=None):
        search = Search(cls.SEARCH_TYPE)
        search.add_user_filter()
        if category:
            search.add_filter("category", category)
        return search
    get_search = classmethod(get_search)

    def get_all(cls, category=None):
        '''get all or all items in a category'''
        search = Clipboard.get_search(category=category)
        return search.get_sobjects()
    
    get_all = classmethod(get_all)


    # special selected methods
    def add_to_selected(cls, search_keys):
        # make sure the sobjects exist
        for search_key in search_keys:
            sobject = SearchKey.get_by_search_key(search_key)
            item = SearchType.create("sthpw/clipboard")
            item.set_user()

            item.add_related_sobject(sobject)
            item.set_value("category", "select")
            item.commit()
    add_to_selected = classmethod(add_to_selected)

    def clear_selected(cls):
        # make sure the sobjects exist
        search = Search("sthpw/clipboard")
        search.add_filter("category", "select")
        search.add_user_filter()
        items = search.get_sobjects()

        for item in items:
            item.delete()
    clear_selected = classmethod(clear_selected)


    def get_selected(cls):
        # make sure the sobjects exist
        search = Search("sthpw/clipboard")
        search.add_filter("category", "select")
        search.add_user_filter()
        items = search.get_sobjects()

        parents = []
        for item in items:
            parent = item.get_parent()
            if parent:
                parents.append(parent)
            else:
                print "WARNING: parent to clipboard item [%s] does not exist" % item.get_code()
        return parents
    get_selected = classmethod(get_selected)


    def is_selected(cls, sobject):
        clipboard_cache = Clipboard._get_cache("select")
        if not sobject:
            return False
        search_key = sobject.get_search_key()
        item = clipboard_cache.get(search_key)
        if item:
            return True
        else:
            return False

    is_selected = classmethod(is_selected)




    def reference_selected(cls, sobject):
        items = cls.get_selected()

        # get all of the items already connected to this sobject
        from pyasm.biz import SObjectConnection
        # create a connection for each item
        for item in items:
            SObjectConnection.create(sobject, item)

    reference_selected = classmethod(reference_selected)






    def _get_cache(cls, category):
        '''preselect all the clipboard items of a particular category'''

        key = "clipboard:%s" % category
        clipboard_cache = Container.get(key)
        if clipboard_cache == None:
            clipboard_cache = {}
            Container.put(key, clipboard_cache)
        else:
            return clipboard_cache

        search = Search(Clipboard)
        search.add_user_filter()
        search.add_filter("category","select")
        items = search.get_sobjects()

        for item in items:
            search_type = item.get_value("search_type")
            search_id = item.get_value("search_id")
            search_key = "%s|%s" % (search_type, search_id)

            clipboard_cache[search_key] = item

        return clipboard_cache
            
    _get_cache = classmethod(_get_cache)




 


