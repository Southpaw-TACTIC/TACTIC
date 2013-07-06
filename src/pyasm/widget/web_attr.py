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

__all__ = ['IconAttr', 'BrandAttr']


from pyasm.search import SObjectAttr, Search
from file_wdg import *


class IconAttr(SObjectAttr):
    '''defines attribute which has a get_display function like all widgets'''

    def get_value(my):
        return my.get_display()

    def get_display(my):
        widget_class = "ThumbWdg"
        widget = eval( "%s()" % widget_class )
        #widget.set_icon_size("")
        widget.set_name("files")
        widget.set_sobjects([my.sobject])

        print widget.get_display()
        return widget



class BrandAttr(SObjectAttr):
    '''defines attribute which has a get_display function like all widgets'''

    def get_value(my):
        return my.get_display()

    def get_display(my):

        brand_code = my.sobject.get_value("brand_code")
        search = Search("pg/brand")
        search.add_filter("brand_code", brand_code)
        brand = search.get_sobject()

        if brand == None:
            return "&nbsp;"

        attr = brand.get_attr("icon_wdg")
        return attr.get_display()







