###########################################################
#
# Copyright (c) 2005-2014, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ["TextAreaInputWdg"]


from pyasm.widget import TextAreaWdg, BaseInputWdg


class TextAreaInputWdg(BaseInputWdg):

    def __init__(my, **kwargs):
        my.kwargs = kwargs

        my.name = my.kwargs.get("name")
        my.text = TextAreaWdg(my.name)
        my.text.add_class("form-control")
        my.text.add_attr("rows", "3")
        my.top = my.text

    def add_class(my, class_name):
        my.text.add_class(class_name)


    def get_display(my):

        return my.top

