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

__all__ = ['RepoBrowserWdg', 'RepoBrowserDirListWdg','RepoBrowserCbk', 'RepoBrowserDirContentWdg', 'RepoBrowserActionCmd']

from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Environment

from pyasm.web import DivWdg, WebContainer, Table
from pyasm.biz import Snapshot, Project
from pyasm.search import Search, SearchType, SearchKey
from pyasm.widget import IconWdg
from pyasm.command import Command

from tactic.ui.panel import FastTableLayoutWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ResizableTableWdg
from tactic.ui.widget import DirListWdg
from tactic.ui.container import Menu, MenuItem, SmartMenu

import os


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


        paths = []
        my.file_codes = {}
        my.snapshot_codes = {}
        base_dir = Environment.get_asset_dir()

        search_codes = {}

        # Not this shold be used sparingly because it can find lots of
        # sobjects
        if my.mode != "folder":

            search = Search("sthpw/file")
            search.add_filter("search_type", search_type)
            if parent_ids:
                search.add_filters("search_id", parent_ids)
            if keywords:
                search.add_text_search_filter("metadata_search", keywords)

            if my.mode == 'main':
                search.add_filter("type", "main")

            file_objects = search.get_sobjects()



            for file_object in file_objects:
                relative_dir = file_object.get_value("relative_dir")
                file_name = file_object.get_value("file_name")

                repo_type = file_object.get_value("repo_type")
                if repo_type == 'perforce':
                    print "PERFORCE: ", file_object.get_code(), file_name
                    #continue

                path = "%s/%s/%s" % (base_dir, relative_dir, file_name)
                paths.append(path)

                my.file_codes[path] = file_object.get("code")
                my.snapshot_codes[path] = file_object.get("snapshot_code")

                # store search codes per directory
                dirname = "%s/%s/" % (base_dir, relative_dir)
                search_code = file_object.get("search_code")
                search_codes_list = search_codes.get(dirname)
                if search_codes_list == None:
                    search_codes[dirname] = set([search_code])
                else:
                    search_codes[dirname].add(search_code)





        # get all the directories
        project_code = Project.get_project_code()
        search_type_obj = SearchType.get(search_type)
        parts = search_type_obj.get_base_key().split("/")
        if len(parts) == 2:
            table = parts[1]
        else:
            table = parts[0]
        start_dir = "%s/%s/%s" % (base_dir, project_code, table)
        paths.append("%s/" % start_dir)

        num_sobjects = {}
        for root, dirnames, filenames in os.walk(start_dir):

            for dirname in dirnames:
                # need to put a / and the end to signify a directory
                full = "%s/%s/" % (root, dirname)
                paths.append(full)

                search_codes_list = search_codes.get(full)
                if not search_codes_list:
                    num_sobjects[full] = 0
                else:
                    num_sobjects[full] = len(search_codes_list)



        print "---"               

        for name, value in num_sobjects.items():
            print value, name

        return paths



    def get_display(my):

        search_type = my.kwargs.get("search_type")
        keywords = my.kwargs.get("keywords")

        top = my.top
        top.add_color("background", "background")
        top.add_class("spt_repo_browser_top")

        my.mode = 'main'
        #my.mode = 'all'
        #my.mode = 'folder'

        """
        title_wdg = DivWdg()
        top.add(title_wdg)
        title_wdg.add_border()
        title_wdg.add_style("padding: 10px")
        title_wdg.add_gradient("background", "background", -10)
        title_wdg.add("Repository Browser")
        title_wdg.add_style("font-size: 14px")
        title_wdg.add_style("font-weight: bold")
        """

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
        left_inner = DivWdg()
        left.add(left_inner)
        left_inner.add_style("padding: 10px")
        left_inner.add_style("width: 350px")
        #left_inner.add_style("max-height: 600px")
        left_inner.add_style("min-height: 500px")
        left_inner.add_style("min-height: 500px")
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
        text.add_style("width: 250px")
        if keywords:
            text.set_value(keywords)
        search_div.add(text)
        search_div.add("<hr/")

        paths = my.get_files()
        file_codes = my.file_codes

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
        dir_list = RepoBrowserDirListWdg(base_dir=project_dir, location="server", show_base_dir=True,paths=paths, open_depth=1, search_type=search_type, file_codes=file_codes, snapshot_codes=my.snapshot_codes)
        content_div.add(dir_list)



        content = table.add_cell()
        content.add_style("vertical-align: top")
        content.add_border()
        #content.add_style("padding: 10px")
        #content.add_style("width: 600px")

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


class RepoBrowserDirListWdg(DirListWdg):

    def add_top_behaviors(my, top):

        top.add_behavior( {
            'type': 'load',
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
                if (diff_y < 1 && diff_y > -1) {
                    return;
                }

                bvr.src_el.setStyle("border", "solid 1px black");
                bvr.src_el.setStyle("box-shadow", "0px 0px 5px");
                bvr.src_el.setStyle("position", "absolute");
                bvr.src_el.position({x:mouse_411.curr_x+5, y:mouse_411.curr_y+5});
            }
            spt.repo_browser.drag_file_action = function(evt, bvr, mouse_411) {
 
                //bvr.src_el.position(spt.repo_browser.start_pos);


                bvr.src_el.setStyle("border", "");
                bvr.src_el.setStyle("box-shadow", "");
                bvr.src_el.setStyle("position", "relative");
                bvr.src_el.position( spt.repo_browser.start_pos);

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


                bvr.src_el.inject(drop_on_el, 'after');
                var padding = drop_on_el.getStyle("padding-left");
                padding = parseInt(padding.replace("px", ""));
                padding += 25;
                bvr.src_el.setStyle("padding-left", padding);


                var server = TacticServerStub.get(); 

                var snapshot_code = bvr.src_el.getAttribute("spt_snapshot_code");
                // get the new relative_dir
                var relative_dir = drop_on_el.getAttribute("spt_relative_dir");

                var cmd = 'tactic.ui.tools.RepoBrowserCbk';
                var kwargs = {
                    snapshot_code: snapshot_code,
                    relative_dir: relative_dir
                }
                server.execute_cmd(cmd, kwargs); 

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
        menu = my.get_dir_context_menu()
        menus = [menu.get_data()]
        menus_in = {
            'DIR_ITEM_CTX': menus,
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

        





    def get_dir_context_menu(my):

        search_type = my.kwargs.get("search_type")

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='New Folder')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'search_type': search_type,
            'cbjs_action': r'''
            var activator = spt.smenu.get_activator(bvr);
            var relative_dir = activator.getAttribute("spt_relative_dir");

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
            if (content.childNodes.length)
                div.inject(content.childNodes[0], "before");
            else
                div.inject(content);


            var padding = activator.getStyle("padding-left");
            padding = parseInt( padding.replace("px", "") ) + 11;
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


        menu_item = MenuItem(type='action', label='Rename Folder (TODO)')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var relative_dir = activator.getAttribute("spt_relative_dir");

            var input = $(document.createElement("input"));
            input.setAttribute("type", "text");

            var el = activator.getElement(".spt_dir_value");
            input.replaces(el);

            var parts = relative_dir.split("/");
            input.value = parts[parts.length-1];
            input.select();

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
            };


            var class_name = 'tactic.ui.tools.RepoBrowserActionCmd';
            var kwargs = {
                search_type: bvr.search_type,
                action: 'rename_folder',
                relative_dir: relative_dir
            }
            var server = TacticServerStub.get();
            server.execute_cmd(class_name, kwargs);

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

        menu_item = MenuItem(type='action', label='Check-in Files')
        menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'search_type': search_type,
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var relative_dir = activator.getAttribute("spt_relative_dir");
            var class_name = 'tactic.ui.tools.IngestUploadWdg';
            var kwargs = {
                search_type: bvr.search_type,
                relative_dir: relative_dir
            };
            spt.panel.load_popup("Check-in", class_name, kwargs);
            '''
        } )



        return menu






    def add_file_behaviors(my, item_div, dirname, basename):
        search_type = my.kwargs.get("search_type")
        item_div.add_class("spt_drag_file_item")

        path = "%s/%s" % (dirname, basename)
        file_code = my.kwargs.get("file_codes").get(path)
        snapshot_code = my.kwargs.get("snapshot_codes").get(path)
        item_div.add_attr("spt_file_code", file_code)
        item_div.add_attr("spt_snapshot_code", snapshot_code)


        item_div.add_behavior( {
            'type': 'drag',
            "mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.repo_browser.drag_file'

        } )



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

        SmartMenu.assign_as_local_activator( item_div, 'DIR_ITEM_CTX' )

        path = "%s/%s" % (dirname, basename)
        relative_dir = path.replace(my.base_dir, "")
        relative_dir = relative_dir.strip("/")
        # my.base_dir contains the project, so it will be removed.  Add this
        # back
        project_code = Project.get_project_code()
        relative_dir = "%s/%s" % (project_code, relative_dir)
        item_div.add_attr("spt_relative_dir", relative_dir)

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
        spt.app_busy.show("Loading ...");
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
        #print "code: ", my.kwargs.get("file_codes").get(path)
        if not os.path.exists(path):
            return IconWdg.ERROR
        return IconWdg.DETAILS

    def get_dir_icon(my, dir, item):
        return IconWdg.LOAD



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
            print "full: ", full_dir

            if os.path.exists(full_dir):
                raise Exception("Directory [%s] already exists" % relative_dir)

            os.makedirs(full_dir)

        elif action == "delete_folder":

            relative_dir = my.kwargs.get("relative_dir")
            if not relative_dir:
                return

            full_dir = "%s/%s" % (base_dir, relative_dir)
            os.rmdir(full_dir)


        elif action == "rename_folder":

            relative_dir = my.kwargs.get("relative_dir")
            if not relative_dir:
                return

            print "OMG!!!"

            







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

        layout_mode = 'default'
        from tactic.ui.panel import ViewPanelWdg
        layout = ViewPanelWdg(
            search_type=search_type,
            expression=expression,
            #search_keys=search_keys,
            view="table",
            element_names=['preview','code','name','description','history','file_list'],
            show_shelf=True,
            layout=layout_mode,
            scale='50'
        )
        #layout.set_sobjects(sobjects)


        top.add_border(size="1px 1px 0px 1px")
        top.add(layout)

        return top



