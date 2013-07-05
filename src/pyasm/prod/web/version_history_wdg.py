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

"""
__all__ = ['VersionHistoryWdg']

from pyasm.common import Xml
from pyasm.search import Search
from pyasm.biz import Snapshot
from pyasm.web import *
from pyasm.prod.biz import Render
from pyasm.widget import BaseTableElementWdg, IconWdg

class VersionHistoryWdg(BaseTableElementWdg):

    def get_display(my):

        widget = DivWdg()
        widget.add_style("height: 100%")

        sobject = my.get_current_sobject()
        if isinstance(sobject, Render):
            session_xml = sobject.get_xml_value("session")
        else:
            # try last render with this asset
            search = Search( Render.SEARCH_TYPE )
            search.add_filter("search_type", sobject.get_search_type() )
            search.add_filter("search_id", sobject.get_id() )
            search.add_order_by("timestamp desc")
            last_render = search.get_sobject()

            if last_render == None:
                widget.add("No renders")
                return widget

            session_xml = last_render.get_xml_value("session")


        if session_xml == None:
            widget.add("No renders")
            return widget


        nodes = session_xml.get_nodes("session/node")


        table = Table()
        table.add_style("width: 250")

        for node in nodes:
            instance = Xml.get_attribute(node, "instance")
            snapshot_code = Xml.get_attribute(node, "ref_snapshot_code")

            table.add_row()
            table.add_cell("%s" % instance )

            if snapshot_code == "":

                # backwards compatiility
                snapshot_code = Xml.get_attribute(node, "asset_snapshot_code")
                if snapshot_code == "":
                    table.add_cell( "!")
                    table.add_cell( "!")
                    print "Skipping: ", instance
                    continue

            # get the snapsht that this refering to
            snapshot = Snapshot.get_by_code(snapshot_code)
            if snapshot == None:
                print "Skipping snapshot_code '%s': does not exist" % snapshot_code
                continue
            context = snapshot.get_value("context")

            # if this was rendered with a proxy
            if context == "proxy":
                pass

            search_type = snapshot.get_value("search_type")
            search_id = snapshot.get_value("search_id")
            version = snapshot.get_value("version")



            # get the latest for these conditions
            latest = Snapshot.get_latest(search_type,search_id,context)
            latest_version = latest.get_value("version")

            if version < latest_version:
                dot = "red"
            else:
                dot = "green"

            td = table.add_cell("v%s (v%s)" % (version, latest_version) )
            td.add_style("width: 40px")
            td = table.add_cell( HtmlElement.img("/context/icons/common/dot_%s.png" % dot) )
            td.add_style("width: 20px")

        widget.add( table )

        return widget
"""
