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

from pyasm.web import *
from pyasm.widget import *
from pyasm.biz import *
from pyasm.flash import *
from pyasm.flash.widget import *


class FlashFunpackBuilderWdg(Widget):

    def init(my):

        div = DivWdg()
        div.set_class("admin_section")
        div.add_style("width: 80%")
        div.center()


        header = DivWdg()
        header.set_style("text-align: center")
        episode_filter = EpisodeNavigatorWdg()
        episode = episode_filter.get_value()
        header.add(episode_filter)
        header.add( IconRefreshWdg() )
        div.add(header)
        div.add("<br/>")

        header = DivWdg("Synopsis")
        header.set_class("admin_header")
        div.add(header)

        div.add( my.get_synopsis() )

        # Storyboard
        header = DivWdg("Storyboard")
        header.set_class("admin_header")
        div.add(header)

        search = Search("prod/storyboard")
        search.add_filter("episode_code", episode)
        sobjects = search.get_sobjects()

        table = Table()
        for sobject in sobjects:

            thumb = ThumbWdg("files")
            thumb.set_sobject(sobject)

            table.add_row()
            table.add_cell( thumb )

        div.add(table)


        # Storyboard
        header = DivWdg("Script")
        header.set_class("admin_header")
        div.add(header)

        search = Search("prod/script")
        search.add_filter("episode_code", episode)
        sobjects = search.get_sobjects()

        table = Table()
        for sobject in sobjects:

            thumb = ThumbWdg("files")
            thumb.set_sobject(sobject)

            table.add_row()
            table.add_cell( thumb )

        div.add(table)




        # Assets
        header = DivWdg("Assets")
        header.set_class("admin_header")
        div.add(header)

        search = Search("flash/asset")
        search.add_filter("episode_code", episode)
        sobjects = search.get_sobjects()

        table = Table()
        table.add_row()
        for sobject in sobjects:

            thumb = ThumbWdg()
            thumb.set_name("snapshot")
            thumb.set_sobject(sobject)

            table.add_cell( thumb )

        div.add(table)


        my.add(div)




    def get_synopsis(my):

        return '''
<pre>
Once upon a time I dreamed there were castles
And you were a princess once upon a time
Once upon a time I dreamed of a kingdom
Of a far magic land once upon a time

In those days there were dragons and witches and wise men
And a man could live by the strength in his arm
And the strongest and bravest of all was the king
And he kept his kingdom safe from all harm

...
</pre>
    '''

