###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["LimitedTextWdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg

from tactic.ui.common import BaseRefreshWdg


class LimitedTextWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
            'length': 'how many charcters to show',
            'text': 'content'
            }

    def init(my):
        my.text = my.kwargs.get('text')
        my.length = my.kwargs.get('length')
        if not my.length:
            my.length = 20
    
    def get_display(my):
        span = SpanWdg()
        if len(my.text) > my.length:
            content = my.text[0:my.length]
            span.add('%s...' %content)
            span.add_tip(my.text, my.text)
        else:
            span.add(my.text)

        return span

