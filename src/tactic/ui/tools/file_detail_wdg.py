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

__all__ = ['FileDetailWdg']

from tactic.ui.common import BaseRefreshWdg

from pyasm.web import DivWdg, WebContainer, Table, WebState, HtmlElement
from pyasm.search import Search, SearchType, SearchKey
from tactic.ui.panel import TableLayoutWdg

from pyasm.widget import ThumbWdg

import os


class FileDetailWdg(BaseRefreshWdg):
    '''Single File Widget'''

    def get_display(my):

        my.search_key = my.kwargs.get("search_key")
        my.sobject = Search.get_by_search_key(my.search_key)
        snapshot = my.sobject.get_parent()
        parent = snapshot.get_parent()

        top = my.top

        from tactic.ui.container import ResizableTableWdg
        table = ResizableTableWdg()
        top.add(table)
        table.add_row()
        table.add_style("width: 100%")

        #td = table.add_cell()
        #thumb_div = DivWdg()
        #td.add(thumb_div)
        #thumb = ThumbWdg()
        #thumb_div.add(thumb)
        #thumb_div.add_class("spt_resizable")
        #thumb.set_sobject(parent)
        #thumb.set_icon_size(120)

        from tactic.ui.widget import EmbedWdg
        td = table.add_cell()
        td.add_color("background", "background",)
        td.add_style("vertical-align: middle")
        td.add_style("height: 200px")
        td.add_style("overflow-x: auto")


        file_type = "icon"
        thumb_path = snapshot.get_web_path_by_type(file_type)

        file_type = "main"
        src = snapshot.get_web_path_by_type(file_type)


        #src = my.sobject.get_web_path()
        parts = os.path.splitext(src)
        ext = parts[1]
        ext = ext.lower()

        if ext in ['.doc','.xls']:
            from pyasm.widget import ThumbWdg
            link = ThumbWdg.find_icon_link(src)
            img = HtmlElement.img(src=link)
            href = DivWdg()
            href.add_style("text-align: center")
            href.add(img)
            td.add(href)
            href.add_behavior( {
                'type': 'click_up',
                'src': src,
                'cbjs_action': '''
                window.open(bvr.src);
                '''
            } )
            href.add_class("hand")

        else:
            embed_wdg = EmbedWdg(src=src, thumb_path=thumb_path)
            td.add(embed_wdg)
            embed_wdg.add_style("margin: auto auto")
            embed_wdg.add_class("spt_resizable")
            embed_wdg.add_style("width: 100%")
            embed_wdg.add_style("height: 240px")

            embed_wdg.add_behavior( {
                'type': 'load',
                'cbjs_action': '''
                var last_height = spt.container.get_value("last_img_height");
                if (last_height) {
                    bvr.src_el.setStyle("height", last_height);
                }
                '''
            } )


            embed_wdg.add_behavior( {
                'type': 'unload',
                'cbjs_action': '''
                var last_height = bvr.src_el.getStyle("height");
                spt.container.set_value("last_img_height", last_height);
                '''
            } )



        table.add_row()
        td = table.add_cell()


        from tactic.ui.checkin import PathMetadataWdg
        from tactic.ui.checkin import SnapshotMetadataWdg


        metadata_div = DivWdg()
        td.add(metadata_div)
        metadata_div.add_style("max-height: 400px")
        metadata_div.add_style("overflow-y: auto")
        metadata_div.add_style("overflow-x: hidden")

        parser = my.kwargs.get("parser")
        if parser:
            file_type = "main"
            server_src = snapshot.get_lib_path_by_type(file_type)

            metadata_wdg = PathMetadataWdg(path=server_src, parser=parser)
            metadata_div.add(metadata_wdg)
        else:
            metadata_wdg = SnapshotMetadataWdg(snapshot=snapshot)
            metadata_div.add(metadata_wdg)


        top.add("<br/>")

        return top


