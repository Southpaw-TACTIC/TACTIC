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
__all__ = ['FlashAssetHistoryWdg']

from pyasm.web import Table, Widget, HtmlElement, WebContainer, DivWdg
from pyasm.widget import ThumbWdg, DateTimeWdg, UpdateWdg, DependencyLink, IconWdg, SubmissionLinkWdg, WikiElementWdg, TableWdg
from pyasm.search import Search, SearchKey
from pyasm.prod.web import RenderLinkTableElement, AssetHistoryWdg
from tactic.ui.panel import TableLayoutWdg

class FlashAssetHistoryWdg(AssetHistoryWdg):

    def init_dynamic(args):
        widget = FlashAssetHistoryWdg()
        return widget
    init_dynamic = staticmethod(init_dynamic)


    def get_default_versions_filter(my):
        return "last 10"

    def get_table(my, sobject, snapshots):
        parent_key = SearchKey.get_by_sobject(sobject)
        table = TableLayoutWdg(table_id='snapshot_history_table', search_type='sthpw/snapshot', view='checkin_history', show_search_limit=False, show_gear=False, show_insert=False, parent_key=parent_key, mode='simple')
        table.set_sobjects(snapshots)

        return table
        """
        table = Table()
        table.set_class("embed")
        table.add_style("font-size: 0.9em")
        table.set_max_width()

        table.add_row()
        
        table.add_header("&nbsp;")
        table.add_header("Snapshot")
        table.add_header("Context")
        table.add_header("Ver#")
        table.add_header("Rev#")
        table.add_header("Level")
        table.add_header("Type")
        table.add_header("Dependency")
        table.add_header("User")
        table.add_header("Time")
        table.add_header("Comment")
        table.add_header("Submit")
        table.add_header("Render")
        table.add_header("Update")


        status = [None, IconWdg.GOOD, IconWdg.ERROR]
        import random
       
        thumb = ThumbWdg()
        thumb.set_sobjects(snapshots)
        thumb.preprocess()
        for idx, snapshot in enumerate(snapshots):

            tr = table.add_row()
            tr.add_style("display", "table-row")
            row_id = "%s%s" % (TableWdg.ROW_PREFIX, snapshot.get_search_key())
            tr.set_id( row_id )

            if snapshot.is_current():
                current = IconWdg("current", IconWdg.CURRENT)
                table.add_cell(current)
            else:
                table.add_blank_cell()

            
            thumb.set_name("snapshot")
            thumb.set_current_index(idx)
            thumb.set_icon_size(60)
            table.add_cell(thumb.get_buffer_display())

            time_wdg = DateTimeWdg("timestamp")
            time_wdg.set_sobject(snapshot)

            dependency = DependencyLink()
            dependency.set_sobject(snapshot)

            context = snapshot.get_value("context")
            if context == "":
                context = "N/A"
            version = snapshot.get_value("version")
            if not version:
                version = 1
            revision = snapshot.get_value("revision", no_exception=True)

            table.add_cell( "<b>%s</b>" % context )
            table.add_cell( "v%0.3d" % version )
            if revision:
                table.add_cell( "r%0.3d" % revision )
            else:
                table.add_cell( "---")

            # add level
            level_type = snapshot.get_value("level_type")
            level_id = snapshot.get_value("level_id")
            if level_type and level_id:
                sobject = Search.get_by_id(level_type, level_id)
                table.add_cell(sobject.get_code())
            else:
                table.add_cell("---")


            table.add_cell( snapshot.get_value("snapshot_type") )
            table.add_cell( dependency )
            table.add_cell( snapshot.get_value("login") )
            table.add_cell( time_wdg)
            wiki_wdg = WikiElementWdg("description")
            wiki_wdg.set_sobject(snapshot)
            table.add_cell( wiki_wdg )


            submit_wdg = SubmissionLinkWdg(snapshot.get_search_type(),\
                snapshot.get_id())
            submit_wdg.set_sobjects(snapshots)
            submit_wdg.set_current_index(idx)
            table.add_cell(submit_wdg)

            render_link = RenderLinkTableElement()
            render_link.set_sobject(snapshot)
            table.add_cell( render_link )

            update_wdg = UpdateWdg()
            update_wdg.set_name("update")
            update_wdg.set_sobjects(snapshots)
            update_wdg.set_current_index(idx)
            table.add_cell(update_wdg)


        return table
        """



