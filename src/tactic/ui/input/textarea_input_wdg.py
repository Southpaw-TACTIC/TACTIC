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

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.name = self.kwargs.get("name")
        self.text = TextAreaWdg(self.name)
        self.text.add_class("form-control")
        self.text.add_attr("rows", "3")
        self.top = self.text

    def add_class(self, class_name):
        self.text.add_class(class_name)


    def get_display(self):

        return self.top

