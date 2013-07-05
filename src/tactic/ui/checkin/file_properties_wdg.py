###########################################################
#
# Copyright (c) 2011, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['FilePropertiesWdg']

from pyasm.common import Environment
from pyasm.search import Search
from pyasm.web import DivWdg

from tactic.ui.common import BaseRefreshWdg

import os


class FilePropertiesWdg(BaseRefreshWdg):

    def get_display(my):

        path = my.kwargs.get("path")
        md5 = my.kwargs.get("md5")
        snapshot_code = my.kwargs.get("snapshot_code")

        top = my.top
        top.add_style("padding: 10px")
        top.add_color("background", "background", -5)

        path_div = DivWdg()
        top.add(path_div)
        path_div.add("<b>Local Path: %s</b><br/>" % path)
        path_div.add_style("font-size: 12px")
        path_div.add_style("margin-bottom: 10px")

        info_wdg = DivWdg()
        info_wdg.add_color("background", "background3")
        top.add(info_wdg)
        info_wdg.add("md5: %s<br/>" % md5)
        info_wdg.add("snapshot_code: %s<br/>" % snapshot_code)
        info_wdg.add_style("padding: 5px")


        search_key = my.kwargs.get("search_key")
        sobject = Search.get_by_search_key(search_key)


        # bit of a hack get the file system paths
        #spath = Common.get_filesystem_name(path)
        spath = path.replace(" ", "_")
        search = Search("sthpw/file")
        search.add_sobject_filter(sobject)
        search.add_filter("source_path", spath)
        search.add_order_by("timestamp desc")
        files = search.get_sobjects()

        '''
        files_div = DivWdg()
        files_div.add_style("margin: 5px")
        files_div.add_style("padding: 5px")
        files_div.add_border()

        top.add(files_div)
        '''
        snapshots = []
        for file in files:
            snapshot = file.get_parent()
            snapshots.append(snapshot)

        from tactic.ui.panel import StaticTableLayoutWdg
        table = StaticTableLayoutWdg(search_type="sthpw/snapshot", view="table", show_shelf=False)
        table.set_sobjects(snapshots)
        top.add(table)



        return top



