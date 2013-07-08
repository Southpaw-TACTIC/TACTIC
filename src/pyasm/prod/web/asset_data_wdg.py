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

__all__ = ['AssetDataLink', 'AssetWdg']

from pyasm.common import *
from pyasm.web import *
from pyasm.widget import *

from shot_navigator_wdg import *


class AssetDataLink(BaseTableElementWdg):

    def get_display(my):

        sobject = my.get_current_sobject()

        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", "AssetWdg")
        url.set_option("asset_code", sobject.get_code())

        ref = url.get_url()

        iframe = Container.get("iframe")
        action = iframe.get_on_script(ref)

        button = IconButtonWdg("Info", IconWdg.INFO)
        button.add_event("onclick", "%s" % action )
        button.add_style("margin: 3px 5px")

        return button




class AssetWdg(Widget):

    def init(my):

        web = WebContainer.get_web()
        asset_code = web.get_form_value("asset_code")

        asset = Asset.get_by_code(asset_code)

        # display some information
        my.add("<div class='admin_header'>Information</div>")

        info = DivWdg()
        info.add_style("border-style: solid")
        info.add_style("border-width: 1px")
        info.add_style("margin: 10px")
        info.add_style("padding: 10px")
        table = Table()
        table.add_row()
        info.add(table)
        my.add(info)

        # Milestone test
        #my.add("<div class='admin_header'>Milestones</div>")
        #milestone = MilestoneWdg()
        #my.add(milestone)

        my.add("<div class='admin_header'>User Task</div>")
        search = Search("sthpw/task")
        search.add_filter("search_type", asset.get_search_type() )
        search.add_filter("search_id", asset.get_id() )
        table = TableWdg("sthpw/task", "artist")
        table.set_search(search)
        my.add(table)




