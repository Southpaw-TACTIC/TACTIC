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
from pyasm.biz import Snapshot
from pyasm.widget import TextAreaWdg
from tactic.ui.panel import TableLayoutWdg

from pyasm.widget import ThumbWdg

import os


class FileDetailWdg(BaseRefreshWdg):
    '''Single File Widget'''

    def get_display(my):

        my.search_key = my.kwargs.get("search_key")
        sobject = Search.get_by_search_key(my.search_key)

        if sobject.get_base_search_type() == "sthpw/snapshot":
            snapshot = sobject
        elif sobject.get_base_search_type() == "sthpw/file":
            # if it is a file object
            snapshot = sobject.get_parent()
        else:
            snapshots = Snapshot.get_by_sobject(sobject)
            snapshot = snapshots[0]

        #parent = snapshot.get_parent()

        top = my.top

        from tactic.ui.container import ResizableTableWdg
        table = ResizableTableWdg()
        top.add(table)
        table.add_row()
        table.add_style("width: 100%")


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
        lib_path = snapshot.get_lib_path_by_type(file_type)


        parts = os.path.splitext(src)
        ext = parts[1]
        ext = ext.lower()


        content_div = DivWdg()

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

        elif ext in ['.txt','.html', '.ini']:
            f = open(lib_path, 'r')
            content = f.read(10000)
            f.close()
            if not content:
                text = "No Content"
            else:

                size = os.path.getsize(lib_path)

                from pyasm.common import FormatValue
                value = FormatValue().get_format_value(size, "KB")

                content_div.add("Showing first 10K of %s<hr/>" % value)

                text = TextAreaWdg()
                text.add(content)
                text.add_style("width: 100%")
                text.add_style("height: 300px")
                text.add_style("padding: 10px")
                text.add_style("border: none")
                text.add_attr("readonly", "true")

            content_div.add(text)
            td.add(content_div)
            content_div.add_style("color", "#000")
            content_div.add_style("width", "auto")
            content_div.add_style("margin", "20px")


        elif thumb_path == "__DYNAMIC__":
            td.add("No Preview")
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
        use_tactic_tags = my.kwargs.get("use_tactic_tags")

        file_type = "main"
        server_src = snapshot.get_lib_path_by_type(file_type)

        # get it dynamically by path
        metadata_wdg = PathMetadataWdg(path=server_src, parser=parser, use_tactic_tags=use_tactic_tags)
        metadata_div.add(metadata_wdg)

        #else:
        #    metadata_wdg = SnapshotMetadataWdg(snapshot=snapshot)
        #    metadata_div.add(metadata_wdg)


        top.add("<br/>")

        return top


