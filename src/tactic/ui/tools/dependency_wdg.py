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
__all__ = ["DependencyWdg", "SnapshotDirListWdg", "SnapshotDirListWdg2"]

from pyasm.common import Environment
from pyasm.biz import Snapshot
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table
from pyasm.widget import IconWdg
from pyasm.search import Search

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import DirListWdg

from pipeline_canvas_wdg import *
from pipeline_wdg import *



class SnapshotDirListWdg(DirListWdg):
    def get_display(my):

        top = my.top
        top.add_color("background", "background")
        top.add_style("padding: 10px")
        top.add_style("width: 500px")
        top.add_style("height: 300px")

        dir_list = SnapshotDirListWdg2(**my.kwargs)
        top.add(dir_list)

        return top





class SnapshotDirListWdg2(DirListWdg):
    def add_file_behaviors(my, item_div, dirname, basename):
        """
        item_div.add_behavior( {
        'type': 'click_up',
        'dirname': dirname,
        'basename': basename,
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_repo_browser_top");
        var content = top.getElement(".spt_repo_browser_content");
        var class_name = "tactic.ui.tools.repo_browser_wdg.RepoBrowserContentWdg";
        var kwargs = {
          dirname: bvr.dirname,
          basename: bvr.basename
        };
        spt.panel.load(content, class_name, kwargs);
        '''
        } )
        """

        # convert this to a repo directory
        asset_dir = Environment.get_asset_dir()


        # FIXME: not sure how general this
        webdirname = "/assets/%s" % dirname.replace(asset_dir, "")

        item_div.add_behavior( {
        'type': 'click_up',
        'webdirname': webdirname,
        'basename': basename,
        'cbjs_action': '''
        window.open(bvr.webdirname + "/" + bvr.basename, '_blank');
        '''
        } )




    def get_file_icon(my, dir, item):
        return IconWdg.DETAILS

    def get_dir_icon(my, dir, item):
        return IconWdg.LOAD






class DependencyWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        }

    def get_display(my):
        top = my.top

        search = Search("sthpw/snapshot")
        search.add_order_by("timestamp desc")
        search.add_filter("code", "61239PG")
        snapshot = search.get_sobject()

        xml = snapshot.get_value("snapshot")
        files = snapshot.get_all_file_objects()

        ref_snapshots = snapshot.get_all_ref_snapshots()


        table = Table()
        top.add(table)
        table.add_row()

        td = table.add_cell()
        canvas = my.get_canvas()
        td.add(canvas)

        table.add_row()
        td = table.add_cell()

        from tactic.ui.panel import TableLayoutWdg
        file_table = TableLayoutWdg(search_type="sthpw/file", view='table')
        td.add(file_table)
        table.set_sobjects(files)

        xml = []
        xml.append("<dependency>")
        for file in files:
            file_name = file.get_value("file_name")
            xml.append('''<node name="%s"/>''' % file_name)

        xml.append('''<node name="%s"/>''' % snapshot.get_code())
        for ref_snapshot in ref_snapshots:
            code = ref_snapshot.get_code()
            xml.append('''<node name="%s"/>''' % code)
            xml.append('''<connect from="%s" to="%s"/>''' % (code, snapshot.get_code() ))


        

        xml.append("</dependency>")

        xml = "\n".join(xml)



        div = DivWdg()
        top.add(div)
        div.add_behavior( {
        'type': 'load',
        'xml': xml,
        'cbjs_action': '''
        var group = 'dependency';
        var color = '#336655';
        spt.pipeline.import_xml(bvr.xml, group, color);
        '''
        } )


        return top



    def get_canvas(my):
        my.dialog_id = 1234
        my.height = my.kwargs.get("height")
        if not my.height:
            my.height = 300
        my.width = my.kwargs.get("width")
        return DependencyToolCanvasWdg(height=my.height, width=my.width, dialog_id=my.dialog_id, nob_mode="dynamic", line_mode='line', has_prefix=True)




class DependencyToolCanvasWdg(PipelineToolCanvasWdg):

    def get_node_behaviors(my):
        return []

    def get_canvas_behaviors(my):
        return []




