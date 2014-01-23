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

from pyasm.common import Environment

from pyasm.web import DivWdg, WebContainer, Table
from pyasm.biz import Snapshot, Project
from pyasm.search import Search, SearchType, SearchKey, FileUndo
from pyasm.widget import IconWdg, CheckboxWdg
from pyasm.command import Command

from tactic.ui.panel import FastTableLayoutWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ResizableTableWdg
from tactic.ui.widget import DirListWdg, IconButtonWdg, ButtonNewWdg, ButtonRowWdg
from tactic.ui.container import Menu, MenuItem, SmartMenu, DialogWdg

import os, shutil


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
        table.add_style("margin: -1px -1px -1px -1px")
        table.add_style("width: 100%")

        base_dir = Environment.get_asset_dir()
        project_code = Project.get_project_code()
        project_dir = "%s/%s" % (base_dir, project_code)

        table.add_row()

        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add_style("width: 1px")
        left.add_border()

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
        )
        content_div.add(dir_list)



        content = table.add_cell()
        content.add_style("vertical-align: top")
        content.add_border()

        outer_div = DivWdg()
        content.add(outer_div)
        outer_div.add_style("margin: -2px")
        outer_div.add_class("spt_repo_browser_content")

        content_div = DivWdg()
        content_div.add_style("min-width: 400px")
        outer_div.add(content_div)



        table.add_row()
        bottom = table.add_cell()
        bottom.add_attr("colspan", "3")
        info_div = DivWdg()
        bottom.add(info_div)
        bottom.add_border()

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


        return div




class RepoBrowserDirListWdg(DirListWdg):

    def init(my):
        my.file_codes = {}
        my.snapshot_codes = {}
        my.search_types_dict = {}
        my.search_codes = {}


        #dynamic = True
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



    def get_relative_paths(my, base_dir):

        # options to get files
        # show latest version only
        # show files
        # show all files types
        # show totals?
        my.show_files = True
        show_latest_only = True
        show_main_only = True
        show_empty_folders = True

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
                search_types = [SearchType.build_search_type(x) for x in search_types]
                parent_ids = []


            elif search_key:
                sobject = Search.get_by_search_key(search_key)
                search_types = [sobject.get_search_type()]
                parent_ids = [x.get_id() for x in sobjects]

            elif search_type:
                search_types = [SearchType.build_search_type(x) for x in search_types]

                my.sobjects = []
                parent_ids = []

            else:
                search_type_objs = Project.get().get_search_types(include_sthpw=False,include_config=False)
                search_types = [x.get_base_key() for x in search_type_objs]

                search_types = [SearchType.build_search_type(x) for x in search_types]
                my.sobjects = []
                parent_ids = []


        else:
            search_types = [sobjects[0].get_search_type()]
            parent_ids = [x.get_id() for x in sobjects]
            my.sobjects = sobjects



        paths = []
        my.file_codes = {}
        my.snapshot_codes = {}
        my.search_types_dict = {}
        my.search_codes = {}

        # Not this shold be used sparingly because it can find lots of
        # sobjects
        if my.show_files:

            search = Search("sthpw/file")
            if search_types:
                search.add_filters("search_type", search_types)

            if relative_dir:
                search.add_op("begin")
                search.add_filter("relative_dir", "%s" % relative_dir)
                if not my.dynamic:
                    search.add_filter("relative_dir", "%s/%%" % relative_dir, op='like')
                search.add_op("or")


            if parent_ids:
                search.add_filters("search_id", parent_ids)
            if keywords:
                search.add_text_search_filter("metadata_search", keywords)

            if show_latest_only:
                search.add_join("sthpw/snapshot")
                search.add_op("begin")
                search.add_filter("is_latest", True, table="snapshot")
                #search.add_filter("version", -1, table="snapshot")
                search.add_filter("file_name", "")
                search.add_filter("file_name", "NULL", quoted=False, op="is")
                search.add_op("or")

            if show_main_only:
                search.add_filter("type", "main")



            if my.sobjects:
                search.add_sobjects_filter(my.sobjects)

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


        project_code = Project.get_project_code()


        # associate all of the root folders to search types
        """
        for search_type in search_types:
            search_type_obj = SearchType.get(search_type)
            root_dir = search_type_obj.get_value("root_dir", no_exception=True)
            if not root_dir:
                base_type = search_type_obj.get_base_key()
                parts = base_type.split("/")
                root_dir = parts[1]

            dirname = "%s/%s/%s/" % (asset_base_dir, project_code, root_dir)
            if os.path.exists(dirname):
                my.search_types_dict[dirname] = search_type
        """


        num_sobjects = {}

  
        # show all folders, except the base folder of the project
        project_code = Project.get_project_code()
        project_base_dir = "%s/%s" % (asset_base_dir, project_code)
        if show_empty_folders and os.path.isdir(base_dir) and base_dir != project_base_dir:
            dirnames = os.listdir(base_dir)
            for dirname in dirnames:
                full = "%s/%s/" % (base_dir, dirname)
                if not os.path.isdir(full):
                    continue

                paths.append(full)



        # get all the directories
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



            # handle the dynamic case
            if my.dynamic and base_dir.startswith(start_dir):

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
            // get the new relative_dir
            var relative_dir = drop_on_el.getAttribute("spt_relative_dir");


            if ( drop_on_el.hasClass("spt_open") == true) {
                bvr.src_el.inject(drop_on_el, 'after');
                var padding = drop_on_el.getStyle("padding-left");
                padding = parseInt(padding.replace("px", ""));
                padding += 25;
                bvr.src_el.setStyle("padding-left", padding);
            }
            else {
                spt.behavior.destroy_element(bvr.src_el);
            }


            var cmd = 'tactic.ui.tools.RepoBrowserCbk';
            var kwargs = {
                snapshot_code: snapshot_code,
                relative_dir: relative_dir
            }
            server.execute_cmd(cmd, kwargs); 

        }

        spt.repo_browser.selected = [];
        spt.repo_browser.select = function(file_item) {
            spt.repo_browser.selected.push(file_item);
            //file_item.setStyle("background", "#F00");
        }
        spt.repo_browser.clear_selected = function() {
            var selected = spt.repo_browser.selected();
            for (var i = 0; i < selected.length; i++) {
                selected[i].setStyle("background", "");
            }
            spt.repo_browser.selected = [];
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
        #menus = [menu.get_data()]
        menus_in = {
            'FREEFORM_DIR_ITEM_CTX': freeform_menu,
            'STRICT_DIR_ITEM_CTX': strict_menu,
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


        if mode == "freeform":

            menu_item = MenuItem(type='separator')
            menu.add(menu_item)


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
                if (!confirm("Delete folder ["+relative_dir+"]?")) {
                    return;
                }

                var class_name = 'tactic.ui.tools.RepoBrowserActionCmd';
                var kwargs = {
                    search_type: bvr.search_type,
                    action: 'delete_folder',
                    relative_dir: relative_dir
                }
                var server = TacticServerStub.get();
                server.execute_cmd(class_name, kwargs);

                activator.destroy();


                '''
            } )



        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        """
        menu_item = MenuItem(type='action', label='Check-in Files')
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



        return menu






    def add_file_behaviors(my, item_div, dirname, basename):
        item_div.add_class("spt_drag_file_item")

        path = "%s/%s" % (dirname, basename)
        relative_dir = path.replace(my.base_dir, "")
        relative_dir = relative_dir.strip("/")

        #search_types = my.kwargs.get("search_types")
        search_types = my.search_types_dict


        #file_codes = my.kwargs.get("file_codes")
        file_codes = my.file_codes

        #snapshot_codes = my.kwargs.get("snapshot_codes")
        snapshot_codes = my.snapshot_codes

        search_type = search_types.get(path)
        if not search_type:
            parts = relative_dir.split("/")
            for i in range(len(parts)+1, 0, -1):
                tmp_rel_dir = "/".join(parts[:i])
                tmp_dir = "%s/%s" % (my.base_dir, tmp_rel_dir)
                search_type = search_types.get("%s/" % tmp_dir)

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
        'type': 'click_up',
        'dirname': dirname,
        'basename': basename,
        'search_type': search_type,
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_repo_browser_top");
        var content = top.getElement(".spt_repo_browser_content");
        spt.table.last_table = null;
        var class_name = "tactic.ui.tools.repo_browser_wdg.RepoBrowserContentWdg";
        spt.app_busy.show("Loading information");
        var kwargs = {
          search_type: bvr.search_type,
          dirname: bvr.dirname,
          basename: bvr.basename
        };
        spt.panel.load(content, class_name, kwargs);
        spt.app_busy.hide();

        spt.repo_browser.select(bvr.src_el);
        '''
        } )




    def add_dir_behaviors(my, item_div, dirname, basename):

        asset_base_dir = Environment.get_asset_dir()

        path = "%s/%s" % (dirname, basename)
        relative_dir = path.replace(asset_base_dir, "")
        relative_dir = relative_dir.strip("/")

        #search_types = my.kwargs.get("search_types")
        search_types = my.search_types_dict

        #search_codes = my.kwargs.get("search_codes")
        search_codes = my.search_codes



        search_type = search_types.get("%s/" % path)



        if not search_type:
            parts = relative_dir.split("/")
            for i in range(len(parts)+1, 0, -1):
                tmp_rel_dir = "/".join(parts[:i])
                tmp_dir = "%s/%s" % (my.base_dir, tmp_rel_dir)
                search_type = search_types.get("%s/" % tmp_dir)

        if not search_type:
            return


        # FIXME: TEST TEST
        if search_type.startswith("test2/sequence") or search_type.startswith("test2/shot"):
            SmartMenu.assign_as_local_activator( item_div, 'STRICT_DIR_ITEM_CTX' )
        else:
            SmartMenu.assign_as_local_activator( item_div, 'FREEFORM_DIR_ITEM_CTX' )

        item_div.add_attr("spt_search_type", search_type)


        search_code_list = search_codes.get("%s/" % path)
        if not search_code_list:
            search_code_list = []
        search_codes_str = "|".join(list(search_code_list))
        item_div.add_attr("spt_search_codes", search_codes_str)


        item_div.add_attr("spt_relative_dir", relative_dir)
        item_div.add_attr("spt_dirname", "%s/%s" % (dirname, basename))

        item_div.add_behavior( {
        'type': 'click_up',
        'dirname': "%s/%s" % (dirname, basename),
        'basename': '',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_repo_browser_top");
        var content = top.getElement(".spt_repo_browser_content");
        var class_name = "tactic.ui.tools.RepoBrowserDirContentWdg";

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
        var search_keys = dir_list_top.getAttribute("spt_search_keys");
        if (search_keys) {
            search_keys = search_keys.split("|");
        }
        else {
            search_keys = [];
        }

        var search_codes = bvr.src_el.getAttribute("spt_search_codes");
        search_codes = search_codes.split("|");

        spt.app_busy.show("Loading ...");
        var kwargs = {
            search_type: search_type,
            view: 'table',
            dirname: bvr.dirname,
            basename: bvr.basename,
            search_keys: search_keys
        };
        spt.table.last_table = null;
        spt.panel.load(content, class_name, kwargs);
        spt.app_busy.hide();

        '''
        } )




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

            print "old_dir: ", old_dir
            print "new_dir: ", new_dir
            for file in files:
                file.set_value("relative_dir", new_relative_dir)
                file.commit()
            FileUndo.move(old_dir, new_dir)


            







class RepoBrowserCbk(Command):

    def execute(my):
        relative_dir = my.kwargs.get("relative_dir")
        snapshot_code = my.kwargs.get("snapshot_code")

        snapshot = Search.get_by_code("sthpw/snapshot", snapshot_code)
        version  = snapshot.get_value("version")

        parent = snapshot.get_parent()

        #if version == 1:
        if False:
            snapshots = [snapshot]
        else:
            context = snapshot.get_value("context")

            search = Search("sthpw/snapshot")
            search.add_parent_filter(parent)
            search.add_filter("context", context)
            snapshots = search.get_sobjects()

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
            # 1) all snapshots exist in the same folder
            # 2) all sobjects have a column called {relative_dir}
            # This should all fail cleanly if these assumptions are not the
            # case unless the sobject has a column called "relative_dir"
            # used for some other purpose
            if parent.column_exists("relative_dir"):
                parent.set_value("relative_dir", relative_dir)
                parent.commit()

        search_keys = [x.get_search_key() for x in all_files]

        from tactic.command import NamingMigratorCmd
        cmd = NamingMigratorCmd( mode="file", search_keys=search_keys)
        cmd.execute()






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
        tab = TabWdg(config_xml=config, selected=selected, show_remove=False, show_add=False, tab_offset=10)
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
        #path = "%s/%s" % (dirname, basename)
        path = dirname

        asset_dir = Environment.get_asset_dir()
        if not dirname.startswith(asset_dir):
            top.add("Error: path [%s] does not belong in the asset directory [%s]" % (path, asset_dir))
            return top

        reldir = path.replace(asset_dir, "")
        reldir = reldir.strip("/")


        search = Search("sthpw/file")
        search.add_filter("relative_dir", "%s%%" % reldir, op='like')
        search.add_filter("search_type", search_type)

        search2 = Search(search_type)
        search2.add_relationship_search_filter(search)
        sobjects = search2.get_sobjects()




        top = my.top

        path = my.kwargs.get("dirname")
        path_div = DivWdg()
        top.add(path_div)
        path_div.add("<b>Path:</b> %s" % path)
        path_div.add_color("color", "color")
        path_div.add_color("background", "background", -5)
        path_div.add_style("padding: 15px")
        path_div.add_style("margin: -1 -1 0 -1")
        path_div.add_border()



        search_codes = [x.get_value("code") for x in sobjects]
        search_codes_str = "|".join(search_codes)
        expression = "@SEARCH(%s['code','in','%s'])" % (search_type,search_codes_str)

        #search_keys = my.kwargs.get("search_keys")
        search_keys = []



        #layout_mode = 'default'

        search_type_obj = SearchType.get(search_type)
        layout_mode = search_type_obj.get_value("default_layout", no_exception=True)
        if layout_mode == '':
            layout_mode = 'default'

        if layout_mode == 'default' or layout_mode == 'browser':
            # if browser default is browser, then like we don't want to see
            # a browser again.
            layout_mode = 'tile'


        element_names = None
        if layout_mode == "checkin":
            element_names = ['preview','code','name','general_checkin','file_list', 'history','description','notes']



        from tactic.ui.panel import ViewPanelWdg
        layout = ViewPanelWdg(
            search_type=search_type,
            expression=expression,
            search_keys=search_keys,
            view="table",
            element_names=element_names,
            show_shelf=True,
            layout=layout_mode,
            scale='75',
            width='100%',
        )
        #layout.set_sobjects(sobjects)


        top.add_border(size="1px 1px 0px 1px")
        top.add(layout)

        return top



