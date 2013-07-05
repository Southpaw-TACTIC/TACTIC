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

from pyasm.web import DivWdg, HtmlElement
from tactic.ui.common import BaseRefreshWdg


class BaseExampleWdg(BaseRefreshWdg):

    def setup_next_example(my, div, msg):
        my.example_count += 1

        div.add( '<br/>' )
        div.add( '<hr>' )

        if msg:
            title = HtmlElement.p()
            title.add_looks( "fnt_title_3" )
            title.add( "Example #%s" % my.example_count )

            description = HtmlElement.p()
            description.add_looks( "fnt_text" )
            description.add( msg )

            div.add( title )
            div.add( description )

        div.add( '<br/>' )


    def get_display(my):
        my.example_count = 0

        div = DivWdg()

        div.add( "<BR/>" )
        ex_title_div = DivWdg()
        ex_title_div.add_looks( "fnt_title_2" )
        ex_title_div.add( my.get_example_title() )
        div.add( ex_title_div )
        div.add( "<BR/>" )

        ex_desc_div = DivWdg()
        ex_desc_div.add( my.get_example_description() )
        ex_desc_div.add_looks( "fnt_title_5 fnt_italic" )
        ex_desc_div.add_styles( "padding-left: 12px;" )
        div.add( ex_desc_div )

        div.add( "<BR/>" )

        ex_div = my.get_example_display()
        ex_div.add_styles( "margin-left: 10px;" )
        div.add( ex_div )

        div.add( "<BR/>" )

        return div


