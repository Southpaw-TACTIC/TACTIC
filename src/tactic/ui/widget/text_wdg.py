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

    def get_args_keys(self):
        return {
            'length': 'how many charcters to show',
            'text': 'content'
            }

    def init(self):
        self.text = self.kwargs.get('text')
        self.length = self.kwargs.get('length')
        if not self.length:
            self.length = 20
    
    def get_display(self):
        span = SpanWdg()
        if len(self.text) > self.length:
            content = self.text[0:self.length]
            span.add('%s...' %content)
            span.add_tip(self.text, self.text)
        else:
            span.add(self.text)

        return span

