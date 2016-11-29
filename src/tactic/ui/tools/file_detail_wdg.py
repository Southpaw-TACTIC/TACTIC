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
from pyasm.widget import IconWdg

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
            snapshots = Snapshot.get_by_sobject(sobject, is_latest=True)
            snapshot = snapshots[0]

        # Extension determine UI class for preview
        thumb_path = snapshot.get_web_path_by_type("icon")
        web_src = snapshot.get_web_path_by_type("web")

        from pyasm.biz import File
        file_type = "main"
        lib_path = snapshot.get_lib_path_by_type(file_type)
        src = snapshot.get_web_path_by_type(file_type)
        if not web_src:
            web_src = src
        
        parts = os.path.splitext(src)
        ext = parts[1]
        ext = ext.lstrip(".")
        ext = ext.lower()
        
        #parent = snapshot.get_parent()

        top = my.top

        if ext == "pdf":
            iframe = HtmlElement.iframe()
            iframe.set_attr('src', src)
            iframe.add_style("width: 100%")
            iframe.add_style("height: 800px")
            top.add(iframe)
            return top

        from tactic.ui.container import ResizableTableWdg
        table = ResizableTableWdg()
        top.add(table)
        tr = table.add_row()

        # These bvrs allow for smooth switching if switching between files 
        # like in the RepoBrowserWdg
        tr.add_style("height: 200px")
        load_height_bvr = {
            'type': 'load',
            'cbjs_action': '''
            var last_height = spt.container.get_value("last_img_height");
            if (last_height) {
                bvr.src_el.setStyle("height", last_height);
            } 
            '''
        } 
        tr.add_behavior(load_height_bvr)

        unload_height_bvr = {
            'type': 'unload',
            'cbjs_action': '''
            var last_height = bvr.src_el.getStyle("height");
            spt.container.set_value("last_img_height", last_height);
            '''
        }
        tr.add_behavior(unload_height_bvr)

        table.add_style("width: 100%")
        table.add_style("text-align", "center")

        from tactic.ui.widget import EmbedWdg
        td = table.add_cell()
        td.add_color("background", "background",)
        td.add_style("vertical-align: middle")
        td.add_style("height: inherit")
        td.add_style("overflow-x: auto")


        if ext in ['txt','html', 'ini']:
            content_div = DivWdg()
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
                text.add_style("height: 100%")
                text.add_style("padding: 10px")
                text.add_style("border: none")
                text.add_attr("readonly", "true")

            content_div.add(text)
            td.add(content_div)
            content_div.add_style("color", "#000")
            content_div.add_style("width", "auto")
            content_div.add_style("margin", "20px")
            content_div.add_style("height", "100%")
 
        elif ext in File.IMAGE_EXT or ext == "gif":
            if lib_path.find("#") != -1:
                img = DivWdg()

                file_range = snapshot.get_file_range()
                file_range_div = DivWdg()
                file_range_div.add("File Range: %s" % file_range.get_display())
                img.add(file_range_div)
                file_range_div.add_style("font-size: 1.4em")
                file_range_div.add_style("margin: 15px 0px")

                """
                left_chevron = IconWdg("Previous", "BS_CHEVRON_LEFT")
                file_range_div.add(left_chevron)
                right_chevron = IconWdg("Next", "BS_CHEVRON_RIGHT")
                file_range_div.add(right_chevron)
                """


                expanded_paths = snapshot.get_expanded_web_paths()
                lib_paths = snapshot.get_expanded_lib_paths()
                lib_path = lib_paths[0]

                items_div = DivWdg()
                img.add(items_div)
                items_div.add_style("width: auto")

                for path in expanded_paths:
                    item = HtmlElement.img(src=path)
                    items_div.add(item)
                    item.add_style("max-height: 300px")
                    item.add_style("height: auto")
                    item.add_style("display: inline-block")
                    item.add_class("spt_resizable")

                img.add_style("margin: 20px")
                img.add_style("max-height: 400px")
                img.add_style("overflow-y: auto")
                img.add_style("overflow-hidden: auto")
                img.add_style("text-align: left")

                    
            else:
                if ext == "gif":
                    img = HtmlElement.img(src=src)
                else:
                    img = HtmlElement.img(src=web_src)
                img.add_style("height: inherit")
                img.add_style("width: auto")
            td.add(img)
        elif ext in File.VIDEO_EXT:
            embed_wdg = EmbedWdg(src=src, thumb_path=thumb_path, preload="auto", controls=True)
            td.add(embed_wdg)
            
            embed_wdg.add_style("margin: auto auto")
            embed_wdg.add_class("spt_resizable")

            embed_wdg.add_behavior(load_height_bvr)
            embed_wdg.add_behavior(unload_height_bvr)

        else:
            thumb_table = DivWdg()
            td.add(thumb_table)
            
            thumb_table.add_behavior( {
                'type': 'click_up',
                'src': src,
                'cbjs_action': '''
                window.open(bvr.src);
                '''
            } )
            thumb_table.add_class("hand")
            thumb_table.add_style("width: 200px")
            thumb_table.add_style("height: 125px")
            thumb_table.add_style("padding: 5px")
            thumb_table.add_style("margin-left: 20px")
            thumb_table.add_style("display: inline-block")
            thumb_table.add_style("vertical-align: top")
            thumb_table.add_style("overflow-y: hidden")    
            from tactic.ui.panel import ThumbWdg2
            thumb = ThumbWdg2()
            thumb_table.add(thumb)
            thumb.set_sobject(snapshot)


        table.add_row()
        td = table.add_cell()


        from tactic.ui.checkin import PathMetadataWdg
        from tactic.ui.checkin import SnapshotMetadataWdg


        metadata_div = DivWdg()
        td.add(metadata_div)
        metadata_div.add_style("max-height: 400px")
        metadata_div.add_style("overflow-y: auto")
        metadata_div.add_style("overflow-x: hidden")
        metadata_div.add_style("margin: 20px 0px 20px 10px")
        metadata_div.add_style("text-align: left")

        metadata_div.add("<div style='font-size: 16px'>File Metadata</div>")
        metadata_div.add("<div>Metadata extracted directly from the file</div>")
        metadata_div.add("<hr/>")

        parser = my.kwargs.get("parser")
        use_tactic_tags = my.kwargs.get("use_tactic_tags")

        server_src = lib_path

        # get it dynamically by path
        metadata_wdg = PathMetadataWdg(path=server_src, parser=parser, use_tactic_tags=use_tactic_tags)
        metadata_div.add(metadata_wdg)

        #else:
        #    metadata_wdg = SnapshotMetadataWdg(snapshot=snapshot)
        #    metadata_div.add(metadata_wdg)


        top.add("<br/>")

        return top


