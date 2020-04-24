###########################################################
#
# Copyright (c) 2020, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['MultiTextInputWdg']

from pyasm.widget import BaseInputWdg, SelectWdg, TextWdg, IconButtonWdg, IconWdg, HiddenWdg 

from pyasm.web import DivWdg, SpanWdg
from pyasm.widget import TextAreaWdg

from .text_input_wdg import TextInputWdg


class MultiTextInputWdg(BaseInputWdg):

    ARGS_KEYS = {
    }


    def __init__(self, name=None, **kwargs):
        if not name:
            name = kwargs.get("name")
        self.top = DivWdg()
        self.input = None
        self.kwargs = kwargs
        super(MultiTextInputWdg, self).__init__(name)

        if not self.input:
            self.input = TextAreaWdg(name=self.get_input_name())



    def add_style(self, name, value=None):
        self.top.add_style(name, value)

    def set_input(self, input):
        self.input = input
        self.input.set_name(self.get_input_name() )

    def get_input(self):
        return self.input


    def add(self, widget):
        self.top.add(widget)


    def add_behavior(self, behavior):
        return self.input.add_behavior(behavior)



    def get_display(self):

        top = self.top

        value = self.get_value()

        top.add(self.input)
        self.input.set_value(value)


        return top
 




