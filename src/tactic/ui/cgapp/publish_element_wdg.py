###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['PublishElementWdg']

import types, re

from pyasm.common import Container
from pyasm.biz import Project
from pyasm.web import Table, HtmlElement, SpanWdg, DivWdg
from pyasm.widget import CheckboxWdg, ThumbWdg, IconWdg, SwapDisplayWdg, TextAreaWdg
from tactic.ui.common import BaseTableElementWdg

from pyasm.prod.biz import SessionContents
from pyasm.prod.load import ProdLoaderContext

from tactic.ui.filter import FilterData


class PublishElementWdg(BaseTableElementWdg):
    '''Snapshot publish for any search type'''
    

    def get_display(self):

        top = DivWdg()

        text = TextAreaWdg()
        text.add_style("width: 98%")
        text.add_style("height: 90%")
        top.add(text)
        return top
