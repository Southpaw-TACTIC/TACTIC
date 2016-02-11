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

__all__ = ['RepoBrowserWdg', 'RepoBrowserDirListWdg','RepoBrowserContentWdg', 'RepoBrowserCbk', 'RepoBrowserDirContentWdg', 'RepoBrowserActionCmd']

from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment, Xml

from pyasm.web import DivWdg, WebContainer, Table, WidgetSettings
from pyasm.biz import Snapshot, Project, File
from pyasm.search import Search, SearchType, SearchKey, FileUndo
from pyasm.widget import IconWdg, CheckboxWdg
from pyasm.command import Command

from tactic.ui.panel import FastTableLayoutWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ResizableTableWdg
from tactic.ui.widget import DirListWdg, IconButtonWdg, ButtonNewWdg, ButtonRowWdg, ActionButtonWdg
from tactic.ui.container import Menu, MenuItem, SmartMenu, DialogWdg

import os, shutil, re


class RepoBrowserWdg(BaseRefreshWdg):


    def get_display(my):

        search_type = my.kwargs.get("search_type")
        keywords = my.kwargs.get("keywords")

        top = my.top
        top.add_color("background", "background")
        top.add_class("spt_repo_browser_top")
        my.set_as_panel(top)

        my.mode = 'main'
        #my.mode = 'all'
        #my.mode = 'folder'


        #table = ResizableTableWdg()
        table = Table()
        top.add(table)
        table.add_color("color", "color")
        #table.add_style("margin: -1px -1px -1px -1px")
        table.add_style("width: 100%")

        base_dir = Environment.get_asset_dir()
        project_code = Project.get_project_code()
        project_dir = "%s/%s" % (base_dir, project_code)

        table.add_row()

        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add_style("width: 1px")
        left.add_border(size="0px 1px 0px 0px", color="table_border")

        shelf_wdg = DivWdg()
        left.add(shelf_wdg)

        # TODO: this doesn't work very well. Disabling for now until a
        # better solution can be found.
        """
        custom_cbk = {
        'enter': '''
            var top = bvr.src_el.getParent(".spt_repo_browser_top");
            var search_el = top.getElement(".spt_main_search");
            var keywords = search_el.value;

            var class_name = 'tactic.ui.tools.RepoBrowserWdg';
            var kwargs = {
                'keywords': keywords,
            }
            content = top.getElement(".spt_repo_browser_content")
            spt.panel.load(top, class_name, kwargs);
        '''
        }

        search_div = DivWdg()
        shelf_wdg.add(search_div)
        search_div.add("<b>File Filter: </b>")
        search_div.add("&nbsp;"*2)
        from tactic.ui.input import LookAheadTextInputWdg
        text = LookAheadTextInputWdg(search_type='sthpw/file',column='metadata_search', custom_cbk=custom_cbk)
        text.add_class("spt_main_search")
        text.add_style("width: 250px")
        if keywords:
            text.set_value(keywords)
        search_div.add(text)
        search_div.add("<hr/")
        """


        if not search_type:
            shelf_wdg.add_style("padding: 10px")
            button_row = ButtonRowWdg()
            shelf_wdg.add(button_row)
            button_row.add_style("float: right")
            #button_row.add_style("margin-top: -10px")

            button = ButtonNewWdg(title="Refresh", icon=IconWdg.REFRESH)
            button_row.add( button )
            button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_repo_browser_top");
                spt.app_busy.show("Refreshing ...");
                spt.panel.refresh(top);
                spt.app_busy.hide();
                '''
            } )


            """
            button = ButtonNewWdg(title="Options", icon=IconWdg.GEAR, show_arrow=True)
            button_row.add( button )
            dialog = DialogWdg(show_title=False)
            dialog.add( my.get_options_wdg() )
            shelf_wdg.add( dialog )
            dialog.set_as_activator(button, offset={'x': -10, 'y': 10} )
            dialog.set_title(None)
            """


            button = ButtonNewWdg(title="Add", icon=IconWdg.ADD, show_arrow=True)
            button_row.add( button )
            menu = my.get_add_menu()
            menus = [menu.get_data()]
            SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'ADD_BUTTON_CTX': menus } )
            SmartMenu.assign_as_local_activator( button.get_button_wdg(), "ADD_BUTTON_CTX", True )







        stats_div = DivWdg()
        shelf_wdg.add(stats_div)
        stats_div.add_style("font-size: 10px")
        stats_div.add_style("font-style: italic")
        stats_div.add_style("opacity: 0.5")
        stats_div.add_style("margin-bottom: 5px")


        left_inner = DivWdg()
        left.add(left_inner)
        left_inner.add_style("width: 300px")
        left_inner.add_style("padding: 5px")
        #left_inner.add_style("max-height: 600px")
        left_inner.add_style("min-height: 500px")
        left_inner.add_style("max-height: 1000px")
        left_inner.add_style("min-width: 300px")
        left_inner.add_class("spt_resizable")
        left_inner.add_class("spt_repo_browser_list")
        left_inner.add_style("overflow-x: scroll")
        left_inner.add_style("overflow-y: auto")

        left_wdg = DivWdg()
        left_inner.add(left_wdg)
        left_wdg.add_style("width: 1000px")





        content_div = DivWdg()
        content_div.add_style("min-width: 400px")
        left_wdg.add(content_div)



        open_depth = my.kwargs.get("open_depth")
        if open_depth == None:
            open_depth = 0
        else:
            open_depth = int(open_depth)


        if search_type:
            search_types = [search_type]
        else:
            search_types = None


        parent_search = my.kwargs.get("search")
        if parent_search:
            parent_search.set_limit(1000)
            parent_search.set_offset(0)



        search_keys =  [x.get_search_key() for x in my.sobjects]
        dynamic = True


        dir_list = RepoBrowserDirListWdg(
                base_dir=project_dir,
                location="server",
                show_base_dir=True,
                open_depth=open_depth,
                search_types=search_types,
                dynamic=dynamic,
                keywords=keywords,
                search_keys=search_keys,
                search=parent_search
        )
        content_div.add(dir_list)

        top.add_attr("spt_search_keys", "|".join(search_keys) )



        content = table.add_cell()
        content.add_style("vertical-align: top")

        outer_div = DivWdg()
        content.add(outer_div)
        outer_div.add_class("spt_repo_browser_content")



        content_div = DivWdg()
        content_div.add_style("min-width: 400px")
        outer_div.add(content_div)

        count = parent_search.get_count()
        if count:
            widget = RepoBrowserDirContentWdg(
                search_type=search_type,
                view='table',
                dirname="%s/%s" % (project_dir, "asset"),
                basename="",
            )
            outer_div.add(widget)

        else:
            msg_div = DivWdg()
            msg_div.add("Search for content")
            outer_div.add(msg_div)
            msg_div.add_style("margin: 100px auto")
            msg_div.add_style("width: 250px")
            msg_div.add_style("padding: 50px")
            msg_div.add_style("font-size: 20px")
            msg_div.add_border()
            msg_div.add_style("text-align: center")
 

        table.add_row()
        bottom = table.add_cell()
        bottom.add_attr("colspan", "3")
        info_div = DivWdg()
        bottom.add(info_div)

        #info_div.add_style("height: 100px")

        return top


    def get_add_menu(my):


        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        from pyasm.biz import Project
        project = Project.get()
        search_types = project.get_search_types()


        for search_type_obj in search_types:
            title = search_type_obj.get_title()
            search_type = search_type_obj.get_value("search_type")

            display_title = "Add New %s" % title
            menu_item = MenuItem(type='action', label=display_title)
            menu.add(menu_item)
            
            menu_item.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'title': title,
                'cbjs_action': '''
                spt.tab.set_main_body_tab();
                //spt.tab.add_new(bvr.title, bvr.title, "tactic.ui.panel.table_layout_wdg.FastTableLayoutWdg", { search_type: bvr.search_type, view: "table" } );
                spt.panel.load_popup("Add New Item", "tactic.ui.panel.EditWdg", { search_type: bvr.search_type, single: 'false' } )
                '''
            } )


        if search_types:
            menu_item = MenuItem(type='separator')
            menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Add New sType')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var class_name = 'tactic.ui.app.SearchTypeCreatorWdg';
            spt.panel.load_popup("Create New sType", class_name);
            '''
        } )


        menu_item = MenuItem(type='action', label='Manage Schema')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.tools.SchemaToolWdg';
            spt.tab.add_new("Manage Schema", "Manage Schema", class_name);
            '''
        } )


        return menu








    def get_options_wdg(my):
        #show_files = True
        #show_latest_only = True
        #show_main_only = True
        #show_empty_folders = False
        #my.mode = ""

        div = DivWdg()
        div.add_class("spt_repo_browser_options")

        div.add_style("width: 200px")
        div.add_style("height: 200px")
        div.add_style("padding: 15px")
        div.add_border()
        div.set_box_shadow()
        div.add_color("background", "background3")

        checkbox = CheckboxWdg("show_files")
        div.add(checkbox)
        div.add("Show files")
        div.add("<br/>"*2)
        checkbox.add_behavior({"type": "click_up", "cbjs_action" : ""})

        checkbox = CheckboxWdg("show_latest_only")
        div.add(checkbox)
        div.add("Show only the last version")
        div.add("<br/>"*2)
        checkbox.add_behavior({"type": "click_up", "cbjs_action" : ""})

        checkbox = CheckboxWdg("show_main_only")
        div.add(checkbox)
        div.add("Show only the main files")
        div.add("<br/>"*2)
        checkbox.add_behavior({"type": "click_up", "cbjs_action" : ""})


        checkbox = CheckboxWdg("show_empty_folders")
        div.add(checkbox)
        div.add("Show empty folders")
        div.add("<br/>")
        checkbox.add_behavior({"type": "click_up", "cbjs_action" : ""})

        div.add("<br/>")

        button = ActionButtonWdg(title="Refresh")
        div.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_repo_browser_options");
            var values = spt.api.get_input_values(top, null, false);
            console.log(values);



            var top = bvr.src_el.getParent(".spt_repo_browser_top");
            spt.app_busy.show("Refreshing ...");
            spt.panel.refresh(top);
            spt.app_busy.hide();
            '''
        } )
        button.add_style("float: right")


        return div




class RepoBrowserDirListWdg(DirListWdg):

    def init(my):
        my.file_codes = {}
        my.snapshot_codes = {}
        my.search_types_dict = {}
        my.search_codes = {}
        my.search_types = my.kwargs.get("search_types")


        my.dynamic = my.kwargs.get("dynamic")
        if my.dynamic in ['true', True, 'True']:
            my.dynamic = True
        else:
            my.dynamic = False


        # find the sobjects
        search_keys = my.kwargs.get("search_keys")
        if search_keys:
            my.sobjects = Search.get_by_search_keys(search_keys)
        else:
            my.sobjects = []

        super(RepoBrowserDirListWdg, my).init()




    def get_file_search(my, base_dir, search_types, parent_ids, mode="count"):

        show_main_only = True
        show_latest = True
        show_versionless = False

        asset_base_dir = Environment.get_asset_dir()
        relative_dir = base_dir.replace(asset_base_dir, "")
        relative_dir = relative_dir.strip("/")

        keywords = my.kwargs.get("keywords")

        project_code = Project.get_project_code()
        search = Search("sthpw/file")
        if search_types:
            search.add_filters("search_type", search_types)

        if relative_dir:

            # TODO: not very clean.  There are different ways that the
            # relative dir needs to be searched on depending on usage
            # For now, just use a simple mode
            if mode == "count":
                search.add_op("begin")
                search.add_filter("relative_dir", "%s" % relative_dir)
                search.add_filter("relative_dir", "%s/%%" % relative_dir, op='like')
                search.add_op("or")
            else:
                search.add_op("begin")
                search.add_filter("relative_dir", "%s" % relative_dir)
                if not my.dynamic:
                    search.add_filter("relative_dir", "%s/%%" % relative_dir, op='like')
                search.add_op("or")


        if parent_ids:
            search.add_filters("search_id", parent_ids)
        if keywords:
            search.add_text_search_filter("metadata_search", keywords)

        if show_latest or show_versionless:
            search.add_join("sthpw/snapshot")
            search.add_op("begin")
            if show_latest:
                search.add_filter("is_latest", True, table="snapshot")
            if show_versionless:
                search.add_filter("version", -1, table="snapshot")
            search.add_filter("file_name", "")
            search.add_filter("file_name", "NULL", quoted=False, op="is")
            search.add_op("or")
        else:
            pass

        if show_main_only:
            search.add_filter("type", "main")


        if my.sobjects:
            search.add_sobjects_filter(my.sobjects)


        search_type = search_types[0]
        key = "repo_browser:%s" % search_type
        parent_search_str = WidgetSettings.get_value_by_key(key)
        if parent_search_str:
            parent_search = Search(search_type)
            parent_search.select.loads(parent_search_str)
            parents = parent_search.get_sobjects()
            parent_codes = [x.get_value("code") for x in parents]

            search.add_filters("search_code", parent_codes)

        return search




    def get_relative_paths(my, base_dir):

        # options to get files
        # show latest version only
        # show files
        # show all files types

        show_empty_folders = True
        show_no_sobject_folders = True


        my.show_files = True
        show_main_only = True
        show_latest = True
        show_versionless = False




        asset_base_dir = Environment.get_asset_dir()


        relative_dir = base_dir.replace(asset_base_dir, "")
        relative_dir = relative_dir.strip("/")

        keywords = my.kwargs.get("keywords")

        search_types = my.kwargs.get("search_types")
        sobjects = my.sobjects
        if not sobjects:

            search_key = my.kwargs.get("search_key")
            search_type = my.kwargs.get("search_type")

            if search_types:
                parent_ids = []
            elif search_key:
                sobject = Search.get_by_search_key(search_key)
                search_types = [sobject.get_search_type()]
                parent_ids = [x.get_id() for x in sobjects]

            elif search_type:
                search_types = [search_type]
                my.sobjects = []
                parent_ids = []


            # This attempts to display all search types, but it causes problems
            # because it is the default and if any of the above kwargs is
            # missing, it leads to misleading results.  Disabling for now
            #else:
            #    raise Exception("No search_key or search_type/s specified")
            else:
                search_types = []
                my.sobjects = []
                parent_ids = []


        else:
            search_types = [sobjects[0].get_search_type()]
            parent_ids = [x.get_id() for x in sobjects]
            my.sobjects = sobjects


        search_types = [SearchType.build_search_type(x) for x in search_types]


        search_type = search_types[0]
        key = "repo_browser:%s" % search_type
        parent_search_str = WidgetSettings.get_value_by_key(key)
        if parent_search_str:
            show_no_sobject_folders = False
            show_empty_folders = True


        paths = []
        my.file_codes = {}
        my.file_objects = {}
        my.snapshot_codes = {}
        my.search_types_dict = {}
        my.search_codes = {}

        # Note this shold be used sparingly because it can find lots of
        # sobjects
        if my.show_files:

            search = my.get_file_search(relative_dir, search_types, parent_ids, mode="folder")
            file_objects = search.get_sobjects()

            for file_object in file_objects:
                relative_dir = file_object.get_value("relative_dir")
                file_name = file_object.get_value("file_name")

                repo_type = file_object.get_value("repo_type")
                if repo_type == 'perforce':
                    print "PERFORCE: ", file_object.get_code(), file_name
                    #continue


                path = "%s/%s/%s" % (asset_base_dir, relative_dir, file_name)
                paths.append(path)

                my.file_codes[path] = file_object.get("code")
                my.snapshot_codes[path] = file_object.get("snapshot_code")
                my.file_objects[path] = file_object

                # store search codes per directory
                dirname = "%s/%s/" % (asset_base_dir, relative_dir)
                search_code = file_object.get("search_code")


                search_codes_list = my.search_codes.get(dirname)

                # only file objects with not file are recorded
                if not file_name:
                    if search_codes_list == None:
                        my.search_codes[dirname] = set([search_code])
                    else:
                        my.search_codes[dirname].add(search_code)


                search_type = file_object.get("search_type")
                my.search_types_dict[path] = search_type

                if not file_name:
                    #print search_type, relative_dir
                    continue

                # go up the path and set the search type
                parts = relative_dir.split("/")
                for i in range (0, len(parts)+1):
                    tmp_dir = "/".join(parts[:i])
                    tmp_dir = "%s/%s/" % (asset_base_dir, tmp_dir)
                    my.search_types_dict[tmp_dir] = search_type



        # find any folders that match
        """
        dirnames = os.listdir(base_dir)
        for dirname in dirnames:

            parts = dirname.strip().split("/")
            parts = [x.lower() for x in parts]
            parts.append(dirname)
            parts = set(parts)

            for root, subdirnames, subbasenames in os.walk("%s/%s" % (base_dir, dirname)):
                for subdirname in subdirnames:
                    parts.add(subdirname.lower())

            keywords = my.kwargs.get("keywords") or []

            subdir = "%s/%s" % (base_dir, dirname)

            for keyword in keywords:
                if keyword.lower() in parts:
                    paths.append("%s/" % subdir)
        """
            
    

        # add dirnames if they have sobject files in them
        #if not show_no_sobject_folders:
        my.counts = {}
        print "base_dir: ", base_dir
        if True:
            dirnames = os.listdir(base_dir)
            for dirname in dirnames:
                subdir = "%s/%s" % (base_dir, dirname)
                if not os.path.isdir(subdir):
                    continue

                search = my.get_file_search(subdir, search_types, parent_ids, mode="count")
                count = search.get_count()
                my.counts[subdir] = count
                if count:
                    full = "%s/" % subdir
                    # FIXME: this actually allows for the click-up behavior
                    # however, it only currently works for a single stype
                    my.search_types_dict[full] = search_types[0]
                    paths.append(full)
                else:
                    full = "%s/" % subdir
                    paths.append(full)


            #return paths

        return paths


        # FIXME: is the rest here even needed?


        project_code = Project.get_project_code()


        num_sobjects = {}

        # show all folders, except in the case of the base folder of the project
        project_code = Project.get_project_code()
        project_base_dir = "%s/%s" % (asset_base_dir, project_code)
        if os.path.isdir(base_dir) and base_dir != project_base_dir:
            dirnames = os.listdir(base_dir)
            if show_empty_folders or len(dirnames) > 0:

                for dirname in dirnames:
                    full = "%s/%s" % (base_dir, dirname)
                    if not os.path.isdir(full):
                        continue

                    paths.append("%s/" % full)

        # only look at folders associated with search types given
        for search_type in search_types:
            #search = Search(search_type)
            #count = search.get_count()
            #if not count:
            #    continue

            search_type_obj = SearchType.get(search_type)

            parts = search_type_obj.get_base_key().split("/")
            if len(parts) == 2:
                table = parts[1]
            else:
                table = parts[0]



            # TODO: this is tenuous
            project_code = Project.get_project_code()
            start_dir = "%s/%s/%s" % (asset_base_dir, project_code, table)
            full = "%s/" % start_dir
            paths.append(full)



            search_type = search_type_obj.get_value("search_type")
            search_type = "%s?project=%s" % (search_type, project_code)
            my.search_types_dict[full] = search_type

            if not os.path.exists(start_dir):
                continue

            # handle the dynamic case and make sure that the paths
            # are in this search_type's directory
            if my.dynamic:
                if base_dir.startswith(start_dir):

                    if not os.path.exists(base_dir):
                        continue
                    dirnames = os.listdir(base_dir)
                    for dirname in dirnames:
                        full = "%s/%s/" % (base_dir, dirname)
                        if not os.path.isdir(full):
                            continue

                        search_codes_list = my.search_codes.get(full)
                        if not search_codes_list:
                            num_sobjects[full] = 0
                        else:
                            num_sobjects[full] = len(search_codes_list)

                        my.search_types_dict[full] = search_type

                        if show_empty_folders:
                            paths.append(full)
                continue



            if not start_dir.startswith(base_dir):
                continue


            # This walks up the folder structure and sets search codes

            for root, dirnames, filenames in os.walk(start_dir):

                for dirname in dirnames:
                    full = "%s/%s/" % (root, dirname)

                    search_codes_list = my.search_codes.get(full)
                    if not search_codes_list:
                        num_sobjects[full] = 0
                    else:
                        num_sobjects[full] = len(search_codes_list)

                    my.search_types_dict[full] = search_type

                    if show_empty_folders:
                        paths.append(full)


        #for path in paths:
        #    print "path: ", path
        #print "---"
        #for name, value in num_sobjects.items():
        #    print value, name


        return paths





    def add_top_behaviors(my, top):

        search = my.kwargs.get("search")
        if search:
            key = "repo_browser:%s" % search.get_search_type()
            dump = search.select.dumps()
            WidgetSettings.set_value_by_key(key, dump)



        border = top.get_color("shadow")

        top.add_behavior( {
        'type': 'load',
        'border': border,
        'cbjs_action': '''

        spt.repo_browser = {};
        spt.repo_browser.start_y = null;
        spt.repo_browser.start_pos = null;

        spt.repo_browser.drag_file_setup = function(evt, bvr, mouse_411) {
            spt.repo_browser.start_y = mouse_411.curr_y
            spt.repo_browser.start_pos = bvr.src_el.getPosition();
        }
        spt.repo_browser.drag_file_motion = function(evt, bvr, mouse_411) {
            var diff_y = mouse_411.curr_y - spt.repo_browser.start_y;
            if (diff_y < 3 && diff_y > -3) {
                return;
            }

            bvr.src_el.setStyle("border", "solid 1px " + bvr.border);
            bvr.src_el.setStyle("box-shadow", "0px 0px 5px");
            bvr.src_el.setStyle("position", "absolute");
            bvr.src_el.setStyle("padding", "5px");
            bvr.src_el.position({x:mouse_411.curr_x+5, y:mouse_411.curr_y+5});
        }
        spt.repo_browser.drag_file_action = function(evt, bvr, mouse_411) {

            //bvr.src_el.position(spt.repo_browser.start_pos);

            var diff_y = mouse_411.curr_y - spt.repo_browser.start_y;
            if (diff_y < 3 && diff_y > -3) {
                return;
            }

            bvr.src_el.setStyle("border", "");
            bvr.src_el.setStyle("box-shadow", "");
            bvr.src_el.setStyle("position", "relative");
            bvr.src_el.setStyle("padding", "2px 0px 2px 15px");

            var pos = spt.repo_browser.start_pos;
            new Fx.Tween(bvr.src_el,{duration:"short"}).start('top', pos.y);
            new Fx.Tween(bvr.src_el,{duration:"short"}).start('left', pos.x);
            bvr.src_el.setStyle("position", "");

            var drop_on_el = spt.get_event_target(evt);

            if (!drop_on_el.hasClass("spt_dir_item")) {
                drop_on_el = drop_on_el.getParent(".spt_dir_item");
            }

            if (! drop_on_el) {
                return;
            }


            var server = TacticServerStub.get(); 

            var snapshot_code = bvr.src_el.getAttribute("spt_snapshot_code");
            // or get the diranme
            var from_relative_dir = bvr.src_el.getAttribute("spt_relative_dir");


            // get the new relative_dir
            var relative_dir = drop_on_el.getAttribute("spt_relative_dir");


            if ( drop_on_el.hasClass("spt_open") == true) {
                var sibling = drop_on_el.getNext();
                var inner = sibling.getElement(".spt_dir_list_handler_content");
                bvr.src_el.inject(inner, 'top');
                var padding = drop_on_el.getStyle("padding-left");

                //padding = parseInt(padding.replace("px", ""));
                //padding += 25;
                if (bvr.src_el.hasClass("spt_dir") ) {
                    bvr.src_el.setStyle("padding-left", "");
                }
                else {
                    bvr.src_el.setStyle("padding-left", "15px");
                }
            }
            else {
                spt.behavior.destroy_element(bvr.src_el);
            }

            var cmd = 'tactic.ui.tools.RepoBrowserCbk';
            var kwargs = {
                snapshot_code: snapshot_code,
                from_relative_dir: from_relative_dir,
                relative_dir: relative_dir
            }
            server.execute_cmd(cmd, kwargs); 

        }


        spt.repo_browser.select = function(file_item) {
            console.log("select")
            file_item.setStyle("background", "#CCC");
            file_item.setStyle("box-shadow", "0px 0px 5px rgba(0,0,0,0.5)");
            file_item.setStyle("border-radius", "3px");
            file_item.addClass("spt_selected")
        }
        spt.repo_browser.unselect = function(file_item) {
            file_item.setStyle("box-shadow", "");
            file_item.setStyle("border-radius", "");
            file_item.setStyle("background", "");
            file_item.removeClass("spt_selected")
        }
        spt.repo_browser.toggle_select = function(file_item) {
            if (file_item.hasClass("spt_selected")) {
                spt.repo_browser.unselect(file_item);
            }
            else {
                spt.repo_browser.select(file_item);
            }

        }
        spt.repo_browser.clear_selected = function() {
            var selected = spt.repo_browser.get_selected();
            for (var i = 0; i < selected.length; i++) {
                spt.repo_browser.unselect(selected[i]);
            }
        }

        spt.repo_browser.get_selected = function() {
            var selected = $(document.body).getElements(".spt_selected");
            return selected;
        }


        spt.repo_browser.click_file_bvr = function(evt, bvr) {
            if (!evt.control) {
                spt.repo_browser.clear_selected();
            }

            spt.repo_browser.toggle_select(bvr.src_el);
            var selected = spt.repo_browser.get_selected();
            //var selected = [];

            var top = bvr.src_el.getParent(".spt_repo_browser_top");
            var content = top.getElement(".spt_repo_browser_content");
            spt.table.last_table = null;

            spt.app_busy.show("Loading information");

            if (selected.length > 1) {
                var snapshot_codes = [];
                for (var i = 0; i < selected.length; i++) {
                    snapshot_codes.push( selected[i].getAttribute("spt_snapshot_code"));
                }
                var class_name = "tactic.ui.tools.RepoBrowserDirContentWdg";
                var kwargs = {
                  search_type: bvr.search_type,
                  snapshot_codes: snapshot_codes
                };

            }
            else {
                var class_name = "tactic.ui.tools.RepoBrowserContentWdg";

                var dirname = bvr.src_el.getAttribute("spt_dirname");
                var basename = bvr.src_el.getAttribute("spt_basename");

                var kwargs = {
                  search_type: bvr.search_type,
                  dirname: dirname,
                  basename: basename
                };
            }

            spt.panel.load(content, class_name, kwargs);
            spt.app_busy.hide();
        }


        spt.repo_browser.drag_enter = function(event, el) {
        }

        spt.repo_browser.drag_leave = function(event, el) {
            console.log("leave");
        }

        spt.repo_browser.drag_drop = function(evt, bvr) {
            console.log(evt);
            console.log(bvr);
            var top = bvr.src_el.getParent(".spt_tile_top");
            var search_key = top.getAttribute("spt_search_key");

            var target = $(evt.target);
            if (!target.hasClass("spt_dir")) {
                target = target.getParent(".spt_dir");
            }
            var relative_dir = target.getAttribute("spt_relative_dir");



            var server = TacticServerStub.get(); 
            var cmd = 'tactic.ui.tools.RepoBrowserCbk';
            var kwargs = {
                search_key: search_key,
                relative_dir: relative_dir
            }
            server.execute_cmd(cmd, kwargs); 

            spt.behavior.destroy_element(top);

            var dir_top = target.getParent(".spt_dir_list_handler_top");
            spt.panel.refresh(dir_top);

        }


        '''
        } )


        """
        top.add_behavior( {
            'type': 'smart_drag',
            "drag_el": '@',
            'bvr_match_class': 'spt_drag_file_item',
            'cbjs_setup': 'spt.repo_browser.drag_file_setup(evt, bvr, mouse_411)',
            'cbjs_motion': 'spt.repo_browser.drag_file_motion(evt, bvr, mouse_411)',
            'cbjs_action': 'spt.repo_browser.drag_file_action(evt, bvr, mouse_411)',
        } )
        """

        # add in a context menu
        freeform_menu = my.get_dir_context_menu()
        strict_menu = my.get_dir_context_menu(mode="strict")
        file_menu = my.get_file_context_menu()

        menus_in = {
            'FREEFORM_DIR_ITEM_CTX': freeform_menu,
            'STRICT_DIR_ITEM_CTX': strict_menu,
            'FILE_ITEM_CTX': file_menu,
        }
        SmartMenu.attach_smart_context_menu( top, menus_in, False )



        # add in template UIs
        template_div = DivWdg()
        #top.add(template_div)
        
        new_folder_div = DivWdg()
        template_div.add(new_folder_div)
        arrow = "/context/icons/silk/_spt_bullet_arrow_down_dark.png";
        icon = "/context/icons/silk/folder.png";
        html = "";
        html += '<img src="'+arrow+'"/>';
        html += '<img src="'+icon+'"/>';
        html += '<input type="text" value="New Folder"/>';
        new_folder_div.add(html)

        

        # directory click up
        # FIXME: this does not work well with the swap display
        """
        top.add_relay_behavior( {
        'type': 'mouseup',
        'bvr_match_class': 'spt_dir_item',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_repo_browser_top");
        var content = top.getElement(".spt_repo_browser_content");
        var class_name = "tactic.ui.tools.RepoBrowserDirContentWdg";

        var dirname = bvr.src_el.getAttribute("spt_dirname");
        var basename = "";

        var search_type = null;
        var parent = bvr.src_el;
        while (search_type == null) {
            search_type = parent.getAttribute("spt_search_type");
            if (search_type) break;
            parent = parent.getParent();
            parent = parent.getPrevious();
            if (!parent) {
                break;
            }
        }
        if (search_type) {
            var search_codes = bvr.src_el.getAttribute("spt_search_codes");
            //alert(search_codes);
            search_codes = search_codes.split("|");

            spt.app_busy.show("Loading ...");
            var kwargs = {
                search_type: search_type,
                view: 'table',
                dirname: dirname,
                basename: basename
            };
            spt.panel.load(content, class_name, kwargs);
            spt.app_busy.hide();
        }

        '''
        } )
        """






    def get_dir_context_menu(my, mode="freeform"):

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        """
        menu_item = MenuItem(type='action', label='Add New Item')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': r'''
            var activator = spt.smenu.get_activator(bvr);
            var relative_dir = activator.getAttribute("spt_relative_dir");
            var search_type = activator.getAttribute("spt_search_type");

            var class_name = 'tactic.ui.panel.EditWdg';
            var kwargs = {
                relative_dir: relative_dir,
                search_type: search_type,
                mode: 'insert',
                single: 'true',
            };
            spt.panel.load_popup('Add New Item', 'tactic.ui.panel.EditWdg', kwargs);
            '''
        } )
        """

        """ 
        menu_item = MenuItem(type='action', label='Add Multiple Items')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': r'''
            var activator = spt.smenu.get_activator(bvr);
            var relative_dir = activator.getAttribute("spt_relative_dir");
            var search_type = activator.getAttribute("spt_search_type");

            var class_name = 'tactic.ui.panel.EditWdg';
            var kwargs = {
                relative_dir: relative_dir,
                search_type: search_type,
                mode: 'insert',
                single: 'false',
            };
            spt.panel.load_popup('Multi-Insert', 'tactic.ui.panel.EditWdg', kwargs);
            '''
        } )
        """

        """
        menu_item = MenuItem(type='action', label='Delete Item')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': r'''
            var activator = spt.smenu.get_activator(bvr);
            var search_type = activator.getAttribute("spt_search_type");
            var search_codes = activator.getAttribute("spt_search_codes");
            if (! search_codes ) {
                alert( "No SObject associated with this folder" );
                return;
            }

            search_codes = search_codes.split("|");
            if (search_codes.length > 1) {
                alert( "Too many sobjects associated with this folder");
                return;
            }

            var search_key = search_type + "&code=" + search_codes[0];

            var class_name = 'tactic.ui.tools.DeleteToolWdg';
            var kwargs = {
              search_key: search_key,
            }
            var popup = spt.panel.load_popup("Delete Item", class_name, kwargs);
            '''
        } )
        """


        if mode == "freeform":

            #menu_item = MenuItem(type='separator')
            #menu.add(menu_item)


            menu_item = MenuItem(type='action', label='New Folder')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'type': 'click_up',
                'cbjs_action': r'''
                var activator = spt.smenu.get_activator(bvr);
                var relative_dir = activator.getAttribute("spt_relative_dir");
                var search_type = activator.getAttribute("spt_search_type");

                var div = document.createElement("div");
                div = $(div);
                div.setStyle("margin-top: 3px")

                var arrow = "/context/icons/silk/_spt_bullet_arrow_down_dark.png";
                var icon = "/context/icons/silk/folder.png";
                var html = "";
                html += '<img src="'+arrow+'"/>';
                html += '<img src="'+icon+'"/>';
                html += '<input class="new_folder_input" type="text" value="New Folder"/>';
                div.innerHTML = html;

                var content = activator.getNext(".spt_dir_content");
                dyn_content = content.getElement(".spt_dir_list_handler_top");
                if (dyn_content) {
                    content = dyn_content;
                }
                var children = content.getElements(".spt_dir");
                if (content.childNodes.length)
                    div.inject(content.childNodes[0], "before");
                else
                    div.inject(content);

                var padding = activator.getStyle("padding-left");
                padding = parseInt( padding.replace("px", "") );
                div.setStyle("padding-left", padding);

                var input = div.getElement(".new_folder_input");
                input.onblur = function() {
                    var value = this.value;
                    if (!value) {
                        div.destroy();
                    }

                    var span = $(document.createElement("span"));
                    span.innerHTML = " " +value;
                    span.replaces(input);
                    span.addClass("spt_dir_value");

                    var new_relative_dir = relative_dir + "/" + value;
                    div.setAttribute("spt_relative_dir", new_relative_dir);
                    div.addClass("spt_dir_item");

                    var class_name = 'tactic.ui.tools.RepoBrowserActionCmd';
                    var kwargs = {
                        search_type: bvr.search_type,
                        action: 'create_folder',
                        relative_dir: new_relative_dir
                    }
                    var server = TacticServerStub.get();
                    server.execute_cmd(class_name, kwargs);

                    var dir_top = span.getParent(".spt_dir_list_handler_top");
                    spt.panel.refresh(dir_top);
                };
                input.onfocus = function() {
                    this.select();
                };
                input.addEvent( "keyup", function(evt) {
                    var key = evt.key;
                    if (key == 'enter') {
                        evt.stop();
                        this.blur();
                    }
                    else if (key == 'esc') {
                        div.destroy();
                    }
                } );

                input.select();

                '''
            } )


            menu_item = MenuItem(type='action', label='Rename Folder')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);
                var relative_dir = activator.getAttribute("spt_relative_dir");

                var input = $(document.createElement("input"));
                input.setAttribute("type", "text");
                input.setStyle("width", "200px");

                var div = activator;

                var el = activator.getElement(".spt_dir_value");
                input.replaces(el);

                var parts = relative_dir.split("/");
                input.value = parts[parts.length-1];
                var base_relative_dir = parts.slice(0, parts.length-1).join("/");
                input.onblur = function() {
                    var value = this.value;

                    if (!value) {
                        alert("no value");
                        return;
                    }

                    var span = $(document.createElement("span"));
                    span.innerHTML = " " +value;
                    span.replaces(input);
                    span.addClass("spt_dir_value");

                    var new_relative_dir = base_relative_dir + "/" + value;
                    div.setAttribute("spt_relative_dir", new_relative_dir);


                    var class_name = 'tactic.ui.tools.RepoBrowserActionCmd';
                    var kwargs = {
                        search_type: bvr.search_type,
                        action: 'rename_folder',
                        old_relative_dir: relative_dir,
                        new_relative_dir: new_relative_dir
                    }
                    var server = TacticServerStub.get();
                    server.execute_cmd(class_name, kwargs);

                    var dir_top = span.getParent(".spt_dir_list_handler_top");
                    spt.panel.refresh(dir_top);


                };

                '''
            } )

            menu_item = MenuItem(type='action', label='Delete Folder')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);
                var relative_dir = activator.getAttribute("spt_relative_dir");

                // This will only delete the folder if it is empty
                //if (!confirm("Delete folder ["+relative_dir+"]?")) {
                //    return;
                //}

                var server = TacticServerStub.get();

                var class_name = 'tactic.ui.tools.RepoBrowserActionCmd';
                var kwargs = {
                    search_type: bvr.search_type,
                    action: 'delete_folder',
                    relative_dir: relative_dir
                }
                try {
                    server.execute_cmd(class_name, kwargs);
                    activator.destroy();
                }
                catch(e) {
                    alert("Folder is not empty.  Please delete all items in folder first");
                }


                '''
            } )



        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        """
        menu_item = MenuItem(type='action', label='Download Files')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var search_type = activator.getAttribute("spt_search_type");
            var search_codes = activator.getAttribute("spt_search_codes");
            if (! search_codes ) {
                alert( "No SObject associated with this folder" );
                return;
            }

            search_codes = search_codes.split("|");
            if (search_codes.length > 1) {
                alert( "Too many sobjects associated with this folder");
                return;
            }

            var search_key = search_type + "&code=" + search_codes[0];
            var class_name = 'tactic.ui.widget.CheckinWdg';
            var kwargs = {
                search_key: search_key
            };
            spt.panel.load_popup("Check-in", class_name, kwargs);
            '''
        } )
        """




        menu_item = MenuItem(type='action', label='Ingest Files')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var search_type = activator.getAttribute("spt_search_type");

            var relative_dir = activator.getAttribute("spt_relative_dir");
            var class_name = 'tactic.ui.tools.IngestUploadWdg';
            var kwargs = {
                search_type: search_type,
                relative_dir: relative_dir
            };
            spt.panel.load_popup("Ingest <i style='opacity: 0.3'>("+search_type+")</i>", class_name, kwargs);
            '''
        } )


        menu_item = MenuItem(type='separator')
        #menu.add(menu_item)
        menu_item = MenuItem(type='action', label='Copy To Clipboard')
        #menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var relative_dir = activator.getAttribute("spt_relative_dir");

            var server = TacticServerStub.get();

            var class_name = 'tactic.ui.tools.RepoBrowserActionCmd';
            var kwargs = {
                search_type: bvr.search_type,
                action: 'copy_clipboard',
                relative_dir: relative_dir
            }

            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);


            '''
        } )



        menu_item = MenuItem(type='action', label='Check-out Files')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);

            var relative_dir = activator.getAttribute("spt_relative_dir");

            var server = TacticServerStub.get();
            var snapshots = server.get_snapshots_by_relative_dir(relative_dir);
            if (!snapshots.length) {
                alert("No files checked into this folder");
                return;
            }

            var snapshot_codes = []
            for (var i = 0; i < snapshots.length; i++) {
                snapshot_codes.push(snapshots[i].code);
            }

            var class_name = 'tactic.ui.tools.checkout_wdg.CheckoutWdg';
            var kwargs = {
                base_dir: relative_dir,
                snapshot_codes: snapshot_codes,
            }
            spt.panel.load_popup("Check-out", class_name, kwargs);

            return;
            '''
        } )



        return menu


    def get_file_context_menu(my):

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        """
        menu_item = MenuItem(type='action', label='Open Detail')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var snapshot = activator.getAttribute("spt_search_key");
            spt.tab.set_main_body_tab();
            var class_name = "tactic.ui.tools.SObjectDetailWdg";
            var kwargs = {
                
            }
            '''
        } )
        """





        menu_item = MenuItem(type='action', label='Rename Item')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var value = activator.getAttribute("spt_basename");
            var relative_dir = activator.getAttribute("spt_relative_dir");

            var input = $(document.createElement("input"));
            input.setAttribute("type", "text");

            var div = activator;

            var el = activator.getElement(".spt_item_value");
            input.replaces(el);
            input.setStyle("margin-top", "-1px");
            input.setStyle("width", "200px");

            input.value = value;
            input.focus();
            input.select();


            input.onblur = function() {
                var new_value = this.value;

                if (!new_value) {
                    alert("no value");
                    return;
                }


                var span = $(document.createElement("span"));
                span.innerHTML = " " + new_value;
                span.replaces(input);
                span.addClass("spt_item_value");

                div.setAttribute("spt_basename", new_value);

                var class_name = 'tactic.ui.tools.RepoBrowserActionCmd';
                var kwargs = {
                    search_type: bvr.search_type,
                    action: 'rename_item',
                    relative_dir: relative_dir,
                    old_value: value,
                    new_value: new_value
                }
                var server = TacticServerStub.get();
                server.execute_cmd(class_name, kwargs);

                var dir_top = span.getParent(".spt_dir_list_handler_top");
                spt.panel.refresh(dir_top);


            };

            input.onkeyup = function(evt) {
                console.log(evt.key);
            }

            '''
        } )



        menu_item = MenuItem(type='action', label='Delete Item')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var relative_dir = activator.getAttribute("spt_relative_dir");

            var snapshot_code = activator.getAttribute("spt_snapshot_code")

            var server = TacticServerStub.get();

            var class_name = 'tactic.ui.tools.RepoBrowserActionCmd';
            var kwargs = {
                action: 'delete_item',
                snapshot_code,
            }
            try {
                server.execute_cmd(class_name, kwargs);
                activator.destroy();
            }
            catch(e) {
                alert("Could not delete file.");
            }


            '''
        } )




        return menu




    def get_dirname(my, dirname, basename):

        path = "%s/%s" % (dirname, basename)
        counts = my.counts.get(path)
        if counts:
            return "%s <i style='display: inline-block; font-size: 9px; opacity: 0.8'>(%s)</i>" % (basename, counts)
        else:
            return "<span style='opacity: 0.3'>%s</span>" % (basename)





    def get_basename(my, dirname, basename):

        path = "%s/%s" % (dirname, basename)
        file_object = my.file_objects.get(path)

        #src_path = file_object.get_value("source_path")
        src_path = file_object.get_value("file_name")
        src_basename = os.path.basename(src_path)

        # NOTE: pretty hacky
        # remove version
        src_basename = re.sub(r"_v\d+", "", src_basename)


        #if src_basename != basename:
        #    src_basename = "%s <i style='opacity: 0.3; font-size: 0.8em'>(%s)</i>" % (src_basename, basename)

        span = DivWdg()
        span.add_style("display: inline-block")
        span.add_style("text-overflow: ellipsis")
        span.add_style("max-width: 220px")
        span.add_style("overflow-x: hidden")
        span.add_style("white-space: nowrap")
        span.add_attr("title", basename)
        span.add(src_basename)

        src_basename = span


        return src_basename


    def add_file_behaviors(my, item_div, dirname, basename):
        item_div.add_class("spt_drag_file_item")

        asset_base_dir = Environment.get_asset_dir()

        path = "%s/%s" % (dirname, basename)
        relative_dir = path.replace(asset_base_dir, "")
        relative_dir = os.path.dirname(relative_dir)
        item_div.add_attr("spt_relative_dir", relative_dir)

        search_types = my.search_types_dict


        file_codes = my.file_codes

        snapshot_codes = my.snapshot_codes

        search_type = search_types.get(path)

        # ??? What is this for?
        """
        if not search_type:
            parts = relative_dir.split("/")
            for i in range(len(parts)+1, 0, -1):
                tmp_rel_dir = "/".join(parts[:i])
                tmp_dir = "%s/%s" % (my.base_dir, tmp_rel_dir)
                print "tmp: ", tmp_dir
                search_type = search_types.get("%s/" % tmp_dir)
        """

        if not search_type:
            return


        file_code = file_codes.get(path)

        snapshot_code = snapshot_codes.get(path)
        item_div.add_attr("spt_file_code", file_code)
        item_div.add_attr("spt_snapshot_code", snapshot_code)


        item_div.add_behavior( {
            'type': 'drag',
            "mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.repo_browser.drag_file'

        } )


        # TODO: make this into a "smart" behavior
        item_div.add_behavior( {
        'type': 'click',
        'search_type': search_type,
        'cbjs_action': '''spt.repo_browser.click_file_bvr(evt, bvr);'''
        } )
        item_div.add_behavior( {
        'type': 'click',
        'modkeys': 'CTRL',
        'search_type': search_type,
        'cbjs_action': '''spt.repo_browser.click_file_bvr(evt, bvr);'''
        } )


        SmartMenu.assign_as_local_activator( item_div, 'FILE_ITEM_CTX' )





    #def add_base_dir_behaviors(my, div, base_dir):
    #    SmartMenu.assign_as_local_activator( div, 'FREEFORM_DIR_ITEM_CTX' )


    def add_dir_behaviors(my, item_div, dirname, basename):

        """ 
        item_div.add_attr("ondragenter", "spt.repo_browser.drag_enter(event, this)")
        item_div.add_attr("ondragleave", "spt.repo_browser.drag_leave(event, this)")
        item_div.add_attr("ondragover", "return false")
        item_div.add_attr("ondrop", "spt.repo_browser.drag_drop(event, this)")
        """
        item_div.add_class("DROP_ROW")
        item_div.add_class("spt_drop_handler")
        item_div.add_attr("spt_drop_handler", "spt.repo_browser.drag_drop")



        asset_base_dir = Environment.get_asset_dir()

        path = "%s/%s" % (dirname, basename)

        relative_dir = path.replace(asset_base_dir, "")
        relative_dir = relative_dir.strip("/")


        search_codes = my.search_codes



        item_div.add_behavior( {
            'type': 'drag',
            "mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.repo_browser.drag_file'

        } )



        #SmartMenu.assign_as_local_activator( item_div, 'STRICT_DIR_ITEM_CTX' )
        SmartMenu.assign_as_local_activator( item_div, 'FREEFORM_DIR_ITEM_CTX' )


        search_types = my.search_types_dict
        search_type = search_types.get("%s/" % path)

        if not search_type:
            parts = relative_dir.split("/")
            for i in range(len(parts)+1, 0, -1):
                tmp_rel_dir = "/".join(parts[:i])
                tmp_dir = "%s/%s" % (my.base_dir, tmp_rel_dir)
                search_type = search_types.get("%s/" % tmp_dir)

        if not search_type and search_types:
            search_type = search_types[search_types.keys()[0]]

        if not search_type and my.search_types:
            search_type = my.search_types[0]


        item_div.add_attr("spt_search_type", search_type)


        item_div.add_attr("spt_relative_dir", relative_dir)
        item_div.add_attr("spt_dirname", "%s/%s" % (dirname, basename))


        # TODO: make this into a relay behavior
        item_div.add_behavior( {
        'type': 'click',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_repo_browser_top");
        var content = top.getElement(".spt_repo_browser_content");

        var search_type = null;
        var parent = bvr.src_el;
        while (search_type == null) {
            search_type = parent.getAttribute("spt_search_type");
            if (search_type) break;
            parent = parent.getParent();
            parent = parent.getPrevious();
            parent.setStyle("border", "solid 1px blue");
            if (!parent) {
                alert("No Search Type found");
                return;
            }
        }

        var dir_list_top = bvr.src_el.getParent(".spt_dir_list_top");

        var search_keys = top.getAttribute("spt_search_keys");
        if (search_keys) {
            search_keys = search_keys.split("|");
        }
        else {
            search_keys = null;
        }

        var dirname = bvr.src_el.getAttribute("spt_dirname");
        var basename = "";

        spt.app_busy.show("Loading ...");
        var class_name = "tactic.ui.tools.RepoBrowserDirContentWdg";
        var kwargs = {
            search_type: search_type,
            view: 'table',
            dirname: dirname,
            basename: basename,
            search_keys: search_keys
        };
        spt.table.last_table = null;
        spt.panel.load(content, class_name, kwargs);
        spt.app_busy.hide();

        '''
        } )


        """
        item_div.add_behavior( {
            'type': 'accept_drop',
            'drop_code': 'DROP_ROW',
            'cbjs_action': '''
            //var src_el = bvr._drop_source_bvr.src_el;
            var src_el = spt.behavior.get_bvr_src( bvr._drop_source_bvr );
            var layout = src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);
            var row = src_el.getParent(".spt_table_row");

            spt.table.remove_rows([row]);

            var drop_el = bvr.src_el;


            '''
        } )
        """



    def get_file_icon(my, dir, item):
        path = "%s/%s" % (dir, item)
        #print "code: ", my.kwargs.get("file_codes").get(path)
        if not os.path.exists(path):
            return IconWdg.ERROR
        return IconWdg.DETAILS



    def get_dir_icon_wdg(my, dirname, basename):

        path = "%s/%s" % (dirname, basename)

        #search_types = my.kwargs.get("search_types")
        search_types = my.search_types_dict
        search_codes = my.search_codes

        search_code_list = search_codes.get("%s/" % path)
        search_type = search_types.get("%s/" % path)


        if not search_type:
            icon_string = IconWdg.HELP
        elif search_code_list and len(search_code_list) == 1:
            icon_string = IconWdg.CHECK
        else:
            icon_string = None

        # TODO: for now, disable this
        icon_string = None


        div = DivWdg()
        div.add_style("position: relative")

        icon = IconWdg(path, IconWdg.LOAD)
        div.add(icon)

        if icon_string:
            icon = IconWdg(path, icon_string, width=12)
            icon.add_style("position: absolute")
            icon.add_style("top: 6px")
            icon.add_style("left: -1px")
            div.add(icon)

        return div





class RepoBrowserActionCmd(Command):

    def execute(my):

        # if the search_type is working in "single file" mode, then
        # we can make a lot of assumptions about moving and deleting files
        mode = "single_file"


        search_type = my.kwargs.get("search_type")
        action = my.kwargs.get("action")

        base_dir = Environment.get_asset_dir()

        if action == 'create_folder':

            relative_dir = my.kwargs.get("relative_dir")
            if not relative_dir:
                return

            full_dir = "%s/%s" % (base_dir, relative_dir)

            if os.path.exists(full_dir):
                raise Exception("Directory [%s] already exists" % relative_dir)

            FileUndo.mkdir(full_dir)

        elif action == "delete_folder":

            relative_dir = my.kwargs.get("relative_dir")
            if not relative_dir:
                return

            # this will give an error if the directory is not empty
            full_dir = "%s/%s" % (base_dir, relative_dir)
            os.rmdir(full_dir)


        elif action == "rename_folder":

            old_relative_dir = my.kwargs.get("old_relative_dir")
            if not old_relative_dir:
                return
            new_relative_dir = my.kwargs.get("new_relative_dir")
            if not new_relative_dir:
                return

            old_dir = "%s/%s" % (base_dir, old_relative_dir)
            new_dir = "%s/%s" % (base_dir, new_relative_dir)

            search = Search("sthpw/file")
            search.add_filter("relative_dir", old_relative_dir)
            files = search.get_sobjects()

            for file in files:
                file.set_value("relative_dir", new_relative_dir)
                file.commit()

                # get the parent
                if mode == "single_file":
                    parent = Search.get_by_code( file.get("search_type"), file.get("search_code") )
                    if parent.column_exists("relative_dir"):
                        parent.set_value("relative_dir", new_relative_dir)
                        parent.commit()


            FileUndo.move(old_dir, new_dir)


        elif action == "copy_clipboard":

            relative_dir = my.kwargs.get("relative_dir")
            if not relative_dir:
                return

            search = Search("sthpw/file")
            search.add_filter("relative_dir", relative_dir)
            files = search.get_sobjects()

            snapshots = []
            search_keys = []
            for file_object in files:
                snapshot = file_object.get_parent()
                if snapshot:
                    snapshots.append(snapshot)
                    search_keys.append(snapshot.get_search_key())

            Clipboard.clear_selected()
            if search_keys:
                Clipboard.add_to_selected(search_keys)

 

        elif action == "delete_item":

            snapshot_code = my.kwargs.get("snapshot_code")

            snapshot = Snapshot.get_by_code(snapshot_code)
            #snapshot.delete()

            parent = snapshot.get_parent()


 

        elif action == "rename_item":

            relative_dir = my.kwargs.get("relative_dir")
            if not relative_dir:
                return
            relative_dir = relative_dir.strip("/")

            new_value = my.kwargs.get("new_value")
            old_value = my.kwargs.get("old_value")

            if not new_value:
                return
            if not old_value:
                return
            if old_value == new_value:
                return

            search = Search("sthpw/file")
            search.add_filter("relative_dir", relative_dir)
            search.add_filter("file_name", old_value)
            file = search.get_sobject()

            # get the snapshot
            snapshot = file.get_parent()
            sobject = snapshot.get_parent()

            context = snapshot.get_value("context")

            # get all of the snapshots
            search = Search("sthpw/snapshot")
            search.add_sobject_filter(sobject)
            search.add_filter("context", context)
            search.add_order_by("version")
            snapshots = search.get_sobjects()

            for snapshot in snapshots:

                xml = snapshot.get_xml_value("snapshot")
                version = snapshot.get_value("version")
                context = snapshot.get_value("context")

                print "version: ", version


                # need to make some big assumptions about the file name
                # find the main file and set the versions accoridngly

                files = File.get_by_snapshot(snapshot)
                main_file = ""
                for file in files:
                    if file.get_value("type") == "main":
                        main_file = file.get_value("file_name")
                        break


                base, ext = os.path.splitext(main_file)
                new_base, new_ext = os.path.splitext(new_value)


                if version == -1:
                    new_base = new_value
                else:
                    new_base = "%s_v%0.3d" % (new_value, version)

                for file in files:

                    file_name = file.get_value("file_name")
                    print "file_name: ", file.get_code(), file_name
                    new_file_name = file_name.replace(base, new_base)

                    old_path = "%s/%s/%s" % (base_dir, relative_dir, file_name)
                    new_path = "%s/%s/%s" % (base_dir, relative_dir, new_file_name)

                    print "new_path: ", new_path


                    file.set_value("file_name", new_file_name)
                    file.commit()

                    if version != -1 and not os.path.exists(new_path):
                        FileUndo.move(old_path, new_path)

                    # change the xml of the snapshot
                    node = xml.get_node("snapshot/file[@name='%s']" % file_name)
                    Xml.set_attribute(node, "name", new_file_name)

                snapshot.set_value( "snapshot", xml.to_string() )

                parts = context.split("/")
                if len(parts) == 2:
                    new_subcontext, new_ext = os.path.splitext(new_value)
                    context = "%s/%s" % (parts[0], new_subcontext)
                    snapshot.set_value("context", context)

                snapshot.commit()

            snapshots[-1].update_versionless("latest")

            sobject.set_value("name", new_value)
            sobject.commit()





class RepoBrowserCbk(Command):

    def execute(my):
        relative_dir = my.kwargs.get("relative_dir")
        from_relative_dir = my.kwargs.get("from_relative_dir")
        snapshot_code = my.kwargs.get("snapshot_code")
        search_key = my.kwargs.get("search_key")


        base_dir = Environment.get_asset_dir()




        if snapshot_code:
            snapshot = Search.get_by_code("sthpw/snapshot", snapshot_code)
            version  = snapshot.get_value("version")
            parent = snapshot.get_parent()

            context = snapshot.get_value("context")

            search = Search("sthpw/snapshot")
            search.add_parent_filter(parent)
            search.add_filter("context", context)
            search.add_order_by("versoin")
            snapshots = search.get_sobjects()

        elif search_key:

            parent = Search.get_by_search_key(search_key)
            snapshots = Snapshot.get_by_sobject(parent)
            # need to order by ascending version
            snapshots.reverse()


        else:

            # find all the files with the relative dir
            file_search = Search("sthpw/file")
            file_search.add_filter("relative_dir", "%s%%" % from_relative_dir, op='like')
            files = file_search.get_sobjects()


            if not os.path.isdir("%s/%s" % (base_dir, relative_dir)):
                raise Exception("relative_dir [%s] is not a directory" % relative_dir)


            parents = {}
            for file in files:
                basename = os.path.basename(from_relative_dir)

                file_relative_dir = file.get_value("relative_dir")

                sub_relative_dir = file_relative_dir.replace(from_relative_dir, "")
                sub_relative_dir = sub_relative_dir.strip("/")

                basename = os.path.basename(from_relative_dir)

                new_relative_dir = "%s/%s/%s" % (relative_dir, basename, sub_relative_dir)
                new_relative_dir = new_relative_dir.strip("/")

                file.set_value("relative_dir", new_relative_dir)
                file.commit()

                # find the parent
                parent_search_code = file.get_value("search_code")
                parent_search_type = file.get_value("search_type")

                search_key = "%s?code=%s" % (parent_search_type, parent_search_code)
                parent = parents.get(search_key)
                if not parent:
                    parent = Search.get_by_search_key(parent)

                if parent and parent.column_exists("relative_dir"):
                    parent.set_value("relative_dir", new_relative_dir)
                    parent.commit()



            search_keys = [x.get_search_key() for x in files]


            # move all of the folders.
            # NOTE: this may be a bit too much brute force.  It may take files
            # that are not in the file table (but these shouldn't be there
            # in the first place!)
            FileUndo.move("%s/%s" % (base_dir,from_relative_dir), "%s/%s" % (base_dir,relative_dir))

            return



        # handle single file moving

        all_files = []
        for snapshot in snapshots:
            # move all of the files from this snapshot
            files = snapshot.get_all_file_objects()
            for file in files:
                file.set_value("relative_dir", relative_dir)
                file.commit()
            all_files.extend(files)


        mode = "relative_dir"
        if mode == "relative_dir":
            # Some assumed behavior for this mode:
            # 1) all snapshots in this context exist in the same folder
            #    and should remain so
            # 2) all sobjects have a column called {relative_dir}
            # This should all fail cleanly if these assumptions are not the
            # case unless the sobject has a column called "relative_dir"
            # used for some other purpose
            if parent.column_exists("relative_dir"):
                parent.set_value("relative_dir", relative_dir)
                parent.commit()

        search_keys = [x.get_search_key() for x in all_files]

        # move the files to what the naming now says.
        # NOTE: this may not be correct.  A possible operation is to
        # move the file away from the naming conventions say.  In this
        # case, the file will be moved right back to where the naming
        # conventions says to move it.
        from tactic.command import NamingMigratorCmd
        cmd = NamingMigratorCmd( mode="file", search_keys=search_keys)
        cmd.execute()


        # find hightest version
        highest_snapshot = {}
        highest_version = {}
        for snapshot in snapshots:
            context = snapshot.get("context")
            version = snapshot.get_value("version")
            if version == -1:
                continue
            if version > highest_version.get(context):
                highest_version[context] = version
                highest_snapshot[context] = snapshot

        for snapshot in highest_snapshot.values():
            snapshot.update_versionless("latest")





class RepoBrowserContentWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        search_key = my.kwargs.get("search_key")
        if search_key:
            sobject = Search.get_by_search_key(search_key)
            search_type = sobject.get_search_type()
            snapshot = Snapshot.get_latest_by_sobject(sobject)
            if not snapshot:
                raise Excpetion("No snapshot found")

            path = snapshot.get_lib_path_by_type()
            dirname = os.path.dirname(path)
            basename = os.path.basename(path)

        else:
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
        path_div.add_color("background", "background")
        path_div.add_style("padding: 15px")
        path_div.add_style("margin-bottom: 15px")
        #path_div.add_border()

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

        config.append('''
        <element name='sobject_detail' title='Detail'>
            <display class='tactic.ui.tools.SObjectDetailWdg'>
                <search_key>%s</search_key>
            </display>
        </element>
        ''' % parent.get_search_key()
        )

        """
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
        """
 


 
        config.append('''</tab></config>''')
        config = "\n".join(config)
        config = config.replace("&", "&amp;")


        selected = WidgetSettings.get_value_by_key("repo_browser_selected")

        # remember last tab
        #selected = "notes"
        selected = None

        from tactic.ui.container import TabWdg
        tab = TabWdg(config_xml=config, selected=selected, show_remove=False, show_add=False, tab_offset=10)
        div.add(tab)


        return div



class RepoBrowserSearchWrapper(object):

    def alter_search(my, search):

        search_type = search.get_full_search_type()

        # search for all files that are in this relative_dir
        file_search = Search("sthpw/file")
        file_search.add_filter("relative_dir", "%s%%" % reldir, op='like')
        file_search.add_filter("search_type", search_type)

        # use the above search to find all sobjects with files in this
        # relative_dir
        search.add_relationship_search_filter(file_search)






class RepoBrowserDirContentWdg(BaseRefreshWdg):

    def get_display(my):
        search_type = my.kwargs.get("search_type")
        project_code = Project.get_project_code()

        search_type = Project.get_full_search_type(search_type, project_code=project_code)


        snapshot_codes = my.kwargs.get("snapshot_codes")
        if snapshot_codes:
            search = Search("sthpw/snapshot")
            search.add_filters("code", snapshot_codes)

            search2 = Search(search_type)
            search2.add_relationship_search_filter(search)
            sobjects = search2.get_sobjects()
        else:

            dirname = my.kwargs.get("dirname")
            basename = my.kwargs.get("basename")
            path = dirname

            asset_dir = Environment.get_asset_dir()
            if not dirname.startswith(asset_dir):
                top.add("Error: path [%s] does not belong in the asset directory [%s]" % (path, asset_dir))
                return top

            reldir = path.replace(asset_dir, "")
            reldir = reldir.strip("/")


            # search for all files that are in this relative_dir
            search = Search("sthpw/file")
            search.add_filter("relative_dir", "%s%%" % reldir, op='like')
            search.add_filter("search_type", search_type)

            # use the above search to find all sobjects with files in this
            # relative_dir
            search2 = Search(search_type)
            search2.add_relationship_search_filter(search)

            key = "repo_browser:%s" % search_type
            parent_search_str = WidgetSettings.get_value_by_key(key)
            if parent_search_str:
                parent_search = Search(search_type)
                parent_search.select.loads(parent_search_str)
                parent_search.add_column("code")
                search2.add_search_filter("code", parent_search)


            sobjects = search2.get_sobjects()


        # get the sobject codes to feed into the layout widget
        # NOTE: this could be very very slow ... there could be a lot
        # of sobjects in this search and will produce a massive
        # number of search_codes
        search_codes = [x.get_value("code") for x in sobjects]
        search_codes_str = "|".join(search_codes)
        expression = "@SEARCH(%s['code','in','%s'])" % (search_type,search_codes_str)
        #print "expression: ", expression

        search_keys = my.kwargs.get("search_keys")


        top = my.top

        path = my.kwargs.get("dirname")
        path_div = DivWdg()
        top.add(path_div)
        path_div.add("<b>Path:</b> %s" % path)
        path_div.add_color("color", "color")
        path_div.add_color("background", "background")
        path_div.add_style("padding: 15px")
        #path_div.add_style("margin: -1 -1 0 -1")
        #path_div.add_border()




        #layout_mode = 'default'

        search_type_obj = SearchType.get(search_type)
        layout_mode = search_type_obj.get_value("default_layout", no_exception=True)
        if layout_mode == '':
            layout_mode = 'default'

        if layout_mode == 'default' or layout_mode == 'browser':
            # if browser default is browser, then like we don't want to see
            # a browser again.
            layout_mode = 'tile'

        layout_mode = "tile"


        element_names = None
        if layout_mode == "checkin":
            element_names = ['preview','code','name','general_checkin','file_list', 'history','description','notes']



        from tactic.ui.panel import ViewPanelWdg
        layout = ViewPanelWdg(
            search_type=search_type,
            expression=expression,
            view="table",
            element_names=element_names,
            show_shelf=False,
            show_search_limit=False,
            layout=layout_mode,
            scale='100',
            width='100%',

        )


        top.add(layout)

        return top



