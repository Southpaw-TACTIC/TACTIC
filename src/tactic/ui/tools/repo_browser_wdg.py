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

__all__ = ['RepoBrowserWdg', 'RepoBrowserDirListWdg','RepoBrowserDirContentWdg']

from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment

from pyasm.web import DivWdg, WebContainer, Table
from pyasm.biz import Snapshot, Project
from pyasm.search import Search, SearchType, SearchKey
from pyasm.widget import IconWdg

from tactic.ui.panel import FastTableLayoutWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ResizableTableWdg
from tactic.ui.widget import DirListWdg


class RepoBrowserWdg(BaseRefreshWdg):


    def get_files(my):

        sobjects = my.sobjects
        if not my.sobjects:

            search_key = my.kwargs.get("search_key")
            if search_key:
                sobject = Search.get_by_search_key(search_key)
                my.sobjects = [sobject]
                search_type = sobject.get_search_type()
                parent_ids = [x.get_id() for x in sobjects]
            else:
                search_type = my.kwargs.get("search_type")
                project_code = Project.get_project_code()
                search_type = "%s?project=%s" % (search_type, project_code)

                my.sobjects = []
                parent_ids = []


        else:
            search_type = sobjects[0].get_search_type()
            parent_ids = [x.get_id() for x in sobjects]


        keywords = my.kwargs.get("keywords")


        search = Search("sthpw/file")
        search.add_filter("search_type", search_type)
        if parent_ids:
            search.add_filters("search_id", parent_ids)
        if keywords:
            search.add_text_search_filter("metadata_search", keywords)
        file_objects = search.get_sobjects()

        paths = []
        base_dir = Environment.get_asset_dir()
        for file_object in file_objects:
            relative_dir = file_object.get_value("relative_dir")
            file_name = file_object.get_value("file_name")

            repo_type = file_object.get_value("repo_type")
            if repo_type == 'perforce':
                print "PERFORCE: ", file_object.get_code(), file_name
                #continue

            path = "%s/%s/%s" % (base_dir, relative_dir, file_name)
            paths.append(path)

        return paths



    def get_display(my):

        search_type = my.kwargs.get("search_type")
        keywords = my.kwargs.get("keywords")

        top = my.top
        top.add_color("background", "background")
        top.add_class("spt_repo_browser_top")


        title_wdg = DivWdg()
        top.add(title_wdg)
        title_wdg.add_border()
        title_wdg.add_style("padding: 10px")
        title_wdg.add_gradient("background", "background", -10)
        title_wdg.add("Repository Browser")
        title_wdg.add_style("font-size: 14px")
        title_wdg.add_style("font-weight: bold")

        #table = ResizableTableWdg()
        table = Table()
        top.add(table)
        table.add_color("color", "color")


        base_dir = Environment.get_asset_dir()


        table.add_row()

        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add_border()
        left_inner = DivWdg()
        left.add(left_inner)
        left_inner.add_style("padding: 10px")
        left_inner.add_style("width: 400px")
        #left_inner.add_style("max-height: 600px")
        left_inner.add_style("min-height: 300px")
        left_inner.add_style("min-height: 300px")
        left_inner.add_style("min-width: 300px")
        left_inner.add_class("spt_resizable")
        left_inner.add_class("spt_repo_browser_list")
        left_inner.add_style("overflow-x: scroll")
        left_inner.add_style("overflow-y: auto")

        left_wdg = DivWdg()
        left_inner.add(left_wdg)
        left_wdg.add_style("width: 1000px")


        custom_cbk = {
        'enter': '''
            var top = bvr.src_el.getParent(".spt_repo_browser_top");
            var search_el = top.getElement(".spt_main_search");
            var keywords = search_el.value;

            var class_name = 'tactic.ui.tools.RepoBrowserWdg';
            var kwargs = {
                'search_type': '%s',
                'keywords': keywords,
            }
            content = top.getElement(".spt_repo_browser_content")
            spt.panel.load(top, class_name, kwargs);
        ''' % search_type
        }

        search_div = DivWdg()
        left_wdg.add(search_div)
        search_div.add("<b>File Filter: </b>")
        search_div.add("&nbsp;"*2)
        from tactic.ui.input import LookAheadTextInputWdg
        text = LookAheadTextInputWdg(search_type='sthpw/file',column='metadata_search', custom_cbk=custom_cbk)
        text.add_class("spt_main_search")
        text.add_style("width: 300px")
        if keywords:
            text.set_value(keywords)
        search_div.add(text)
        search_div.add("<hr/")

        paths = my.get_files()

        stats_div = DivWdg()
        left_wdg.add(stats_div)
        stats_div.add_style("font-size: 10px")
        stats_div.add_style("font-style: italic")
        stats_div.add_style("opacity: 0.5")
        stats_div.add("Found: %s file/s" % len(paths) )
        stats_div.add_style("margin-bottom: 5px")



        content_div = DivWdg()
        content_div.add_style("min-width: 400px")
        left_wdg.add(content_div)

        search_type = my.kwargs.get("search_type")
        dir_list = RepoBrowserDirListWdg(base_dir=base_dir, location="server", show_base_dir=True,paths=paths, all_open=True, search_type=search_type)
        content_div.add(dir_list)



        content = table.add_cell()
        content.add_style("vertical-align: top")
        content.add_border()
        content.add_style("padding: 10px")
        content.add_style("width: 600px")
        content.add_class("spt_repo_browser_content")

        content_div = DivWdg()
        content_div.add_style("min-width: 400px")
        content.add(content_div)


        table.add_row()
        bottom = table.add_cell()
        bottom.add_attr("colspan", "3")
        info_div = DivWdg()
        bottom.add(info_div)
        bottom.add_border()

        #info_div.add_style("height: 100px")

        return top


class RepoBrowserDirListWdg(DirListWdg):

    def add_file_behaviors(my, item_div, dirname, basename):
        search_type = my.kwargs.get("search_type")

        item_div.add_behavior( {
        'type': 'click_up',
        'dirname': dirname,
        'basename': basename,
        'search_type': search_type,
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_repo_browser_top");
        var content = top.getElement(".spt_repo_browser_content");
        var class_name = "tactic.ui.tools.repo_browser_wdg.RepoBrowserContentWdg";
        spt.app_busy.show("Loading information");
        var kwargs = {
          search_type: bvr.search_type,
          dirname: bvr.dirname,
          basename: bvr.basename
        };
        spt.panel.load(content, class_name, kwargs);
        spt.app_busy.hide();
        '''
        } )


    def add_dir_behaviors(my, item_div, dirname, basename):

        search_type = my.kwargs.get("search_type")

        item_div.add_behavior( {
        'type': 'click_up',
        'dirname': dirname,
        'basename': basename,
        'search_type': search_type,
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_repo_browser_top");
        var content = top.getElement(".spt_repo_browser_content");
        var class_name = "tactic.ui.tools.RepoBrowserDirContentWdg";
        spt.app_busy.show("Loading information");
        var kwargs = {
            search_type: bvr.search_type,
            view: 'table',
            dirname: bvr.dirname,
            basename: bvr.basename
        };
        spt.panel.load(content, class_name, kwargs);
        spt.app_busy.hide();

        '''
        } )




    def get_file_icon(my, dir, item):
        import os
        path = "%s/%s" % (dir, item)
        if not os.path.exists(path):
            return IconWdg.ERROR
        return IconWdg.DETAILS

    def get_dir_icon(my, dir, item):
        return IconWdg.LOAD



class RepoBrowserContentWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        search_type = my.kwargs.get("search_type")
        project_code = Project.get_project_code()
        #search_type = "%s?project=%s" % (search_type, project_code)
        search_type = Project.get_full_search_type(search_type, project_code=project_code)

        dirname = my.kwargs.get("dirname")
        basename = my.kwargs.get("basename")
        path = "%s/%s" % (dirname, basename)

        asset_dir = Environment.get_asset_dir()
        if not dirname.startswith(asset_dir):
            top.add("Error: path [%s] does not belong in the asset directory [%s]" % (path, asset_dir))
            return top

        reldir = dirname.replace(asset_dir, "")
        reldir = reldir.strip("/")

        search = Search("sthpw/file")
        search.add_filter("search_type", search_type)
        search.add_filter("relative_dir", reldir)
        search.add_filter("file_name", basename)
        files = search.get_sobjects()

        good_file = None
        for file in files:
            sobject_div = DivWdg()
            top.add(sobject_div)

            snapshot = file.get_parent()
            if not snapshot:
                parent = None
                print "Dangling file [%s]" % file.get_code()
            else:
                parent = snapshot.get_parent()
                if not parent:
                    print "Dangling snapshot [%s]" % snapshot.get_code()
                else:
                    good_file = file


        path_div = DivWdg()
        top.add(path_div)
        path_div.add("<b>Path:</b> %s" % path)
        path_div.add_color("color", "color")
        path_div.add_color("background", "background", -5)
        path_div.add_style("padding: 15px")
        path_div.add_style("margin-bottom: 15px")
        path_div.add_border()

        # display the info
        """
        layout = FastTableLayoutWdg(
            search_type=parent.get_search_type(),
            view='table',
            element_names=['small_preview','name','description'],
            show_shelf=False,
            show_select=False,
            show_header=False
        )
        layout.set_sobjects([parent])
        top.add(layout)
        """

        if good_file:
            top.add( my.get_content_wdg(good_file, snapshot, parent) )

        return top


    def get_content_wdg(my, file, snapshot, parent):

        div = DivWdg()

        config = []
        config.append('''<config><tab>''')
        config.append('''
        <element name='file_info' title='File Info'>
            <display class='tactic.ui.tools.file_detail_wdg.FileDetailWdg'>
                <search_key>%s</search_key>
            </display>
        </element>
        ''' % file.get_search_key()
        )

        process = snapshot.get_value("process")

        config.append('''
        <element name='notes' title='Notes'>
            <display class='tactic.ui.widget.DiscussionWdg'>
                <search_key>%s</search_key>
                <process>%s</process>
                <context_hidden>true</context_hidden>
                <show_note_expand>false</show_note_expand>
                <note_format>full</note_format>
                <show_expand>true</show_expand>
                <num_start_open>3</num_start_open>

            </display>
        </element>
        ''' % (parent.get_search_key(), process)
        )
 


        config.append('''
        <element name='sobject_detail' title='Full Item Detail'>
            <display class='tactic.ui.tools.SObjectDetailWdg'>
                <search_key>%s</search_key>
            </display>
        </element>
        ''' % parent.get_search_key()
        )
 
        config.append('''</tab></config>''')
        config = "\n".join(config)
        config = config.replace("&", "&amp;")


        from pyasm.web import WidgetSettings
        selected = WidgetSettings.get_value_by_key("repo_browser_selected")

        # remember last tab
        #selected = "notes"
        selected = None

        from tactic.ui.container import TabWdg
        tab = TabWdg(config_xml=config, selected=selected, show_remove=False, show_add=False)
        div.add(tab)





        return div




class RepoBrowserDirContentWdg(BaseRefreshWdg):

    def get_display(my):
        search_type = my.kwargs.get("search_type")
        project_code = Project.get_project_code()

        search_type = Project.get_full_search_type(search_type, project_code=project_code)
        #search_type = "%s?project=%s" % (search_type, project_code)

        dirname = my.kwargs.get("dirname")
        basename = my.kwargs.get("basename")
        path = "%s/%s" % (dirname, basename)

        asset_dir = Environment.get_asset_dir()
        if not dirname.startswith(asset_dir):
            top.add("Error: path [%s] does not belong in the asset directory [%s]" % (path, asset_dir))
            return top

        reldir = path.replace(asset_dir, "")
        reldir = reldir.strip("/")


        search = Search("sthpw/file")
        search.add_filter("relative_dir", "%s%%" % reldir, op='like')
        search.add_filter("search_type", search_type)
        print search.get_statement()

        search2 = Search(search_type)
        search2.add_relationship_search_filter(search)
        sobjects = search2.get_sobjects()

        from tactic.ui.panel import ViewPanelWdg
        layout = ViewPanelWdg(
                search_type=search_type,
                view="table",
                element_names=['preview','code','name','description','history','file_list'],
                show_shelf=False

        )
        layout.set_sobjects(sobjects)


        top = my.top
        top.add(layout)

        return top



