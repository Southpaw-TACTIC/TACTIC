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

from pyasm.common import Environment, Xml, Common

from pyasm.web import DivWdg, WebContainer, Table, WidgetSettings, SpanWdg
from pyasm.biz import Snapshot, Project, File
from pyasm.search import Search, SearchType, SearchKey, FileUndo
from pyasm.widget import IconWdg, CheckboxWdg
from pyasm.command import Command

from tactic.ui.panel import FastTableLayoutWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import DirListWdg, IconButtonWdg, ButtonNewWdg, ButtonRowWdg, ActionButtonWdg
from tactic.ui.container import Menu, MenuItem, SmartMenu, DialogWdg, ResizableTableWdg

import os, shutil, re


class RepoBrowserWdg(BaseRefreshWdg):


    def get_display(my):

        top = my.top
        top.add_color("background", "background")
        top.add_class("spt_repo_browser_top")
        my.set_as_panel(top)
        
        table = Table()
        top.add(table)
        table.add_color("color", "color")
        table.add_style("width: 100%")
 
        my.mode = 'main'
        #my.mode = 'all'
        #my.mode = 'folder'

        keywords = my.kwargs.get("keywords")
        
        
        search_type = my.kwargs.get("search_type")
        if search_type:
            search_types = [search_type]
        else:
            search_types = None

        search = my.kwargs.get("search")
        if search:
            search.set_limit(1000)
            search.set_offset(0)
        else:
            search = Search(search_type)
        
        # FIXME: Single asset mode needs to be passed through ViewPanelWdg
        # so that the TACTIC shelf is available for search.
        single_asset_mode = my.kwargs.get("single_asset_mode")
        if "workflow/asset" in search_type:
            single_asset_mode = True

        parent_key = my.kwargs.get("search_key")
        if parent_key:
            parent = Search.get_by_search_key(parent_key)
            my.sobjects = [parent]
            
            # FIXME: How can we generically determine the parent's base directory?
            # For now, assume that all snapshots are stored under a relative directory 
            # that is two levels up from a typical snapshot. 
            # One possible solution is to build the search first, then display necessary files.
            from tactic_client_lib import TacticServerStub
            server = TacticServerStub.get()
            virtual_path = server.get_virtual_snapshot_path(parent_key)
            context_path, _ = os.path.split(virtual_path)
            parent_path, _ = os.path.split(context_path)
            container_path, _ = os.path.split(parent_path)
            #relative_dir = os.path.relpath(container_path, base_dir)
            #project_dir = "%s/%s" % (base_dir, relative_dir)
            project_dir = container_path 

            search_type = parent.get_search_type()
            parent_code = parent.get_value("code", no_exception=True)

            if parent_code:
                search.add_filter("code", parent_code)
        else:
            project_code = Project.get_project_code()
            base_dir = Environment.get_asset_dir()
            project_dir = "%s/%s" % (base_dir, project_code)
        
        
        # FIXME: is this ever used?
        search_keys =  [x.get_search_key() for x in my.sobjects]
        top.add_attr("spt_search_keys", "|".join(search_keys) )

        table.add_row()

        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add_style("width: 1px")
        left.add_border(size="0px 1px 0px 0px", color="table_border")

        shelf_wdg = DivWdg()
        left.add(shelf_wdg)


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


        # Where should dynamic be passed in?
        dynamic = True
        
        # Display the basename of of the base_dir 
        # default is True.
        show_base_dir = my.kwargs.get("show_base_dir")
        
        # The left contains a directory listing
        # starting at project_dir.
        dir_list = RepoBrowserDirListWdg(
                single_asset_mode=single_asset_mode,
                base_dir=project_dir,
                location="server",
                show_base_dir=show_base_dir,
                open_depth=open_depth,
                search_types=search_types,
                dynamic=dynamic,
                keywords=keywords,
                search_keys=search_keys,
                search=search,
                parent_key=parent_key
        )
        content_div.add(dir_list)


        # The right contains browser of related sobjects determined.
        # Nesting content -> outer_div -> content_div
        content = table.add_cell()
        content.add_style("vertical-align: top")

        outer_div = DivWdg()
        content.add(outer_div)
        outer_div.add_class("spt_repo_browser_content")

        content_div = DivWdg()
        content_div.add_style("min-width: 400px")
        outer_div.add(content_div)
 
        count = 0
        if search:
            count = search.get_count()
        if count:
            widget = RepoBrowserDirContentWdg(
                single_asset_mode=single_asset_mode,
                search_type=search_type,
                view='table',
                dirname=project_dir,
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
 
        '''
        table.add_row()
        bottom = table.add_cell()
        bottom.add_attr("colspan", "3")
        info_div = DivWdg()
        bottom.add(info_div)

        #info_div.add_style("height: 100px")
        '''

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

        # add a search type filter ... ignore this is the search_type are snapshots
        if search_types:
            if search_types[0] != "sthpw/snapshot":
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
                if True:
                    #if not my.dynamic:
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


        # FIXME: this could be very slow for large folders
        search_type = search_types[0]

        key = "repo_browser:%s" % search_type
        parent_search_str = WidgetSettings.get_value_by_key(key)
        if parent_search_str:
            parent_search = Search(search_type)
            parent_search.select.loads(parent_search_str)
            parents = parent_search.get_sobjects()
            parent_codes = [x.get_value("code") for x in parents]

            if search_type == "sthpw/snapshot":
                search.add_filters("snapshot_code", parent_codes)
            else:
                search.add_filter("search_type", search_type)
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
        my.search_keys_dict = {}


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

                search_key = "%s&code=%s" % (search_type, search_code)
                my.search_keys_dict[path] = search_key

                if not file_name:
                    #print search_type, relative_dir
                    continue

                # go up the path and set the search type
                parts = relative_dir.split("/")
                for i in range (0, len(parts)+1):
                    tmp_dir = "/".join(parts[:i])
                    tmp_dir = "%s/%s/" % (asset_base_dir, tmp_dir)
                    my.search_types_dict[tmp_dir] = search_type


        my.counts = {}

        # find any folders that match
        # FIXME: this is slow and need a way to pass keywords through
        keywords = my.kwargs.get("keywords") or []
        #keywords = ["oculus", "one"]
        if keywords:
            dirnames = os.listdir(base_dir)
            for dirname in dirnames:

                parts = Common.extract_keywords_from_path(dirname)
                #parts = [x.lower() for x in parts]
                parts.append(dirname.lower())
                parts = set(parts)

                for root, subdirnames, subbasenames in os.walk("%s/%s" % (base_dir, dirname)):
                    for subdirname in subdirnames:
                        subparts = Common.extract_keywords_from_path(subdirname)
                        parts.update(subparts)
                        parts.add(subdirname.lower())


                subdir = "%s/%s" % (base_dir, dirname)

                match = True
                for keyword in keywords:
                    if not keyword.lower() in parts:
                        match = False
                        break

                if match:
                    paths.append("%s/" % subdir)
                    my.counts[subdir] = -1

        # add dirnames if they have sobject files in them
        #if not show_no_sobject_folders:
        if os.path.exists(base_dir) and os.path.isdir(base_dir):
            dirnames = os.listdir(base_dir)
            for dirname in dirnames:
                subdir = "%s/%s" % (base_dir, dirname)
                if not os.path.isdir(subdir):
                    continue


                if my.counts.get(subdir) is None:
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
        top.add_class("spt_file_drag_top")
        top.add_style("position: relative")

        top.add_behavior( {
        'type': 'load',
        'border': border,
        'cbjs_action': '''

        spt.repo_browser = {};
        spt.repo_browser.start_x = null;
        spt.repo_browser.start_y = null;
        spt.repo_browser.top = null;


         spt.repo_browser.drag_file_setup = function(evt, bvr, mouse_411) {
             spt.repo_browser.top = bvr.src_el.getParent(".spt_repo_browser_list");
             spt.repo_browser.start_x = mouse_411.curr_x;
             spt.repo_browser.start_y = mouse_411.curr_y;
         }

         spt.repo_browser.drag_file_motion = function(evt, bvr, mouse_411) {
             var diff_x = mouse_411.curr_x - spt.repo_browser.start_x;
             var diff_y = mouse_411.curr_y - spt.repo_browser.start_y;
             if (diff_y < 5 && diff_y > -5) {
                 return;
             }

             var pos = spt.repo_browser.top.getPosition();

             bvr.src_el.setStyle("border", "solid 1px " + bvr.border);
             bvr.src_el.setStyle("box-shadow", "0px 0px 5px");
             bvr.src_el.setStyle("position", "absolute");
             bvr.src_el.setStyle("padding", "5px");
             bvr.src_el.position({x:mouse_411.curr_x+10 - pos.x, y:mouse_411.curr_y+10 - pos.y});
        }


        spt.repo_browser.drag_file_action = function(evt, bvr, mouse_411) {
            /* Drag and drop for file and directories within the DirList */
            
            // Remember the src_dir top for refresh later
            var src_dir_top = bvr.src_el.getParent(".spt_dir_list_handler_top");

            var diff_y = mouse_411.curr_y - spt.repo_browser.start_y;
            if (diff_y < 5 && diff_y > -5) {
                return;
            }

            bvr.src_el.setStyle("border", "");
            bvr.src_el.setStyle("box-shadow", "");
            bvr.src_el.setStyle("position", "relative");
            bvr.src_el.setStyle("top", "0px");
            bvr.src_el.setStyle("left", "0px");
            bvr.src_el.setStyle("padding", "2px 0px 2px 15px");

            // Get the drop folder
            var drop_on_el = spt.get_event_target(evt);
            if (!drop_on_el.hasClass("spt_dir_item")) {
                drop_on_el = drop_on_el.getParent(".spt_dir_item");
            }

            // If drop hasn't occured yet or no drop folder found
            if (! drop_on_el) {
                spt.panel.refresh(src_dir_top);
                return;
            }
  
            if ( drop_on_el.hasClass("spt_open") == true) {
                var sibling = drop_on_el.getNext();
                var inner = sibling.getElement(".spt_dir_list_handler_content");
                bvr.src_el.inject(inner, 'top');
                var padding = drop_on_el.getStyle("padding-left");

                if (bvr.src_el.hasClass("spt_dir") ) {
                    bvr.src_el.setStyle("padding-left", "");
                }
                else {
                    bvr.src_el.setStyle("padding-left", "15px");
                }
            }
            else {
                bvr.src_el.setStyle("display", "none");
            }
            
            // Move the files
            var server = TacticServerStub.get(); 

            // Get the snapshot or dir moved
            var snapshot_code = bvr.src_el.getAttribute("spt_snapshot_code");
            var from_relative_dir = bvr.src_el.getAttribute("spt_relative_dir");
            // Get the new relative_dir
            var relative_dir = drop_on_el.getAttribute("spt_relative_dir");
            
            var cmd = 'tactic.ui.tools.RepoBrowserCbk';
            var kwargs = {
                snapshot_code: snapshot_code,
                from_relative_dir: from_relative_dir,
                relative_dir: relative_dir
            }
            try {
                server.execute_cmd(cmd, kwargs); 
            } catch(err) {
                spt.alert(spt.exception.handler(err));
            }
       
            // Refresh the source dir top and destination dir top 
            spt.panel.refresh(src_dir_top);
                
            var dest_dir_top = drop_on_el.getParent(".spt_dir_list_handler_top");
            spt.panel.refresh(dest_dir_top);
 
            
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
            // When an item is clicked in the directory, display 
            // the file detail.
  
            if (bvr.src_el.hasClass("spt_item_value")) {
                bvr.src_el = bvr.src_el.getParent(".spt_dir_list_item");
            }
        
            if (!evt.control) {
                spt.repo_browser.clear_selected();
            }

            spt.repo_browser.toggle_select(bvr.src_el);
            var selected = spt.repo_browser.get_selected();

            var top = bvr.src_el.getParent(".spt_repo_browser_top");
            var content = top.getElement(".spt_repo_browser_content");

            spt.app_busy.show("Loading information");
            
            if (selected.length > 1) {
                var snapshot_codes = [];
                for (var i = 0; i < selected.length; i++) {
                    snapshot_codes.push( selected[i].getAttribute("spt_snapshot_code"));
                }
                var class_name = "tactic.ui.tools.RepoBrowserDirContentWdg";
                var kwargs = {
                  single_asset_mode: bvr.single_asset_mode,
                  search_type: bvr.search_type,
                  snapshot_codes: snapshot_codes
                };
            }
            else {
                var dirname = bvr.src_el.getAttribute("spt_dirname");
                var basename = bvr.src_el.getAttribute("spt_basename");
                
                var class_name = "tactic.ui.tools.RepoBrowserContentWdg";
                var kwargs = {
                  single_asset_mode: bvr.single_asset_mode,
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
            /* Drop action of tile on folder */
            
            var top = bvr.src_el.getParent(".spt_tile_top");
            var layout = bvr.src_el.getParent(".spt_layout");
            spt.table.set_layout(layout);

            var search_keys = spt.table.get_selected_search_keys();
            if (search_keys.length != 0) {
                var search_key = null;
            }
            else {
                var search_key = top.getAttribute("spt_search_key");
            }

            var target = $(evt.target);
            if (!target.hasClass("spt_dir")) {
                target = target.getParent(".spt_dir");
            }
            var relative_dir = target.getAttribute("spt_relative_dir");


            var server = TacticServerStub.get(); 
            var cmd = 'tactic.ui.tools.RepoBrowserCbk';
            var kwargs = {
                search_key: search_key,
                search_keys: search_keys,
                relative_dir: relative_dir
            }
            try {
                server.execute_cmd(cmd, kwargs); 
            } catch(err) {
                spt.alert(spt.exception.handler(err));
                return;
            }

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

       
        search_types = my.kwargs.get("search_types")
        if search_types:
            search_type = search_types[0]
        else:
            search_type = my.kwargs.get("search_type") 

        # If single_asset_mode is specified, then clicking 
        # a file or directory will display information
        # related to the single asset search type.
        single_asset_mode = my.kwargs.get("single_asset_mode")

        # When the parent key is defined, clicking directory
        # item displays sthpw/snapshots based on related parent_type.
        # Otherwise, it display the search type as defined.
        parent_key = my.kwargs.get("parent_key")
        if parent_key:
            parent = Search.get_by_search_key(parent_key)
            search_type = parent.get_search_type()
        

        # Directory click up - display related sObjects
        top.add_relay_behavior( {
        'type': 'click',
        'single_asset_mode': single_asset_mode,
        'search_type': search_type,
        'bvr_match_class': 'spt_dir_value',
        'cbjs_action': '''
     
            var top = bvr.src_el.getParent(".spt_repo_browser_top");
            var content = top.getElement(".spt_repo_browser_content");
            var item_div = bvr.src_el.getParent(".spt_dir_item");

            // Get parent search keys
            var search_keys = top.getAttribute("spt_search_keys");
            if (search_keys) {
                search_keys = search_keys.split("|");
            } else {
                search_keys = null;
            }

            var dirname = item_div.getAttribute("spt_dirname");
            
            spt.app_busy.show("Loading ...");
            
            var class_name = "tactic.ui.tools.RepoBrowserDirContentWdg";
            var kwargs = {
                single_asset_mode: bvr.single_asset_mode,
                search_type: bvr.search_type,
                view: 'table',
                dirname: dirname,
                search_keys: search_keys
            };
            spt.table.last_table = null;
            spt.panel.load(content, class_name, kwargs);
            spt.app_busy.hide();

        '''
        } )


        # File click-up - display file detail
        top.add_relay_behavior( {
            'type': 'click',
            'single_asset_mode': single_asset_mode,
            'search_type': search_type,
            'bvr_match_class': 'spt_item_value',
            'cbjs_action': '''spt.repo_browser.click_file_bvr(evt, bvr);'''
        } )


    def get_dir_context_menu(my, mode="freeform"):

        parent_key = my.kwargs.get("parent_key")

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        if mode == "freeform":

            menu_item = MenuItem(type='action', label='New Folder')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'type': 'click_up',
                'cbjs_action': r'''
                
                var activator = spt.smenu.get_activator(bvr);
                var relative_dir = activator.getAttribute("spt_relative_dir");
                var search_type = activator.getAttribute("spt_search_type");
              
                //TODO: If directory is not open, open it to edit new item.
                //if (!activator.hasClass("spt_open")) {
                //    var swap_top = activator.getElement(".spt_swap_top");
                //    var swap_child = swap_top.getLast();
                //    var expand_bvrs = spt.behavior.get_bvrs_by_type("click_up", swap_child);
                //    for (var i = 0; i < expand_bvrs.length; i++) {
                //        spt.behavior.run_cbjs(expand_bvrs[i].cbjs_action, {src_el: swap_child});
                //    }
                //}

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
                    // Attempt to create new folder
                    var value = this.value;

                    if (!value) {
                        div.destroy();
                    }

                    var valid_regex = /^[a-zA-Z0-9\_\s\-\.]+$/;
                    if (!valid_regex.test(value)) {
                        spt.alert("Please enter a valid file system name. Names may contain alphanumeric characters, underscores, hyphens and spaces.");
                        div.destroy();
                        return; 
                    }     
                    
                    var span = $(document.createElement("span"));
                    span.innerHTML = " " +value;
                    span.replaces(input);
                    span.addClass("spt_dir_value");

                    div.setAttribute("spt_relative_dir", new_relative_dir);
                    div.addClass("spt_dir_item");
                    
                    var new_relative_dir = relative_dir + "/" + value;
                    
                    var server = TacticServerStub.get();
                    var class_name = 'tactic.ui.tools.RepoBrowserActionCmd';
                    
                    var kwargs = {
                        search_type: bvr.search_type,
                        action: 'create_folder',
                        relative_dir: new_relative_dir
                    }
                    
                    try {
                        server.execute_cmd(class_name, kwargs);
                        
                        var dir_top = span.getParent(".spt_dir_list_handler_top");
                        spt.panel.refresh(dir_top);
                    } catch(err) {
                        spt.alert(spt.exception.handler(err));
                        div.destroy();
                        return;
                    }
                    

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
                var original_dir = activator.getAttribute("spt_reldir");

                var original_el = activator.getElement(".spt_dir_value");
                original_el.setStyle("display", "none");
                
                // Inject a input
                var input = $(document.createElement("input"));
                input.value = original_dir;
                input.setAttribute("type", "text");
                input.setStyle("width", "200px");
                input.inject(original_el, "after");
                
                var parts = relative_dir.split("/");
                input.value = parts[parts.length-1];
                var base_relative_dir = parts.slice(0, parts.length-1).join("/");
                
                input.onblur = function() {
                    var value = this.value;
                    var valid_regex = /^[a-zA-Z0-9\_\s\-\.]+$/;
                    if (!valid_regex.test(value)) {
                        spt.alert("Please enter a valid file system name. Names may contain alphanumeric characters, underscores, hyphens and spaces.");
                        this.value = original_dir;
                        input.focus();
                        return; 
                    } else if (value == original_dir) {
                        input.destroy();
                        original_el.setStyle("display", "");
                        return;
                    }
                    
                    var new_relative_dir = base_relative_dir + "/" + value;
                    
                    var span = $(document.createElement("span"));
                    span.innerHTML = " " +value;
                    span.replaces(input);

                    try {
                        var server = TacticServerStub.get();
                        var class_name = 'tactic.ui.tools.RepoBrowserActionCmd';
                        var kwargs = {
                            search_type: bvr.search_type,
                            action: 'rename_folder',
                            old_relative_dir: relative_dir,
                            new_relative_dir: new_relative_dir
                        };

                        server.execute_cmd(class_name, kwargs)
                    
                        spt.notify.show_message("Folder rename complete");
                        var dir_top = activator.getParent(".spt_dir_list_handler_top");
                        spt.panel.refresh(dir_top);
                        
                    } catch(err) {
                        spt.alert(spt.exception.handler(err));
                        span.destroy();
                        original_el.setStyle("display", "");
                    }

                };
                
                input.focus();
                input.select();

                '''
            } )

            menu_item = MenuItem(type='action', label='Delete Folder')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                // This will only delete the folder if it is empty
                var activator = spt.smenu.get_activator(bvr);
                var relative_dir = activator.getAttribute("spt_relative_dir");

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
                catch(err) {
                    spt.alert(spt.exception.handler(err));
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
            'search_key': parent_key,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var search_type = activator.getAttribute("spt_search_type");

            var relative_dir = activator.getAttribute("spt_relative_dir");
            var class_name = 'tactic.ui.tools.IngestUploadWdg';
            var kwargs = {
                search_type: search_type,
                relative_dir: relative_dir,
                search_key: bvr.search_key
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


        """
        TODO: This should not be exposed unless the applet is available.
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
        """


        return menu


    def get_file_context_menu(my):

        single_asset_mode = my.kwargs.get("single_asset_mode")

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
            'single_asset_mode': single_asset_mode,
            'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);
                var content = activator.getElement(".spt_basename_content");
                var file_name = content.getAttribute("spt_file_name");
                var old_value = content.getAttribute("spt_src_basename");
                var relative_dir = activator.getAttribute("spt_relative_dir");
                
        
                var original_el = activator.getElement(".spt_item_value");
                original_el.setStyle("display", "none");
                
                // Inject a input
                var input = $(document.createElement("input"));
                input.value = old_value;
                input.setAttribute("type", "text");
                input.setStyle("width", "200px");
                input.inject(original_el, "after");
                
                input.onblur = function() {
                    var new_value = this.value;
                    var valid_regex = /^[a-zA-Z0-9_\s-\.]+$/;
                    if (!valid_regex.test(new_value)) {
                        spt.alert("Please enter a valid file system name containing letters, numbers, or characters: . - _");
                        input.value = old_value;
                        input.focus();
                        return; 
                    } else if (new_value == old_value) {
                        input.destroy();
                        original_el.setStyle("display", "");
                        return;
                    }
                    
                    var span = $(document.createElement("span"));
                    span.innerHTML = " " + new_value;
                    span.replaces(input);

                    try {
                        var server = TacticServerStub.get();
                        var class_name = 'tactic.ui.tools.RepoBrowserActionCmd';
                        var kwargs = {
                            search_type: bvr.search_type,
                            single_asset_mode: bvr.single_asset_mode,
                            action: 'rename_item',
                            relative_dir: relative_dir,
                            file_name: file_name,
                            old_value: old_value,
                            new_value: new_value
                        };
                        server.execute_cmd(class_name, kwargs)
                    
                        spt.notify.show_message("Item rename complete");
                        var dir_top = activator.getParent(".spt_dir_list_handler_top");
                        spt.panel.refresh(dir_top);
                    } catch(err) {
                        spt.alert(spt.exception.handler(err));
                        span.destroy();
                        original_el.setStyle("display", "");
                    }

                };
                
                input.focus();
                input.select();

            '''
        } )



        menu_item = MenuItem(type='action', label='Delete Item')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'single_asset_mode': single_asset_mode,
            'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);

                if (["True", true, "true"].indexOf(bvr.single_asset_mode) > -1) {
                    var search_key = activator.getAttribute("spt_search_key");
                } else {
                    var server = TacticServerStub.get();
                    var snapshot_code = activator.getAttribute("spt_snapshot_code");
                    var search_key = server.build_search_key("sthpw/snapshot", snapshot_code); 
                }
               
                if (!search_key) return;
                activator.addClass("spt_browser_deleted");

                // On complete, refresh the grandparent directory and the ContentBrowserWdg in case 
                // file in display was deleted.
                var delete_on_complete = "var target = document.getElement('.spt_browser_deleted');"
                delete_on_complete += "var parent_dir = target.getParent('.spt_dir_list_handler_top');"
                delete_on_complete += "var grandparent_dir = parent_dir.getParent('.spt_dir_list_handler_top');"
                delete_on_complete += "if (grandparent_dir) {"
                delete_on_complete += "    spt.panel.refresh(grandparent_dir);"
                delete_on_complete += "}"
                delete_on_complete += "var detail_top = document.getElement('.spt_browser_detail_top');"
                delete_on_complete += "spt.panel.refresh(detail_top);"
                var class_name = 'tactic.ui.tools.DeleteToolWdg';
                var kwargs = {
                  search_key: search_key,
                  on_complete: delete_on_complete
                }
                var popup = spt.panel.load_popup("Delete Item", class_name, kwargs);

            '''
        } )




        return menu




    def get_dirname(my, dirname, basename):

        path = "%s/%s" % (dirname, basename)
        counts = my.counts.get(path)
        if counts == -1:
            return basename
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
        
        # FIXME: In single asset mode, simply display the asset name or 
        # atleast single context.
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
        span.add_attr("spt_src_basename", src_basename)
        span.add_attr("spt_file_name", src_path)
        span.add_class("spt_basename_content")

        return span


    def add_file_behaviors(my, item_div, dirname, basename):
        item_div.add_class("spt_drag_file_item")

        asset_base_dir = Environment.get_asset_dir()

        path = "%s/%s" % (dirname, basename)
        relative_dir = path.replace(asset_base_dir, "")
        relative_dir = os.path.dirname(relative_dir)
        item_div.add_attr("spt_relative_dir", relative_dir)

        search_types = my.search_types_dict
        search_keys = my.search_keys_dict

        search_key = search_keys.get(path)
        item_div.add_attr("spt_search_key", search_key)


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

        SmartMenu.assign_as_local_activator( item_div, 'FILE_ITEM_CTX' )





    #def add_base_dir_behaviors(my, div, base_dir):
    #    SmartMenu.assign_as_local_activator( div, 'FREEFORM_DIR_ITEM_CTX' )


    def add_dir_behaviors(my, item_div, dirname, basename):

        parent_key = my.kwargs.get("parent_key")
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
            
        single_asset_mode = my.kwargs.get("single_asset_mode")
        if single_asset_mode in [True, "true", "True"]:
            single_asset_mode = True
        else:
            single_aset_mode = False


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
 
            # TODO: Users should be able to delete a folder with snapshots,
            # FIXME: If there are dangling files, user should no that.
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
          
            if old_relative_dir == new_relative_dir:
                return

            old_dir = "%s/%s" % (base_dir, old_relative_dir)
            new_dir = "%s/%s" % (base_dir, new_relative_dir)
       
            # We are assuming that as long as there is no naming conflict with
            # the top dir, than none of the file names will create a conflict.
            if (os.path.exists(new_dir)):
                raise Exception("Directory [%s] already exists." % new_dir) 

            # find all of the files in this relative_dir
            search = Search("sthpw/file")
            search.add_op("begin")
            search.add_filter("relative_dir", "%s" % old_relative_dir)
            search.add_filter("relative_dir", "%s/%%" % old_relative_dir, op='like')
            search.add_op("or")
            files = search.get_sobjects()
                
            parent_keys = set() 
            relative_dirs = {}
            for file in files:
                file_sub_dir = file.get_value("relative_dir")
                file_sub_dir = file_sub_dir.replace(old_relative_dir, "")
                file_sub_dir = file_sub_dir.strip("/")
                if file_sub_dir:
                    file.set_value("relative_dir", "%s/%s" %(new_relative_dir, file_sub_dir))
                else:
                    file.set_value("relative_dir", new_relative_dir)
                file.commit()

                # find the parent and store in dictionary for update later
                parent_search_code = file.get_value("search_code")
                parent_search_type = file.get_value("search_type")

                parent_key = "%s&code=%s" % (parent_search_type, parent_search_code)
                parent_keys.add(parent_key)
                relative_dirs[parent_key] = new_relative_dir

            # set the relative dirs of the parents
            parents = Search.get_by_search_keys(list(parent_keys))
            for parent in parents:
                if parent.column_exists("relative_dir"):
                    new_relative_dir = relative_dirs.get(parent.get_search_key())
                    parent.set_value("relative_dir", new_relative_dir)
                    my.set_keywords(parent)
                    parent.commit()

            # Finally, move the entire directory tree.
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

 

        elif action == "rename_item":
            # Renaming an item is actually renaming a context
 
            relative_dir = my.kwargs.get("relative_dir")
            if not relative_dir:
                return
            relative_dir = relative_dir.strip("/")

            file_name = my.kwargs.get("file_name")
            new_value = my.kwargs.get("new_value")
            old_value = my.kwargs.get("old_value")

            if not new_value:
                raise Exception("File renaming failed - New file name not given.")
            if not old_value:
                raise Exception("File renaming failed - Original file not given.")
            if old_value == new_value:
                # Fail silently
                return

            # Get the file sObject that was renamed
            search = Search("sthpw/file")
            search.add_filter("relative_dir", relative_dir)
            search.add_filter("file_name", file_name)
            file = search.get_sobject()
            if not file:
                raise Exception("File not found")
         
            # Check validity: This renaming allows spaces. Compare new name 
            # with underscores replacing spaces to cleaned filename.
            import re
            match = re.match('^[a-zA-Z0-9\_\s\-\.]+$', new_value)
            if not match:
                raise Exception("Invalid file name")

            # For now, user cannot change an extensions.
            # If the user has not entered a matching extension, 
            # the original extension will be appended onto the new name.
            new_base, new_ext = os.path.splitext(new_value)
            old_base, old_ext = os.path.splitext(file_name)
            if not new_ext or new_ext != old_ext:
                new_base = new_value
                new_ext = old_ext
            
            # TODO: If in single asset mode, asset in relative_dir
            # must be unique.

            # get the snapshot
            snapshot = file.get_parent()
            sobject = snapshot.get_parent()
            context = snapshot.get_value("context")

            # get all of the snapshots. Make sure versionless is the first one
            search = Search("sthpw/snapshot")
            search.add_sobject_filter(sobject)
            search.add_filter("context", context)
            search.add_order_by("version")
            snapshots = search.get_sobjects()

            # Build set of parent sObjects to update keywords
            parents = {}
     
            # For each snapshot, update its xml, files and context.
            for snapshot in snapshots:
                # For each file in the snapshot, update the filename.
                # Build a list of tuples - (old_path, new_path) for each
                # file. If one of these has a naming conflict, fail on the 
                # entire snapshot.
                # Otherwise, commit database changes and move all files.
                
                xml = snapshot.get_xml_value("snapshot")
                version = snapshot.get_value("version")
                context = snapshot.get_value("context")
                search_code = snapshot.get_value("search_code")
                if not parents.get(search_code):
                    parent = snapshot.get_parent()
                    parents[search_code] = parent

                # NOTE: We are assuming that files having a naming convention
                # as follows: {basepath}_v{ver#} where the base path is based off
                # of the main file in the snapshot.
                
                # Build new versioned base name
                # FIXME: Why are we not using get main?
                files = File.get_by_snapshot(snapshot)
                main_file = ""
                for file in files:
                    if file.get_value("type") == "main":
                        main_file = file.get_value("file_name")
                        break

                unversioned_base, file_ext = os.path.splitext(main_file)
                if version == -1:
                    new_versioned_base = new_base
                else:
                    new_versioned_base = "%s_v%0.3d" % (new_base, version)

                for file in files:
                    # Build the new path and check if it exists
                    file_name = file.get_value("file_name")
                    new_file_name = file_name.replace(unversioned_base, new_versioned_base)
                    new_path = "%s/%s/%s" % (base_dir, relative_dir, new_file_name)
                    if (os.path.exists(new_path)):
                        raise Exception("[%s] already exists in %s" % (new_file_name, relative_dir))

                    # Move the file it is not versionaless
                    old_path = "%s/%s/%s" % (base_dir, relative_dir, file_name)
                    file.set_value("file_name", new_file_name)
                    file.commit()
                    if version != -1:
                        FileUndo.move(old_path, new_path)

                    # change the xml of the snapshot
                    node = xml.get_node("snapshot/file[@name='%s']" % file_name)
                    Xml.set_attribute(node, "name", new_file_name)
 
                # Update entire snapshot XML
                snapshot.set_value( "snapshot", xml.to_string() )
 
                # Update context if it contains the filename
                parts = context.split("/")
                if len(parts) == 2:
                    new_subcontext, new_ext = os.path.splitext(new_value)
                    context = "%s/%s" % (parts[0], new_subcontext)
                    snapshot.set_value("context", context)

                snapshot.commit()

            snapshots[-1].update_versionless("latest")

            # Update original parent name if in single asset mode
            single_asset_mode = my.kwargs.get("single_asset_mode")
            if single_asset_mode in [True, "true", "True"]:
                # If sobject has an extension in it's name, then 
                # make sure this extension is preserved.
                original_name = sobject.get_value("name", no_exception=True)
                base, ext = os.path.splitext(original_name)
                if ext == old_ext:
                    new_name = "%s%s" % (new_base, ext) 
                else:
                    new_name = new_base
                sobject.set_value("name", new_name)
                
                # TODO: remove this commit statement
                sobject.commit()
 
            # Update any associated parents keywords
            for parent in parents.values():
                my.set_keywords(parent)
                parent.commit()


    def set_keywords(my, parent):

        if not parent.column_exists("keywords_data"):
            return


        keywords_data = parent.get_json_value("keywords_data", {})
        name = parent.get_value("name")
        relative_dir = parent.get_value("relative_dir")
        if relative_dir and name:
            path = "%s/%s" % (relative_dir, name)
        else:
            path = name

        keywords_data['path'] = Common.extract_keywords_from_path(path)

        parent.set_json_value("keywords_data", keywords_data)

        keywords = set()
        for values in keywords_data.values():
            keywords.update(values)
        keywords_list = list(keywords)
        keywords_list.sort()
        parent.set_value("keywords", " ".join(keywords_list))






class RepoBrowserCbk(Command):

    def execute(my):
        
        '''
        Given input snapshots, assets or directory, move to relative_dir.

        relative_dir - destination directory 

        With this command, you can move different assortment of assets.

        snapshot_code - move a single snapshot and sister snapshots sharing 
            its context.
        search_key - move a single asset
        search_keys - move many assets
        from_relative_dir - move an entire directory and all assets within it

        '''

        relative_dir = my.kwargs.get("relative_dir")
        
        snapshot_code = my.kwargs.get("snapshot_code")
        search_key = my.kwargs.get("search_key")
        search_keys = my.kwargs.get("search_keys")
        from_relative_dir = my.kwargs.get("from_relative_dir")

        # FIXME:
        # Possible issue... moving an entire directory structure assumes
        # that all snapshots are in relative directory or parent.
        # but snapshot_code mode only moves sister snapshots in same context.
        if snapshot_code:
            snapshot = Search.get_by_code("sthpw/snapshot", snapshot_code)
            parent = snapshot.get_parent()
            my.move_parent(parent, relative_dir, snapshot)
            return 
        elif search_key:
            parent = Search.get_by_search_key(search_key)
            parents = [parent]
        elif search_keys != None:
            parents = Search.get_by_search_keys(search_keys)
        else:
            # Move an entire directory
            # NOTE: this may be a bit too much brute force.  It may take files
            # that are not in the file table (but these shouldn't be there
            # in the first place!)
            base_dir = Environment.get_asset_dir()
           
            # Build new paths and check that new path is a directory
            abs_relative_dir = os.path.join(base_dir, relative_dir)
            abs_from_dir = os.path.join(base_dir, from_relative_dir)
            if not os.path.isdir(abs_relative_dir):
                raise Exception("Destination [%s] is not a directory" % relative_dir)
            
            # Check for naming conflict
            from_basename = os.path.basename(from_relative_dir)
            new_path = os.path.join(base_dir, relative_dir, from_basename)
            if (os.path.exists(new_path)):
                raise Exception("Directory [%s] already exists" % new_path)

            # find all the files with the relative dir
            file_search = Search("sthpw/file")
            file_search.add_filter("relative_dir", "%s%%" % from_relative_dir, op='like')
            files = file_search.get_sobjects()

            # Update each of the file relative_dir and build list of parents
            parent_keys = set()
            relative_dirs = {}           
            for file in files:
                # Build the new relative dir
                basename = os.path.basename(from_relative_dir)

                file_relative_dir = file.get_value("relative_dir")
                sub_relative_dir = os.path.relpath(from_relative_dir, file_relative_dir)
                new_relative_dir = os.path.normpath(os.path.join(relative_dir, basename, sub_relative_dir))

                file.set_value("relative_dir", new_relative_dir)
                file.commit()

                # find the parent and store in dictionary for update later
                parent_search_code = file.get_value("search_code")
                parent_search_type = file.get_value("search_type")
               
                parent_key = "%s&code=%s" % (parent_search_type, parent_search_code)
                parent_keys.add(parent_key)
                relative_dirs[parent_key] = new_relative_dir
 
            # Move all of the files 
            try:
                FileUndo.move(abs_from_dir, abs_relative_dir)
            except Exception as e:
                raise e
            
            # set the relative dirs of the parents
            parents = Search.get_by_search_keys(list(parent_keys))
            for parent in parents:
                if parent.column_exists("relative_dir"):
                    new_relative_dir = relative_dirs.get(parent.get_search_key())
                    parent.set_value("relative_dir", new_relative_dir)
                    my.set_keywords(parent)
                    parent.commit()

            return

        try:
            for parent in parents:
                my.move_parent(parent, relative_dir)
        except Exception as e:
            raise e
        

        """
        search_keys = [x.get_search_key() for x in all_files]

        # move the files to what the naming now says.
        # NOTE: this may not be correct.  A possible operation is to
        # move the file away from the naming conventions say.  In this
        # case, the file will be moved right back to where the naming
        # conventions says to move it.
        from tactic.command import NamingMigratorCmd
        cmd = NamingMigratorCmd( mode="file", search_keys=search_keys)
        cmd.execute()
        """



    def move_parent(my, parent, relative_dir, snapshot=None):
        '''Moves an asset and all related snapshots'''

        base_dir = Environment.get_asset_dir()

        search = Search("sthpw/snapshot")
        search.add_parent_filter(parent)
        
        if snapshot:
            version = snapshot.get_value("version")
            context = snapshot.get_value("context")
            search.add_filter("context", context)
        else:
            search.add_parent_filter(parent)
        
        search.add_order_by("version")
        snapshots = search.get_sobjects()

        all_files = []
        for snapshot in snapshots:
            # move all of the files from this snapshot
            files = snapshot.get_all_file_objects()
            for file in files:

                # get the old relative_dir
                file_relative_dir = file.get_value("relative_dir")
                file_name = file.get_value("file_name")


                file.set_value("relative_dir", relative_dir)
                file.commit()


                old_path = "%s/%s/%s" % (base_dir, file_relative_dir, file_name)
                new_path = "%s/%s/%s" % (base_dir, relative_dir, file_name)
                if not os.path.exists(old_path):
                    continue

                FileUndo.move(old_path, new_path)

            all_files.extend(files)


        # Some assumed behavior for this mode:
        # 1) all snapshots in this context exist in the same folder
        #    and should remain so
        # 2) all sobjects have a column called {relative_dir}
        # This should all fail cleanly if these assumptions are not the
        # case unless the sobject has a column called "relative_dir"
        # used for some other purpose
        if parent.column_exists("relative_dir"):
            parent.set_value("relative_dir", relative_dir)
            my.set_keywords(parent)
        parent.commit()

        # find highest version
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

    def set_keywords(my, parent):

        if not parent.column_exists("keywords_data"):
            return

        keywords_data = parent.get_json_value("keywords_data", {})
        name = parent.get_value("name")
        relative_dir = parent.get_value("relative_dir")
        if relative_dir and name:
            path = "%s/%s" % (relative_dir, name)
        else:
            path = name
        
        keywords_data['path'] = Common.extract_keywords_from_path(path)
        parent.set_json_value("keywords_data", keywords_data)

        keywords = set()
        for values in keywords_data.values():
            keywords.update(values)
        keywords_list = list(keywords)
        keywords_list.sort()
        parent.set_value("keywords", " ".join(keywords_list))



class RepoBrowserContentWdg(BaseRefreshWdg):

    def get_display(my):

        '''
        This class is displayed on click action of a single directory
        item (ie. "file", "snapshot", "asset")
        It checks if file item clicked has a parent before displaying
        detail.

        search_key - 

        search_type - parent search type
        single_asset_mode -
        
        dirname - 
        basename -

        '''
        
        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_browser_detail_top")
 
        inner = DivWdg()
        top.add(inner)

        search_key = my.kwargs.get("search_key")
        search_type = my.kwargs.get("search_type")
        search_type = SearchType.build_search_type(search_type)

        if search_key:
            sobject = Search.get_by_search_key(search_key)
            search_type = sobject.get_search_type()
            snapshot = Snapshot.get_latest_by_sobject(sobject)
            if not snapshot:
                raise Exception("No snapshot found")

            path = snapshot.get_lib_path_by_type()
            dirname = os.path.dirname(path)
            basename = os.path.basename(path)

        else:
            #project_code = Project.get_project_code()
            #search_type = "%s?project=%s" % (search_type, project_code)
            #search_type = Project.get_full_search_type(search_type, project_code=project_code)

            dirname = my.kwargs.get("dirname")
            basename = my.kwargs.get("basename")
            path = "%s/%s" % (dirname, basename)
            
        asset_dir = Environment.get_asset_dir()
        '''FIXME
        if not dirname.startswith(asset_dir):
            inner.add("Error: path [%s] does not belong in the asset directory [%s]" % (path, asset_dir))
            return top
        '''

        reldir = dirname.replace(asset_dir, "")
        reldir = reldir.strip("/")
        
        search = Search("sthpw/file")
        if search_type:
            search.add_filter("search_type", search_type)
        search.add_filter("relative_dir", reldir)
        search.add_filter("file_name", basename)
        
        files = search.get_sobjects()
      
        # Print statements are good for debugging dangling files and snapshots.
        good_file = None
        for file in files:
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
        inner.add(path_div)
        file_path = os.path.join(reldir, basename)
        path_div.add("<b>Path:</b> %s" % file_path)
        path_div.add_color("color", "color")
        path_div.add_color("background", "background")
        path_div.add_style("padding: 15px")

        if good_file:
            inner.add( my.get_content_wdg(good_file, snapshot, parent) )
        else:
            no_file_div = DivWdg()
            no_file_div.add_style("padding", "15px")
            icon = IconWdg("WARNING", IconWdg.WARNING)
            no_file_div.add(icon)
            no_file_div.add("<b>Invalid file</b>")
            no_file_div.add("<br/>"*2)
            inner.add(no_file_div)            
 
        is_refresh = my.kwargs.get("is_refresh")
        if is_refresh:
            return inner
        else:
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

        single_asset = my.kwargs.get("single_asset_mode")
        if single_asset in [True, "true", "True"]:
            search_key = parent.get_search_key()
        else:
            search_key = snapshot.get_search_key()

        config.append('''
        <element name='sobject_detail' title='Detail'>
            <display class='tactic.ui.tools.SObjectDetailWdg'>
                <search_key>%s</search_key>
            </display>
        </element>
        ''' % search_key
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

        '''Given a directory path and search type, it will displays snapshots that
        have files in that directory related to that search type. 
        If single asset mode is specified, it will display sobjects of the single asset sType.
        
        Given snapshot codes, it will display related single assets or filter those snapshots based
        on parent search type.'''
        
        top = my.top
            

        # The determination of search types important for IngestUploadWdg and ViewPanelWdg.
        single_asset = my.kwargs.get("single_asset_mode")
        if single_asset in ["True", "true", True]:
            parent_type = my.kwargs.get("search_type")
            search_type = parent_type
        else:
            parent_type = my.kwargs.get("search_type")
            search_type = "sthpw/snapshot"

        parent_type = SearchType.build_search_type(parent_type)
        search_type = SearchType.build_search_type(search_type)

        # Input data - snapshots or a absolute directory path
        snapshot_codes = my.kwargs.get("snapshot_codes")
        
        dirname = my.kwargs.get("dirname")
        asset_dir = Environment.get_asset_dir()
        if not dirname.startswith(asset_dir):
            top.add("Error: path [%s] does not belong in the asset directory [%s]" % (path, asset_dir))
            return top
        reldir = os.path.normpath(os.path.relpath(dirname, asset_dir))
        if reldir == ".":
            reldir = ""
    
        if snapshot_codes:
            search = Search("sthpw/snapshot")
            search.add_filters("code", snapshot_codes)

            search2 = Search(search_type)
            search2.add_relationship_search_filter(search)
            sobjects = search2.get_sobjects()
        elif single_asset:
            search = Search(search_type)
            search.add_filter("relative_dir", "%s%%" % reldir, op='like')
        else:
            # Search for all files that are in this relative_dir
            file_search = Search("sthpw/file")
            file_search.add_filter("relative_dir", "%s%%" % reldir, op='like')
            file_search.add_filter("search_type", parent_type)
            # Search for the snapshots related to these files and filter 
            # on parent type.
            search = Search(search_type)
            search.add_relationship_search_filter(file_search)

            '''
            FIXME:
            
            key = "repo_browser:%s" % search_type
            parent_search_str = WidgetSettings.get_value_by_key(key)
            if parent_search_str:
                parent_search = Search(search_type)
                parent_search.select.loads(parent_search_str)
                parent_search.add_column("code")
                search2.add_search_filter("code", parent_search)

            sobjects = search2.get_sobjects()
           '''

        path = my.kwargs.get("dirname")
        asset_dir = Environment.get_asset_dir()
        reldir = path.replace(asset_dir, "").strip("/")


        path_div = DivWdg()
        top.add(path_div)
        path_div.add("<b>Path:</b> %s" % reldir)
        path_div.add_color("color", "color")
        path_div.add_color("background", "background")
        path_div.add_style("padding: 15px")

        # Prefer tile layout
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



        shelf_wdg = DivWdg()
        top.add(shelf_wdg)

        button = ActionButtonWdg(title="Ingest")
        shelf_wdg.add(button)
        shelf_wdg.add_style("margin: 0px 20px")
        button.add_behavior( {
            'type': 'click_up',
            'path': path,
            'search_type': parent_type,
            'cbjs_action': '''
            var class_name = 'tactic.ui.tools.IngestUploadWdg';
            var kwargs = {
                search_type: bvr.search_type,
                base_dir: bvr.path,
            }
            spt.panel.load_popup("Ingest Files", class_name, kwargs);
            '''
        } )


        from tactic.ui.panel import ViewPanelWdg
        layout = ViewPanelWdg(
            search_type=search_type,
            search=search,
            view="table",
            element_names=element_names,
            show_shelf=False,
            show_search_limit=False,
            layout=layout_mode,
            scale='100',
            show_scale=True,
            width='100%',
        )



        top.add(layout)

        return top



